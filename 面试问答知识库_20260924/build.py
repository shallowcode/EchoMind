from pathlib import Path
import ast
import hashlib
import html
import json
import re
import zipfile
from collections import Counter

OUT = Path(__file__).resolve().parent
ROOT = OUT.parent
SECTIONS = {
    'A': ('项目总览与版本', '项目介绍'),
    'B': ('复合任务编排', '复合任务编排'),
    'C': ('RAG与知识检索', '知识与记忆'),
    'D': ('记忆与Skills', '知识与记忆'),
    'E': ('业务工具与权限', '业务工具闭环'),
    'F': ('事务与一致性', '业务工具闭环'),
    'G': ('意图识别与公开评测', '数据与评测'),
    'H': ('端到端评测与统计口径', '全链路验证'),
    'I': ('性能可靠性与部署', '全链路验证'),
    'J': ('场景推演与个人表达', '综合追问'),
}

SPECS = {
 'entry': ('api/main.py', ''),
 'chat': ('supportflow/service.py', 'ChatService.chat'),
 'run': ('supportflow/service.py', 'ChatService._run'),
 'agent': ('supportflow/service.py', 'ToolAgent._call_llm'),
 'shared': ('supportflow/service.py', 'ToolAgent._execute_tool'),
 'versions': ('supportflow/service.py', 'ChatService.versions'),
 'plan': ('supportflow/planning.py', 'plan_tasks'),
 'task': ('supportflow/planning.py', 'Subtask'),
 'gaps': ('supportflow/planning.py', 'Subtask.gaps'),
 'scope': ('supportflow/planning.py', 'scope_message'),
 'render': ('supportflow/planning.py', 'render_tasks'),
 'retrieve': ('supportflow/knowledge.py', 'Knowledge.retrieve'),
 'knowledgeadd': ('supportflow/knowledge.py', 'Knowledge.add'),
 'knowinit': ('supportflow/knowledge.py', 'Knowledge.__init__'),
 'search': ('supportflow/knowledge.py', 'Knowledge.search'),
 'archive': ('supportflow/knowledge.py', 'Knowledge.archive'),
 'recall': ('supportflow/knowledge.py', 'Knowledge.recall'),
 'profileproj': ('supportflow/knowledge.py', 'Knowledge.project_profile'),
 'skillload': ('core/skill_loader.py', 'SkillManager.load'),
 'skillmatch': ('core/skill_loader.py', 'Skill.matches'),
 'skillprompt': ('core/skill_loader.py', 'SkillManager.prompt_for'),
 'tools': ('supportflow/tools.py', 'Tools.call'),
 'breaker': ('supportflow/tools.py', 'Breaker'),
 'mcp': ('supportflow/protocol.py', 'build_mcp'),
 'contracts': ('supportflow/contracts.py', 'AgentTurn'),
 'principal': ('supportflow/contracts.py', 'Principal'),
 'settings': ('supportflow/contracts.py', 'Settings'),
 'model': ('supportflow/model.py', 'Model.complete'),
 'pricing': ('supportflow/pricing.py', 'estimate_call'),
 'store': ('supportflow/store.py', 'Store'),
 'tx': ('supportflow/store.py', 'Store.tx'),
 'auth': ('supportflow/store.py', 'Store.authenticate'),
 'order': ('supportflow/store.py', 'Store.order'),
 'refundstore': ('supportflow/store.py', 'Store.refund_request'),
 'approve': ('supportflow/store.py', 'Store.approve_refund'),
 'settle': ('supportflow/store.py', 'Store.settle_refund'),
 'refundstatus': ('supportflow/store.py', 'Store.refund_status'),
 'ticketcreate': ('supportflow/store.py', 'Store.create_ticket'),
 'ticketupdate': ('supportflow/store.py', 'Store.update_ticket'),
 'lease': ('supportflow/store.py', 'Store.acquire_conversation'),
 'cached': ('supportflow/store.py', 'Store.cached_request'),
 'commit': ('supportflow/store.py', 'Store.commit_turn'),
 'refundresolve': ('supportflow/refunds.py', 'resolve_refund'),
 'refundvalidate': ('supportflow/refunds.py', 'validate_refund_call'),
 'payments': ('supportflow/payments.py', 'Payments'),
 'intent': ('core/intent_recognizer.py', 'IntentRecognizer.recognize'),
 'ivote': ('core/intent_recognizer.py', 'IntentRecognizer._vote'),
 'api': ('supportflow/api.py', 'create_app'),
 'verify': ('evaluation/full_chain.py', 'verify'),
 'fullrun': ('evaluation/full_chain.py', 'run_case'),
 'publicmap': ('evaluation/public_intents.py', ''),
 'compare': ('evaluation/compare_runs.py', ''),
 'fullscript': ('scripts/run_full_evaluation.py', ''),
 'audit': ('评测结果/GLM-1200复核/audit.json', ''),
 'auditread': ('评测结果/GLM-1200复核/README.md', ''),
 'publicreport': ('artifacts/glm-full-20260909/report.json', ''),
 'datacard': ('evaluation/datasets/trial-v3/README.md', ''),
 'guide': ('SUPPORTFLOW.md', ''),
 'compose': ('compose.supportflow.yml', ''),
 'plantest': ('tests/test_supportflow_planning.py', ''),
 'tooltest': ('tests/test_supportflow_tools.py', ''),
 'mcptest': ('tests/test_supportflow_mcp.py', ''),
 'paymenttest': ('tests/test_supportflow_payments.py', ''),
 'skilltest': ('tests/test_supportflow_skills.py', ''),
}

