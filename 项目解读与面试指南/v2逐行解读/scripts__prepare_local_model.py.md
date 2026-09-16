# scripts\prepare_local_model.py

## 输入输出流

命令行参数、工作区文件或固定下载源进入维护脚本；输出明确的本地模型、数据集、身份文件、验证记录或学习文档。

## 先理解设计

下载源与结果哈希、文件落点和被忽略的敏感/大文件需一并核对；脚本不会隐式调用付费模型。

源码 SHA256：`04bf4d5ad29516eb5dcad1995ad0ae22a7faf221db92a5e978c6147a2da201b7`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""Download pinned official Qwen GGUF and llama.cpp CPU binaries into .runtime only."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L3**

```python
import hashlib
```

导入本段使用的标准库、依赖或项目组件。

**L4**

```python
import json
```

导入本段使用的标准库、依赖或项目组件。

**L5**

```python
from pathlib import Path
```

导入本段使用的标准库、依赖或项目组件。

**L6**

```python
import urllib.request
```

导入本段使用的标准库、依赖或项目组件。

**L7**

```python
import zipfile
```

导入本段使用的标准库、依赖或项目组件。

**L8**

```python
import argparse
```

导入本段使用的标准库、依赖或项目组件。

**L10**

```python
ROOT = Path(__file__).resolve().parents[1] / ".runtime"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L11**

```python
ROOT.mkdir(exist_ok=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L12**

```python
MODEL_REV = "23749fefcc72300e3a2ad315e1317431b06b590a"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L13**

```python
parser = argparse.ArgumentParser()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L14**

```python
parser.add_argument("--size", choices=["0.6B", "1.7B"], default="0.6B")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L15**

```python
args = parser.parse_args()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L16**

```python
if args.size == "1.7B":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L17**

```python
    MODEL_REV = "90862c4b9d2787eaed51d12237eafdfe7c5f6077"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L18**

```python
sources = {
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L19**

```python
    "llama.zip": "https://github.com/ggml-org/llama.cpp/releases/download/b10853/llama-b10853-bin-win-cpu-x64.zip",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L20**

```python
    f"Qwen3-{args.size}-Q8_0.gguf": f"https://huggingface.co/Qwen/Qwen3-{args.size}-GGUF/resolve/{MODEL_REV}/Qwen3-{args.size}-Q8_0.gguf",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L21**

```python
}
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L22**

```python
manifest_path = ROOT / "model_manifest.json"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L23**

```python
manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L24**

```python
for name, url in sources.items():
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L25**

```python
    target = ROOT / name
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L26**

```python
    if not target.exists():
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L27**

```python
        print("Downloading", name, flush=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L28**

```python
        urllib.request.urlretrieve(url, target.with_suffix(target.suffix + ".part"))
```

把查询改写、并发检索、按稳定 ID 去重和重排接成一条可降级链路。

**L29**

```python
        target.with_suffix(target.suffix + ".part").replace(target)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L30**

```python
    digest = hashlib.file_digest(target.open("rb"), "sha256").hexdigest()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L31**

```python
    manifest[name] = {"source": url, "sha256": digest, "bytes": target.stat().st_size}
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L32**

```python
    print(name, target.stat().st_size, digest, flush=True)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L33**

```python
with zipfile.ZipFile(ROOT / "llama.zip") as z:
```

限定资源、事务、超时或上下文的生存范围，退出时清理。

**L34**

```python
    for name in z.namelist():
```

遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。

**L35**

```python
        if (
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L36**

```python
            not (ROOT / "llama" / name)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L37**

```python
            .resolve()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L38**

```python
            .is_relative_to((ROOT / "llama").resolve())
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L39**

```python
        ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L40**

```python
            raise ValueError("Archive traversal")
```

显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。

**L41**

```python
    if not (ROOT / "llama/llama-server.exe").exists():
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L42**

```python
        z.extractall(ROOT / "llama")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L43**

```python
(ROOT / "model_manifest.json").write_text(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L44**

```python
    json.dumps(manifest, indent=2), encoding="utf-8"
```

在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。

**L45**

```python
)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

## 结合全项目看：边界与增强

跨平台运行与远程服务配置应在目标环境复验；学习文档行号需在源码变化后重新生成。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
