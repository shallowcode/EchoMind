# scripts\start_glm.py

## 输入输出流

命令行参数、工作区文件或固定下载源进入维护脚本；输出明确的本地模型、数据集、身份文件、验证记录或学习文档。

## 先理解设计

下载源与结果哈希、文件落点和被忽略的敏感/大文件需一并核对；脚本不会隐式调用付费模型。

源码 SHA256：`67baadd4eefaed49dca3819399a7e131e953ed4b8e01b3b47418942eaef8df95`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""Launch the configured GLM sandbox in a hidden process on a separate local port."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L3**

```python
import argparse
```

导入本段使用的标准库、依赖或项目组件。

**L4**

```python
import json
```

导入本段使用的标准库、依赖或项目组件。

**L5**

```python
import os
```

导入本段使用的标准库、依赖或项目组件。

**L6**

```python
from pathlib import Path
```

导入本段使用的标准库、依赖或项目组件。

**L7**

```python
import subprocess
```

导入本段使用的标准库、依赖或项目组件。

**L8**

```python
import sys
```

导入本段使用的标准库、依赖或项目组件。

**L10**

```python
ROOT = Path(__file__).resolve().parents[1]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L11**

```python
sys.path.insert(0, str(ROOT))
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L12**

```python
from scripts.start_local import occupied, launch, wait_ready
```

导入本段使用的标准库、依赖或项目组件。

### L15 · main

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L15**

```python
def main():
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L16**

```python
    parser = argparse.ArgumentParser()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L17**

```python
    parser.add_argument("--port", type=int, default=8002)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L18**

```python
    parser.add_argument("--env-file", default=".runtime/glm.env")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L19**

```python
    args = parser.parse_args()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L20**

```python
    config = (ROOT / args.env_file).resolve()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L21**

```python
    if not config.is_file():
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L22**

```python
        raise RuntimeError(
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L23**

```python
            "Create the private GLM configuration from .env.supportflow.example first"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L24**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L25**

```python
    if occupied(args.port):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L26**

```python
        raise RuntimeError(
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L27**

```python
            f"Port {args.port} is already occupied; use that service or choose another port"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L28**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L29**

```python
    env = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L30**

```python
        **os.environ,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L31**

```python
        "SF_ENV_FILE": str(config),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L32**

```python
        "SF_DB_PATH": "data/supportflow-glm.sqlite3",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L33**

```python
        "SF_CHROMA_PATH": "data/supportflow-glm-chroma",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L34**

```python
        "SF_PUBLIC_URL": f"http://localhost:{args.port}",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L35**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L36**

```python
    # Use the selected file rather than stale model settings inherited from a local run.
```

作者注释，说明约束或设计意图；本行不执行。

**L37**

```python
    for field in [
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L38**

```python
        "MODEL_BACKEND",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L39**

```python
        "MODEL_URL",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L40**

```python
        "MODEL_NAME",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L41**

```python
        "MODEL_KEY",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L42**

```python
        "LOCAL_CHAT_TEMPLATE",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L43**

```python
        "SUPPORTS_JSON_SCHEMA",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L44**

```python
        "MODEL_THINKING",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L45**

```python
        "PRICING_PROFILE",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L46**

```python
    ]:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L47**

```python
        env.pop("SF_" + field, None)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L48**

```python
    subprocess.run(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L49**

```python
        [
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L50**

```python
            sys.executable,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L51**

```python
            "scripts/bootstrap_supportflow.py",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L52**

```python
            "--output",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L53**

```python
            ".runtime/glm-demo-tokens.json",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L54**

```python
        ],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L55**

```python
        cwd=ROOT,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L56**

```python
        env=env,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L57**

```python
        check=True,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L58**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L59**

```python
    pid = launch(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L60**

```python
        [
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L61**

```python
            sys.executable,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L62**

```python
            "-m",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L63**

```python
            "uvicorn",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L64**

```python
            "api.main:app",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L65**

```python
            "--host",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L66**

```python
            "127.0.0.1",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L67**

```python
            "--port",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L68**

```python
            str(args.port),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L69**

```python
        ],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L70**

```python
        "glm-api",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L71**

```python
        env,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L72**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L73**

```python
    wait_ready(f"http://127.0.0.1:{args.port}/health")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L74**

```python
    (ROOT / ".runtime/glm-service.json").write_text(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L75**

```python
        json.dumps({"pid": pid, "port": args.port}), encoding="utf-8"
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L76**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L77**

```python
    print(f"GLM service ready: http://127.0.0.1:{args.port}/docs; PID {pid}")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L80**

```python
if __name__ == "__main__":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L81**

```python
    main()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

## 结合全项目看：边界与增强

跨平台运行与远程服务配置应在目标环境复验；学习文档行号需在源码变化后重新生成。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