def symbols(text):
    found = {}
    def visit(node, prefix=''):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                name = prefix + child.name
                found[name] = (child.lineno, child.end_lineno)
                visit(child, name + '.')
            else:
                visit(child, prefix)
    visit(ast.parse(text))
    return found

sources = {}
for key, (path, symbol) in SPECS.items():
    file = ROOT / path
    raw = file.read_bytes()
    content = raw.decode('utf-8-sig')
    lines = content.splitlines()
    start, end = symbols(content)[symbol] if symbol else (1, len(lines))
    # Short excerpts aid navigation; full implementation remains at the cited file.
    stop = min(end, start + 19)
    sources[key] = dict(id=key, path=path, symbol=symbol, line=start, end_line=end,
                        sha256=hashlib.sha256(raw).hexdigest(),
                        snippet='\n'.join(f'{n}: {lines[n-1]}' for n in range(start, stop+1)),
                        absolute_path=file.as_posix())

cards = []
for file in sorted((OUT/'source').glob('*.txt')):
    for block in re.split(r'\n\s*\n', file.read_text(encoding='utf-8').strip()):
        rows = block.splitlines()
        assert len(rows) == 7, (file, rows[0], len(rows))
        ident, priority, evidence, tags, refs, related = rows[0].split('|')
        section, bullet = SECTIONS[ident[0]]
        cards.append(dict(id=ident, section=section, section_id=ident[0], bullet=bullet,
                          priority=priority, evidence=evidence, tags=tags.split(','),
                          sources=refs.split(','), related=related.split(','),
                          question=rows[1], answer=rows[2], detail=rows[3],
                          followup=rows[4], followup_answer=rows[5], boundary=rows[6]))

cards.sort(key=lambda c:c['id'])
ids = {c['id'] for c in cards}
assert len(cards) == len(ids) == 120
assert len({c['question'] for c in cards}) == len(cards)
for c in cards:
    assert set(c['sources']) <= sources.keys(), c['id']
    assert set(c['related']) <= ids, c['id']
    for field in ['question','answer','detail','followup','followup_answer','boundary']:
        assert c[field].strip(), (c['id'],field)

