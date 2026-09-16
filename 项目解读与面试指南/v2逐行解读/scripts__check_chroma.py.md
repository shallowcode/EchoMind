# scripts\check_chroma.py

## 输入输出流

命令行参数、工作区文件或固定下载源进入维护脚本；输出明确的本地模型、数据集、身份文件、验证记录或学习文档。

## 先理解设计

下载源与结果哈希、文件落点和被忽略的敏感/大文件需一并核对；脚本不会隐式调用付费模型。

源码 SHA256：`6ec9e0b0917ba78a0ab33e1e84e8b82fef78fc52cf67d312d349a2bf3e4ab09a`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""Explicit real Chroma integration check; downloads default ONNX embedding on first use."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L3**

```python
import asyncio
```

导入本段使用的标准库、依赖或项目组件。

**L4**

```python
from pathlib import Path
```

导入本段使用的标准库、依赖或项目组件。

**L5**

```python
import sys
```

导入本段使用的标准库、依赖或项目组件。

**L6**

```python
import time
```

导入本段使用的标准库、依赖或项目组件。

**L8**

```python
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L9**

```python
from supportflow.contracts import Settings, Principal
```

导入本段使用的标准库、依赖或项目组件。

**L10**

```python
from supportflow.store import Store
```

导入本段使用的标准库、依赖或项目组件。

**L11**

```python
from supportflow.knowledge import Knowledge
```

导入本段使用的标准库、依赖或项目组件。

### L14 · main

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L14**

```python
async def main():
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L15**

```python
    root = Path(".runtime") / ("chroma-check-" + str(time.time_ns()))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L16**

```python
    s = Settings(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L17**

```python
        db_path=str(root / "db.sqlite"),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L18**

```python
        storage="chroma",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L19**

```python
        chroma_path=str(root / "vectors"),
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L20**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L21**

```python
    kb = Knowledge(Store(s.db_path), s, None)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L22**

```python
    kb.add("a", "login", "Login", "401 login token expired, sign in again.")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L23**

```python
    kb.add("b", "private", "Private", "TENANT_B_PRIVATE_RECORD")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L24**

```python
    first = kb.search("a", "401 login", 3)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L25**

```python
    assert first and all("PRIVATE" not in r["content"] for r in first)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L26**

```python
    old = first[0]["id"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L27**

```python
    kb.add("a", "login", "Login", "401 authentication expired; renew the session.")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L28**

```python
    assert all(r["id"] != old for r in kb.search("a", "401 login", 3))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L29**

```python
    p = Principal("a", "alice")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L30**

```python
    await kb.archive(p, "conv", "Order ORD1001 remains pending.", 1)
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L31**

```python
    assert await kb.recall(p, "order")
```

将模型提出的工具操作先验证再执行，并在 finally 中记录成功/失败与耗时。

**L32**

```python
    assert not await kb.recall(Principal("b", "alice"), "order")
```

将模型提出的工具操作先验证再执行，并在 finally 中记录成功/失败与耗时。

**L33**

```python
    await kb.project_profile(p, {"language": "zh"})
```

等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。

**L34**

```python
    print(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L35**

```python
        "REAL CHROMA PASS: tenant isolation, version replacement, episodic recall, profile projection"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L36**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L39**

```python
if __name__ == "__main__":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L40**

```python
    asyncio.run(main())
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

## 结合全项目看：边界与增强

跨平台运行与远程服务配置应在目标环境复验；学习文档行号需在源码变化后重新生成。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
