# scripts\audit_trial_dataset.py

## 输入输出流

冻结业务数据、公开分区、清单与旧样本进入只读核对；输出integrity-audit.json，记录哈希、数量、分区和近重复检查。

## 先理解设计

校验器独立重算选中公开样本的相似度与暴露排除，防止仅相信生成器自己的声明；全程不调用模型。

源码 SHA256：`20cd13c662f30292f7d6a6120eb524321bd878520ae771a0e7a5961182470bb6`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""Audit frozen dataset integrity, exposure filters and split balance; never call an LLM."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L3**

```python
from collections import Counter
```

导入本段使用的标准库、依赖或项目组件。

**L4**

```python
import hashlib
```

导入本段使用的标准库、依赖或项目组件。

**L5**

```python
import json
```

导入本段使用的标准库、依赖或项目组件。

**L6**

```python
from pathlib import Path
```

导入本段使用的标准库、依赖或项目组件。

**L7**

```python
import sys
```

导入本段使用的标准库、依赖或项目组件。

**L9**

```python
ROOT = Path(__file__).resolve().parents[1]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L10**

```python
sys.path.insert(0, str(ROOT))
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L11**

```python
from evaluation.public_intents import MAP
```

导入本段使用的标准库、依赖或项目组件。

**L12**

```python
from scripts.build_acceptance_dataset import canonical
```

导入本段使用的标准库、依赖或项目组件。

**L13**

```python
from scripts.prepare_public_intents import grams, normalize
```

导入本段使用的标准库、依赖或项目组件。

### L16 · read

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L16**

```python
def read(path):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L17**

```python
    return json.loads(path.read_text(encoding="utf-8"))
```

结束当前函数并把本行构造的结果交给调用方。

### L20 · audit

重新读取生成产物与固定哈希，检查标签平衡、族分区、源行唯一及近重复；成功写审计JSON，失败立即中断。

**L20**

```python
def audit():
```

重新读取生成产物与固定哈希，检查标签平衡、族分区、源行唯一及近重复；成功写审计JSON，失败立即中断。

**L21**

```python
    folder = ROOT / "evaluation/datasets/trial-v3"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L22**

```python
    manifest = read(folder / "manifest.json")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L23**

```python
    public = read(folder / "public-manifest.json")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L24**

```python
    families, texts, ids = {}, {}, set()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L25**

```python
    source_rows, public_texts = set(), set()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L26**

```python
    by_label = {}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L27**

```python
    old = read(ROOT / ".runtime/datasets/bitext-sample.json")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L28**

```python
    exposed = [grams(normalize(r["message"])) for r in old["examples"]]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L29**

```python
    result = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L30**

```python
        "method": "Offline integrity and lexical leakage checks; no model quality evaluation or human review",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L31**

```python
        "authored": {},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L32**

```python
        "public_intents": {},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L33**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L34**

```python
    for split in ["development", "validation", "acceptance"]:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L35**

```python
        raw = (folder / (split + ".json")).read_bytes()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L36**

```python
        assert hashlib.sha256(raw).hexdigest() == manifest["splits"][split]["sha256"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L37**

```python
        cases = json.loads(raw)["cases"]
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L38**

```python
        for c in cases:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L39**

```python
            assert c["id"] not in ids
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L40**

```python
            ids.add(c["id"])
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L41**

```python
            assert families.setdefault(c["family"], split) == split
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L42**

```python
            assert texts.setdefault(canonical(c["turns"]), split) == split
```

去除消息中的订单/咨询编号及金额，检查模板换参数后是否跨分区重复；不等于语义相似度判定。

**L43**

```python
        result["authored"][split] = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L44**

```python
            "cases": len(cases),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L45**

```python
            "families": len({c["family"] for c in cases}),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L46**

```python
            "groups": dict(Counter(c["group"] for c in cases)),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L47**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L48**

```python
        raw = (ROOT / public["splits"][split]["path"]).read_bytes()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L49**

```python
        assert hashlib.sha256(raw).hexdigest() == public["splits"][split]["sha256"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L50**

```python
        rows = json.loads(raw)["examples"]
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L51**

```python
        for r in rows:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L52**

```python
            normalized = normalize(r["message"])
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L53**

```python
            assert r["source_row"] not in source_rows
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L54**

```python
            assert normalized not in public_texts
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L55**

```python
            assert hashlib.sha256(r["message"].encode()).hexdigest() == r["text_sha256"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L56**

```python
            source_rows.add(r["source_row"])
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L57**

```python
            public_texts.add(normalized)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L58**

```python
            a = grams(normalized)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L59**

```python
            assert all(len(a & b) / max(1, len(a | b)) < 0.82 for b in exposed)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L60**

```python
            by_label.setdefault(r["label"], []).append(a)
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L61**

```python
        counts = Counter(r["label"] for r in rows)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L62**

```python
        assert len(counts) == 27 and len(set(counts.values())) == 1
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L63**

```python
        result["public_intents"][split] = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L64**

```python
            "rows": len(rows),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L65**

```python
            "source_labels": len(counts),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L66**

```python
            "mapped_rows": sum(r["label"] in MAP for r in rows),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L67**

```python
            "excluded_rows": sum(r["label"] not in MAP for r in rows),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L68**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L69**

```python
    for items in by_label.values():
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L70**

```python
        for i, a in enumerate(items):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L71**

```python
            assert all(len(a & b) / max(1, len(a | b)) < 0.82 for b in items[:i])
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L72**

```python
    assert len(ids) == 1200 and len(families) == 48 and len(source_rows) == 2700
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L73**

```python
    result["checks"] = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L74**

```python
        "frozen_hashes": True,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L75**

```python
        "authored_ids_unique": True,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L76**

```python
        "family_splits_disjoint": True,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L77**

```python
        "normalized_authored_templates_disjoint": True,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L78**

```python
        "public_source_rows_unique": True,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L79**

```python
        "public_normalized_text_unique": True,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L80**

```python
        "public_old_sample_and_near_matches_excluded": True,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L81**

```python
        "public_within_label_near_duplicate_threshold": 0.82,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L82**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L83**

```python
    result["limitations"] = [
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L84**

```python
        "Semantic similarity may cross splits",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L85**

```python
        "Same author knows scenario design; not independent blind acceptance",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L86**

```python
        "Public training corpus may overlap model pretraining",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L87**

```python
        "No enterprise customer records or enterprise sign-off",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L88**

```python
    ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L89**

```python
    path = folder / "integrity-audit.json"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L90**

```python
    path.write_text(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L91**

```python
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L92**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L93**

```python
    print(json.dumps(result, ensure_ascii=False, indent=2))
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L96**

```python
if __name__ == "__main__":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L97**

```python
    audit()
```

重新读取生成产物与固定哈希，检查标签平衡、族分区、源行唯一及近重复；成功写审计JSON，失败立即中断。

## 结合全项目看：边界与增强

自动完整性审计不等于金标语义正确或人工签字。异常断言停止流程，不能删去失败样本后宣称通过。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