FILES = {k:f'{i:02d}_{v[0]}.md' for i,(k,v) in enumerate(SECTIONS.items(),1)}
TOP = ['A01','A02','A03','A05','A06','B01','B02','B04','B05','B07','B08',
       'C01','D01','D06','E01','E03','E06','E08','E10','E12','F01','F02',
       'G04','G06','H01','H06','H07','H10','H12','J07']
def cardlink(ident):
    return f"[{ident}]({FILES[ident[0]]}#{ident.lower()})"
def sourcelink(key):
    s = sources[key]
    label = s['path'] + ':' + str(s['line']) + (' · '+s['symbol'] if s['symbol'] else '')
    return f"[{label}](<{s['absolute_path']}:{s['line']}>)"

intro = '''# SupportFlow 面试问答知识库

依据：张天宇2.0.pdf 的“项目经历”部分、当前工作区代码、2026-09-09历史评测归档。整理时间：2026-09-24。

本库只展开 SupportFlow 项目，不把实习里的 GRPO、SFT、Verifier 数据混入项目答案。120道主问题，每题另有1道带答案的深入追问，共240个问答入口；10个主题。题目为基于简历和代码推演的面试题，不是真实面试记录。

## 怎么查、怎么练

- 首选打开同目录的 **知识库.html**：离线全文搜索、主题/简历要点/证据类型/P0筛选、收藏、隐藏答案、随机抽题、题号链接、代码依据弹窗。无需上传数据或联网。
- 用空格组合检索词，例如“退款 幂等”“401 复核”“P95 并发”；输入题号可直达。搜索包含主问答、深入追问、边界和标签。
- P0是优先练习，P1是深入题。先用下面30题建立主线，再按薄弱模块展开。每题先练30—60秒主回答，再展开实现细节，最后接深入追问。
- Markdown按主题分文件；全量问答.md可直接作为个人检索资料；问答.json和问答.jsonl适合导入其他知识库。JSONL一行一题，带完整引用与关联题号。
- 收藏只存当前浏览器localStorage；不跨浏览器同步，网页另存或更换浏览器后可能不保留。原始内容以Markdown/JSON为准。

## 证据标签是什么意思

| 标签 | 可以如何使用 |
|---|---|
| 代码已核对 | 依据当前代码说明实现；不自动证明已线上运行、历史版本一致或本人编写 |
| 历史评测 | 引用归档结果并带分母、日期、配置与限制；不是本次新跑分 |
| 设计推演 | 根据现有机制分析取舍或提出改进；不得说成已经完成 |
| 场景推演 | 虚构输入用于白板练习；不是本次真实工具或退款操作 |
| 待本人确认 | 个人贡献、开发时间、原创性等需本人补充，不能直接背作经历 |

每题的“边界/易错点”也是答案的一部分。代码标签不意味着该题所有后续改进已经实现。

## 先统一的事实口径

| 项目 | 应使用的说法 |
|---|---|
| 项目时间 | 简历写2026.03—2026.05；可核查该批成绩来自2026-09-09，需本人解释后续迭代时间线 |
| 当前入口 | api/main.py → supportflow.api.create_app；旧材料与新版不能混用 |
| 总体完成率 | 复核406/600→528/600，即67.67%→88.00%，+20.33个百分点 |
| 原始自动评分 | 405/600→527/600，67.50%→87.83%；修正评分误判后两方案各+1 |
| 复合子集 | 85/150→125/150，56.67%→83.33%，+26.67个百分点；属于600的子集 |
| 数据独立性 | 600来自24模板族；150复合来自6族；是参数化开发回归 |
| 公开意图 | 766/1200，63.83%；20源标签、10实际项目类别、固定11类宏F1=0.6786 |
| 另一宏F1口径 | 仅10个有真实样本类别为0.7465，不能替换固定口径而不说明 |
| 12.78秒 | multi整体HTTP请求P95，任务并发2，ASGI进程内链路；不是模型单次推理或生产SLA |
| 成本 | 历史估算0.00445→0.00669元/任务，不是当前报价或实际账单 |
| 退款 | 沙箱业务申请与账本状态，不是真实支付上线证明 |
| MCP | 对外协议入口；聊天内部直接调共享服务。当前7工具，旧文档5工具不能混报 |
| 当前能力 | 新增确定性订单/退款分支、商品定位、进度查询等不能直接解释旧实验收益 |

## 尤其容易被问住的实现边界

1. Redis当前先与SQL历史核对，不能直接声称省去了SQL读取（D02）。
2. 通用Agent的seen会抑制相同失败调用，有限补做不是完善自动重试（B06）。
3. 超时不能证明to_thread内业务写入停止；写结果可能待确认（E12）。
4. SQL与Chroma更新分步，记录降级不等于有可靠自动补偿（C08、F08）。
5. 多Agent对照同时改变多个机制，不能把收益全归因于并行（B12、H07）。
6. 历史复核修了401误判，但当前verify仍有宽泛子串条件；复跑要核对评分版本（H06）。
7. 当前代码未固定知识embedding_function，不能随口报模型名；意图embedding与RAG向量也不同（C06、G02）。
8. 部分问题使用关键词判定完成，有工具证据仍不等于全部自然语言语义正确（B04、H04）。

## 每条简历 bullet 对应哪些题

'''
intro += '| 简历范围 | 题号 | 重点 |\n|---|---|---|\n'
for key,(section,bullet) in SECTIONS.items():
    group=[c for c in cards if c['section_id']==key]
    intro += f"| {bullet} | [{group[0]['id']}—{group[-1]['id']}]({FILES[key]}) | {section} |\n"
