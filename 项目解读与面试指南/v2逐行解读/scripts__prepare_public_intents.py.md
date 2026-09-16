# scripts\prepare_public_intents.py

## 输入输出流

固定修订Bitext CSV及旧54条已暴露样本进入过滤器；输出2700条分层意图样本到.runtime，以及受版本控制的来源、许可、哈希清单。

## 先理解设计

排除旧样本近邻，按源标签对候选池的字符三元组做连通分量聚类，每簇取代表后分区；24个源标签进入当前意图映射。

源码 SHA256：`7fc4ba4190c84a95b85878eca0ee54e5324a67cf6fe992a3e0be450a143f952d`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""Stratified public intent samples, kept separate from authored transaction tasks.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L3**

```python
Use one representative per near-duplicate cluster; split only after clustering.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L4**

```python
Raw/derived Bitext text stays under .runtime with source/license metadata.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L5**

```python
"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L7**

```python
from collections import defaultdict
```

导入本段使用的标准库、依赖或项目组件。

**L8**

```python
import csv
```

导入本段使用的标准库、依赖或项目组件。

**L9**

```python
import hashlib
```

导入本段使用的标准库、依赖或项目组件。

**L10**

```python
import json
```

导入本段使用的标准库、依赖或项目组件。

**L11**

```python
from pathlib import Path
```

导入本段使用的标准库、依赖或项目组件。

**L12**

```python
import random
```

导入本段使用的标准库、依赖或项目组件。

**L13**

```python
import re
```

导入本段使用的标准库、依赖或项目组件。

**L14**

```python
import sys
```

导入本段使用的标准库、依赖或项目组件。

**L16**

```python
ROOT = Path(__file__).resolve().parents[1]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L17**

```python
sys.path.insert(0, str(ROOT))
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L18**

```python
from scripts.build_supportflow_dataset import REV, URL
```

导入本段使用的标准库、依赖或项目组件。

**L19**

```python
from scripts.build_acceptance_dataset import write_frozen
```

导入本段使用的标准库、依赖或项目组件。

### L22 · normalize

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L22**

```python
def normalize(text):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L23**

```python
    return re.sub(r"[^a-z0-9]+", " ", text.lower()).strip()
```

结束当前函数并把本行构造的结果交给调用方。

### L26 · grams

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L26**

```python
def grams(text):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L27**

```python
    return {text[i : i + 3] for i in range(max(1, len(text) - 2))}
```

结束当前函数并把本行构造的结果交给调用方。

### L30 · representatives

按字符三元组Jaccard阈值建立候选近重复图，以并查集形成连通分量，每个分量选一个原始代表。

**L30**

```python
def representatives(rows):
```

按字符三元组Jaccard阈值建立候选近重复图，以并查集形成连通分量，每个分量选一个原始代表。

**L31**

```python
    """Connected components at character-trigram Jaccard >= .82, within source intent.
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L33**

```python
    One representative per component means selected representatives never meet this
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L34**

```python
    lexical threshold with each other. This does not establish semantic independence.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L35**

```python
    """
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L36**

```python
    parents = list(range(len(rows)))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L38 · root

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L38**

```python
    def root(i):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L39**

```python
        while parents[i] != i:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L40**

```python
            parents[i] = parents[parents[i]]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L41**

```python
            i = parents[i]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L42**

```python
        return i
```

结束当前函数并把本行构造的结果交给调用方。

**L44**

```python
    sets = [grams(normalize(r["instruction"])) for r in rows]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L45**

```python
    for i, a in enumerate(sets):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L46**

```python
        for j in range(i):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L47**

```python
            b = sets[j]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L48**

```python
            if min(len(a), len(b)) < 0.82 * max(len(a), len(b)):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L49**

```python
                continue
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L50**

```python
            common = len(a & b)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L51**

```python
            if common / max(1, len(a) + len(b) - common) >= 0.82:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L52**

```python
                parents[root(i)] = root(j)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L53**

```python
    groups = {}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L54**

```python
    for i, row in enumerate(rows):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L55**

```python
        groups.setdefault(root(i), row)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L56**

```python
    return list(groups.values())
```

结束当前函数并把本行构造的结果交给调用方。

### L59 · main

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L59**

```python
def main():
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L60**

```python
    raw_path = ROOT / ".runtime/datasets/bitext.csv"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L61**

```python
    raw = raw_path.read_bytes()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L62**

```python
    digest = hashlib.sha256(raw).hexdigest()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L63**

```python
    if digest != "6f81102b0100b97b8468eb04368033a23206bf1fde9d53500d5806ec1001a434":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L64**

