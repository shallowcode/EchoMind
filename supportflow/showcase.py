"""Local sandbox workbench. All numbers and traces come from recorded execution."""
import asyncio
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import time

from fastapi import Depends, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, ConfigDict, Field


@lru_cache(maxsize=1)
def evaluation_report(root):
    directory = Path(root) / "artifacts/glm-full-20260909"
    report_path = directory / "report.json"
    if not report_path.exists():
        return {"available": False, "reason": "未找到评测归档"}
    report = json.loads(report_path.read_text(encoding="utf-8"))
    records = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((directory / "records").glob("public-*.json"))]
    if not records:
        return {"available": False, "reason": "缺少逐条评测记录"}
    historical = report["public"]["all"]
    labels = sorted(historical["per_class_f1"])
    confusion = Counter((r["expected"], r["predicted"]) for r in records)
    f1 = {}
    for label in labels:
        tp = confusion[label, label]
        fp = sum(n for (a, b), n in confusion.items() if b == label and a != label)
        fn = sum(n for (a, b), n in confusion.items() if a == label and b != label)
        f1[label] = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0
    accuracy = sum(r['expected'] == r['predicted'] for r in records) / len(records)
    macro = sum(f1.values()) / len(f1)
    source = json.loads((directory / "source/evaluation/datasets/trial-v3/public-manifest.json").read_text(encoding="utf-8"))
    mapping = [{"source": label, "target": next(r['expected'] for r in records if r['label'] == label),
                "count": sum(r['label'] == label for r in records)} for label in sorted({r['label'] for r in records})]
    return {"available": True, "model": report['model'], "date": "2026-09-09", "split": "development",
            "evaluated": len(records), "source_classes": len(mapping), "accuracy": accuracy, "macro_f1": macro,
            "report_verified": len(records) == historical['evaluated'] and abs(accuracy - historical['accuracy']) < 1e-9 and abs(macro - historical['macro_f1']) < 1e-9,
            "f1_labels": labels, "per_class_f1": f1,
            "confusion": [{"expected": a, "predicted": b, "n": n} for (a, b), n in sorted(confusion.items())],
            "mapping": mapping, "source": {k: source[k] for k in ('source', 'license', 'revision', 'source_sha256')},
            "artifact": "artifacts/glm-full-20260909/report.json", "artifact_sha256": hashlib.sha256(report_path.read_bytes()).hexdigest(),
            "notes": ["历史版本 · 英文公开合成训练语料 · 开发集", "意图分类评测，不代表退款或工单完成率", "宏 F1 沿用归档的 11 个目标标签；order_status 在本次样本中无真实支持，F1 计 0", "当前代码已更新，尚未重新运行此评测"],
            "records": [{k: r.get(k) for k in ('message', 'label', 'expected', 'predicted', 'source_row', 'http_status', 'latency_ms')} for r in records]}


class SkillEdit(BaseModel):
    model_config = ConfigDict(extra="forbid")
    content: str = Field(min_length=1, max_length=20000)
    version: str


def install_showcase(app, service, identity, require_local_demo, root):
    async def access(request: Request, p=Depends(identity)):
        require_local_demo(request, "merchant")
        p.require("staff")
        return p

    def skill_rows():
        return [{"id": hashlib.sha256(s.path.encode()).hexdigest()[:16], "name": s.name,
                 "agents": s.agents, "keywords": s.keywords, "enabled": s.enabled, "content": s.content,
                 "version": hashlib.sha256(Path(s.path).read_bytes()).hexdigest()} for s in service.skills.skills]

    @app.get('/lab', include_in_schema=False)
    async def home():
        return FileResponse(root / 'frontend/lab.html', headers={'Cache-Control': 'no-cache'})

    @app.get('/lab/evaluation')
    async def evaluation(p=Depends(access)):
        return await asyncio.to_thread(evaluation_report, str(root))

    @app.get('/lab/runtime')
    async def runtime(p=Depends(access)):
        with service.knowledge.store.tx() as c:
            docs = [dict(r) for r in c.execute('SELECT id,title,content,version FROM knowledge WHERE tenant=? ORDER BY title,id', (p.tenant,))]
            audit = [] if service.settings.business_url else [dict(r) for r in c.execute('SELECT * FROM audit WHERE tenant=? ORDER BY seq DESC LIMIT 60', (p.tenant,))]
        if service.settings.business_url:
            audit = service.store.audit_log(p)[:60]
        breakers = [{"tool": name, "failures": b.failures, "threshold": b.threshold,
                     "state": "half_open" if b.probe else "open" if b.opened and time.monotonic() - b.opened < b.recovery else "probe_ready" if b.opened else "closed",
                     "recovery_seconds": b.recovery} for (tenant, name), b in service.tools.breakers.items() if tenant == p.tenant]
        return {"skills": skill_rows(), "skill_errors": service.skills.errors, "knowledge": docs, "audit": audit,
                "breakers": breakers, "tools": service.tools.available('billing'),
                "capabilities": {k: sorted(v) for k, v in service.tools.capabilities.items()},
                "limits": {"tool_timeout_seconds": 10, "knowledge_timeout_seconds": 90, "max_tool_rounds": service.settings.max_tool_rounds,
                           "request_timeout_seconds": service.settings.request_timeout},
                "storage": service.settings.storage, "tenant": p.tenant,
                "transport": "聊天直接调用共享工具服务；MCP /mcp/ 暴露同一服务"}

    @app.post('/lab/skills/reload')
    async def reload(p=Depends(access)):
        service.skills.reload()
        return {"skills": skill_rows(), "errors": service.skills.errors}

    @app.patch('/lab/skills/{skill_id}')
    async def edit(skill_id: str, body: SkillEdit, p=Depends(access)):
        skill = next((s for s in service.skills.skills if hashlib.sha256(s.path.encode()).hexdigest()[:16] == skill_id), None)
        if not skill:
            raise HTTPException(404, 'Skill 不存在')
        path = Path(skill.path).resolve()
        if not path.is_relative_to(service.skills.root_dir) or path.suffix.lower() != '.md':
            raise HTTPException(409, '仅支持编辑现有 Markdown Skill')
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != body.version:
            raise HTTPException(409, 'Skill 已变更，请刷新后重试')
        if not body.content.strip():
            raise HTTPException(422, '内容不能为空')
        text = raw.decode('utf-8')
        prefix = ''
        if text.startswith('---'):
            lines = text.splitlines(keepends=True)
            for i in range(1, len(lines)):
                if lines[i].strip() == '---':
                    prefix = ''.join(lines[:i + 1]) + '\n'
                    break
        tmp = path.with_suffix('.pending')
        tmp.write_text(prefix + body.content.strip() + '\n', encoding='utf-8')
        tmp.replace(path)
        service.skills.reload()
        service.store.append_audit(p, 'skill.update', skill.name, {'before': body.version, 'after': hashlib.sha256(path.read_bytes()).hexdigest()})
        return {"skills": skill_rows(), "errors": service.skills.errors}