intro += '\n## 优先练习30题\n\n'
byid={c['id']:c for c in cards}
for i,ident in enumerate(TOP,1):
    intro += f"{i}. {cardlink(ident)} {byid[ident]['question']}\n"
intro += '''
## 三条模拟面试路线

- **30分钟项目深挖**：A01 → A02 → B01 → B02 → B04 → B07 → E06 → F02 → H01 → H07 → H10 → J07。
- **算法/评测方向**：G01 → G02 → G03 → G04 → G05 → G06 → G09 → H03 → H04 → H06 → H08 → H11。
- **后端/Agent工程方向**：E01 → E03 → E10 → F01 → F03 → F04 → F06 → E12 → C08 → I04 → I08 → J11。

每条路线都先让对方追问，不要一次把所有限制和技术名词堆出来。遇到证据不足，给已知边界和验证方法，比编造结果更有说服力。

## 本人需要补齐的四项信息

1. 3—5月初版、9月评测及当前版本各自的真实参与范围。
2. 自己实现/修改过的模块与对应提交、测试、运行记录。
3. 一次本人参与的问题定位过程：输入、错误、原因、改动、验证。
4. 哪些模块来自已有工程、哪些由AI辅助，自己做了什么审查。

## 来源与复核范围

本次读取并渲染核对了原PDF，检查当前核心源码、已有测试源码及历史报告；没有重跑收费模型评测、整套业务测试或容器部署。历史指标与当前实现严格分开。文件行号和SHA-256见“11_来源与证据.md”及sources.json。后续改代码后行号可能变化，应以符号名和哈希定位。

通用概念参考官方资料：[MCP工具](https://modelcontextprotocol.io/specification/2025-11-25/server/tools)、[SQLite事务](https://sqlite.org/lang_transaction.html)、[Python asyncio](https://docs.python.org/3/library/asyncio-task.html)、[F1定义](https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html)。官方资料用于解释机制，不证明本项目已实现规范的所有可选能力。
'''
(OUT/'00_使用说明与重点题.md').write_text(intro,encoding='utf-8')