```python
        raise ValueError("Public source hash changed; fetch the pinned revision first")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L65**

```python
    old = json.loads(
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L66**

```python
        (ROOT / ".runtime/datasets/bitext-sample.json").read_text(encoding="utf-8")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L67**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L68**

```python
    exposed = [grams(normalize(r["message"])) for r in old["examples"]]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L70 · previously_exposed

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L70**

```python
    def previously_exposed(text):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L71**

```python
        a = grams(normalize(text))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L72**

```python
        return any(len(a & b) / max(1, len(a | b)) >= 0.82 for b in exposed)
```

结束当前函数并把本行构造的结果交给调用方。

**L74**

```python
    by_label = defaultdict(list)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L75**

```python
    with raw_path.open(encoding="utf-8-sig", newline="") as f:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L76**

```python
        for index, row in enumerate(csv.DictReader(f)):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L77**

```python
            if not previously_exposed(row["instruction"]):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L78**

```python
                by_label[row["intent"]].append({**row, "source_row": index})
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L79**

```python
    examples = {s: [] for s in ["development", "validation", "acceptance"]}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L80**

```python
    rng = random.Random(20260909)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L81**

```python
    counts = {}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L82**

```python
    for label, rows in sorted(by_label.items()):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L83**

```python
        rng.shuffle(rows)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L84**

```python
        selected = representatives(rows[:400])
```

按字符三元组Jaccard阈值建立候选近重复图，以并查集形成连通分量，每个分量选一个原始代表。

**L85**

```python
        if len(selected) < 100:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L86**

```python
            selected = representatives(rows)
```

按字符三元组Jaccard阈值建立候选近重复图，以并查集形成连通分量，每个分量选一个原始代表。

**L87**

```python
        if len(selected) < 100:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L88**

```python
            raise ValueError("Insufficient distinct clusters for " + label)
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L89**

```python
        rng.shuffle(selected)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L90**

```python
        counts[label] = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L91**

```python
            "available_rows_after_exposure_filter": len(rows),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L92**

```python
            "candidate_clusters": len(selected),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L93**

```python
            "selected": 100,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L94**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L95**

```python
        for i, row in enumerate(selected[:100]):
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L96**

```python
            split = (
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L97**

```python
                "development" if i < 60 else "validation" if i < 80 else "acceptance"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L98**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L99**

```python
            examples[split].append(
```

把这一轮的事实、输出或失败加入容器，供后续汇总或验证。

**L100**

```python
                {
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L101**

```python
                    "message": row["instruction"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L102**

```python
                    "label": label,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L103**

```python
                    "source_row": row["source_row"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L104**

```python
                    "text_sha256": hashlib.sha256(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L105**

```python
                        row["instruction"].encode()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L106**

```python
                    ).hexdigest(),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L107**

```python
                }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L108**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L109**

```python
    common = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L110**

```python
        "source": URL,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L111**

```python
        "revision": REV,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L112**

```python
        "license": "CDLA-Sharing-1.0",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L113**

```python
        "license_url": "https://cdla.dev/sharing-1-0/",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L114**

```python
        "attribution": "Bitext Innovations, 2024",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L115**

```python
        "source_sha256": digest,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L116**

```python
        "source_type": "public hybrid synthetic training corpus, not customer traffic",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L117**

```python
        "purpose": "English intent evaluation only; not transactional or Chinese task completion",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L118**

```python
        "near_duplicate_method": "one representative per within-intent connected component, character-trigram Jaccard >= .82; old 54-example sample and lexical near matches excluded",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L119**

```python
        "limitations": [
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L120**

```python
            "Semantic duplicates and cross-label lexical neighbors may remain",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L121**

```python
            "Model pretraining overlap unknown",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L122**

```python
            "No independent human adjudication of ontology mapping",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L123**

```python
        ],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L124**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L125**

```python
    manifest = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L126**

```python
        **common,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L127**

```python
        "source_rows": 26872,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L128**

```python
        "sampled": 2700,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L129**

```python
        "per_label": counts,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L130**

```python
        "splits": {},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L131**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L132**

```python
    for split, rows in examples.items():
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L133**

```python
        path = ROOT / ".runtime/datasets/bitext-v2" / (split + ".json")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L134**

```python
        sha = write_frozen(path, {**common, "split": split, "examples": rows})
```

序列化并哈希内容；文件存在且不同则拒绝覆写，防止悄悄改变已报告数据集。

**L135**

```python
        manifest["splits"][split] = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L136**

```python
            "path": str(path.relative_to(ROOT)),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L137**

```python
            "count": len(rows),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L138**

```python
            "sha256": sha,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L139**

```python
        }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L140**

```python
    write_frozen(ROOT / "evaluation/datasets/trial-v3/public-manifest.json", manifest)
```

序列化并哈希内容；文件存在且不同则拒绝覆写，防止悄悄改变已报告数据集。

**L141**

```python
    print(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L142**

```python
        json.dumps(
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L143**

```python
            {"sampled": manifest["sampled"], "splits": manifest["splits"]},
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L144**

```python
            ensure_ascii=False,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L145**

```python
            indent=2,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L146**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L147**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L150**

```python
if __name__ == "__main__":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L151**

```python
    main()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

## 结合全项目看：边界与增强

词面去重不证明语义独立；公开训练语料可能与模型预训练重合。数据不是企业客服日志，也不能证明事务完成率。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
