# scripts\start_local.py

## 输入输出流

命令行参数、工作区文件或固定下载源进入维护脚本；输出明确的本地模型、数据集、身份文件、验证记录或学习文档。

## 先理解设计

下载源与结果哈希、文件落点和被忽略的敏感/大文件需一并核对；脚本不会隐式调用付费模型。

源码 SHA256：`3e5f9a7c6df11d1f9e78d6ac872fac3bc47ce705d432d2a566e7e15f4fc98a2d`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""Start the local sandbox without a visible helper window; never stop occupied ports."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L3**

```python
import json
```

导入本段使用的标准库、依赖或项目组件。

**L4**

```python
import os
```

导入本段使用的标准库、依赖或项目组件。

**L5**

```python
from pathlib import Path
```

导入本段使用的标准库、依赖或项目组件。

**L6**

```python
import socket
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

**L9**

```python
import time
```

导入本段使用的标准库、依赖或项目组件。

**L10**

```python
import urllib.request
```

导入本段使用的标准库、依赖或项目组件。

**L12**

```python
ROOT = Path(__file__).resolve().parents[1]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L13**

```python
RUNTIME = ROOT / ".runtime"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

### L16 · get

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L16**

```python
def get(url):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L17**

```python
    try:
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L18**

```python
        with urllib.request.urlopen(url, timeout=2) as response:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L19**

```python
            return json.load(response)
```

结束当前函数并把本行构造的结果交给调用方。

**L20**

```python
    except Exception:
```

处理这一类失败；注意哪些失败允许降级，哪些必须拒绝操作。

**L21**

```python
        return None
```

结束当前函数并把本行构造的结果交给调用方。

### L24 · occupied

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L24**

```python
def occupied(port):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L25**

```python
    with socket.socket() as connection:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L26**

```python
        connection.settimeout(0.5)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L27**

```python
        return connection.connect_ex(("127.0.0.1", port)) == 0
```

结束当前函数并把本行构造的结果交给调用方。

### L30 · launch

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L30**

```python
def launch(args, name, env):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L31**

```python
    flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L32**

```python
    with (RUNTIME / f"{name}.log").open("ab") as output:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L33**

```python
        return subprocess.Popen(
```

结束当前函数并把本行构造的结果交给调用方。

**L34**

```python
            args,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L35**

```python
            cwd=ROOT,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L36**

```python
            env=env,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L37**

```python
            stdout=output,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L38**

```python
            stderr=subprocess.STDOUT,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L39**

```python
            creationflags=flags,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L40**

```python
            start_new_session=sys.platform != "win32",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L41**

```python
        ).pid
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L44 · wait_ready

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L44**

```python
def wait_ready(url, seconds=60):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L45**

```python
    end = time.monotonic() + seconds
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L46**

```python
    while time.monotonic() < end:
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L47**

```python
        if get(url):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L48**

```python
            return
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L49**

```python
        time.sleep(0.5)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L50**

```python
    raise RuntimeError(f"Service not ready: {url}; inspect .runtime logs")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

### L53 · main

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L53**

```python
def main():
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L54**

```python
    RUNTIME.mkdir(exist_ok=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L55**

```python
    model = RUNTIME / "Qwen3-1.7B-Q8_0.gguf"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L56**

```python
    binary = RUNTIME / "llama/llama-server.exe"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L57**

```python
    if not model.exists() or not binary.exists():
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L58**

```python
        raise RuntimeError("Run scripts/prepare_local_model.py --size 1.7B first")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L59**

```python
    env = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L60**

```python
        **os.environ,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L61**

```python
        "SF_MODEL_BACKEND": "compatible",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L62**

```python
        "SF_MODEL_URL": "http://127.0.0.1:8081/v1",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L63**

```python
        "SF_MODEL_NAME": "Qwen3-1.7B-Q8_0",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L64**

```python
        "SF_MODEL_KEY": "",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L65**

```python
        "SF_LOCAL_CHAT_TEMPLATE": "true",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L66**

```python
        "SF_STORAGE": "chroma",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L67**

```python
        "SF_BUSINESS_MODE": "sandbox",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L68**

```python
        "SF_PUBLIC_URL": "http://localhost:8000",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L69**

```python
    }
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L70**

```python
    pids = {}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L71**

```python
    if occupied(8081):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L72**

```python
        models = get("http://127.0.0.1:8081/v1/models") or {}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L73**

```python
        if not any("1.7B" in m.get("id", "") for m in models.get("data", [])):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L74**

```python
            raise RuntimeError(
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L75**

```python
                "Port 8081 is occupied by a different/unverified model server"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L76**

```python
            )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L77**

```python
    else:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L78**

```python
        pids["model"] = launch(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L79**

```python
            [
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L80**

```python
                str(binary),
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L81**

```python
                "-m",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L82**

```python
                ".runtime/Qwen3-1.7B-Q8_0.gguf",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L83**

```python
                "--host",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L84**

```python
                "127.0.0.1",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L85**

```python
                "--port",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L86**

```python
                "8081",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L87**

```python
                "-c",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L88**

```python
                "16384",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L89**

```python
                "-np",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L90**

```python
                "2",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L91**

```python
                "-t",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L92**

```python
                "6",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L93**

```python
                "--jinja",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L94**

```python
            ],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L95**

```python
            "local-model",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L96**

```python
            env,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L97**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L98**

```python
    wait_ready("http://127.0.0.1:8081/health")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L99**

```python
    if occupied(8000):
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L100**

```python
        info = get("http://127.0.0.1:8000/openapi.json") or {}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L101**

```python
        if info.get("info", {}).get("title") != "SupportFlow":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L102**

```python
            raise RuntimeError("Port 8000 is occupied by another service")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L103**

```python
    else:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L104**

```python
        subprocess.run(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L105**

```python
            [sys.executable, "scripts/bootstrap_supportflow.py"],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L106**

```python
            cwd=ROOT,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L107**

```python
            env=env,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L108**

```python
            check=True,
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L109**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L110**

```python
        pids["api"] = launch(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L111**

```python
            [
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L112**

```python
                sys.executable,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L113**

```python
                "-m",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L114**

```python
                "uvicorn",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L115**

```python
                "api.main:app",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L116**

```python
                "--host",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L117**

```python
                "127.0.0.1",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L118**

```python
                "--port",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L119**

```python
                "8000",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L120**

```python
            ],
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L121**

```python
            "local-api",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L122**

```python
            env,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L123**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L124**

```python
    wait_ready("http://127.0.0.1:8000/health")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L125**

```python
    (RUNTIME / "local-processes.json").write_text(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L126**

```python
        json.dumps(pids, indent=2), encoding="utf-8"
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L127**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L128**

```python
    print("SupportFlow ready: http://127.0.0.1:8000/docs")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L129**

```python
    print(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L130**

```python
        "Credentials: .runtime/demo-tokens.json (not printed); created process IDs:",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L131**

```python
        pids,
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L132**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L135**

```python
if __name__ == "__main__":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L136**

```python
    main()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

## 结合全项目看：边界与增强

跨平台运行与远程服务配置应在目标环境复验；学习文档行号需在源码变化后重新生成。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