all_md=[intro]
for key,(section,_) in SECTIONS.items():
    md=f'# {section}\n\n[返回总索引](00_使用说明与重点题.md)\n\n'
    for c in [c for c in cards if c['section_id']==key]:
        md+=f"<a id=\"{c['id'].lower()}\"></a>\n\n## {c['id']} · {c['question']}\n\n"
        md+=f"**{c['priority']} · {c['evidence']}** | 对应简历：{c['bullet']} | 检索词：{'、'.join(c['tags'])}\n\n"
        for label,field in [('主回答','answer'),('实现细节 / 展开','detail'),('深入追问','followup'),('追问回答','followup_answer'),('边界 / 易错点','boundary')]:
            md+=f'**{label}：** {c[field]}\n\n'
        md+='**依据：** '+'；'.join(sourcelink(s) for s in c['sources'])+'\n\n'
        md+='**关联：** '+' · '.join(cardlink(s) for s in c['related'])+'\n\n---\n\n'
    (OUT/FILES[key]).write_text(md,encoding='utf-8')
    all_md.append(md)
(OUT/'全量问答.md').write_text('\n\n'.join(all_md),encoding='utf-8')

evidence='# 来源与代码定位\n\n短摘录用于定位，不替代完整函数。符号与行号根据当前文件AST解析核验；文件哈希标记制作知识库时的快照。\n\n'
for key,s in sources.items():
    evidence+=f"## {key}\n\n{sourcelink(key)}\n\nSHA-256：`{s['sha256']}`\n\n```text\n{s['snippet']}\n```\n\n"
(OUT/'11_来源与证据.md').write_text(evidence,encoding='utf-8')
(OUT/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2),encoding='utf-8')
payload={'title':'SupportFlow 面试问答知识库','created':'2026-09-24','scope':'简历项目经历，不含实习训练项目',
         'main_questions':len(cards),'followup_questions':len(cards),'sections':SECTIONS,
         'top_questions':TOP,'questions':cards,'sources':sources}
(OUT/'问答.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8')
with (OUT/'问答.jsonl').open('w',encoding='utf-8') as f:
    for c in cards:
        f.write(json.dumps({**c,'source_details':[sources[k] for k in c['sources']]},ensure_ascii=False)+'\n')

template=(OUT/'template.html').read_text(encoding='utf-8')
embedded=json.dumps(payload,ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
(OUT/'知识库.html').write_text(template.replace('__DATA__',embedded),encoding='utf-8')

audit=json.loads((ROOT/'评测结果/GLM-1200复核/audit.json').read_text(encoding='utf-8'))
assert audit['business_cases']==600 and audit['business_executions']==1200
assert audit['reviewed_summaries']['single']['completed']==406
assert audit['reviewed_summaries']['multi']['completed']==528
assert round(audit['public_accuracy']*100,2)==63.83
assert abs(audit['public_macro_f1_fixed_mapping']-0.6786013430639989)<1e-12
qa={'main_questions':len(cards),'followup_questions':len(cards),'sections':dict(Counter(c['section'] for c in cards)),
    'priority_counts':dict(Counter(c['priority'] for c in cards)),
    'evidence_counts':dict(Counter(c['evidence'] for c in cards)),
    'source_symbols_resolved':len(sources),'broken_related_links':0,'duplicate_questions':0,
    'historical_metrics_checked_against_audit':True,
    'note':'只验证知识库结构、引用和历史数字；未运行项目业务测试或模型评测。'}
(OUT/'12_内容校验.json').write_text(json.dumps(qa,ensure_ascii=False,indent=2),encoding='utf-8')
manifest={p.relative_to(OUT).as_posix():hashlib.sha256(p.read_bytes()).hexdigest()
          for p in OUT.rglob('*') if p.is_file() and p.name!='13_文件校验.json'}
(OUT/'13_文件校验.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
zip_path=ROOT/'SupportFlow_面试问答知识库_120题_20260924.zip'
with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED) as z:
    for p in OUT.rglob('*'):
        if p.is_file(): z.write(p,OUT.name+'/'+p.relative_to(OUT).as_posix())
print(json.dumps(qa,ensure_ascii=False,indent=2))
print('OUTPUT',OUT)
print('ZIP',zip_path)
