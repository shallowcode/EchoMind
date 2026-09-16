# api\main.py

## 输入输出流

应用启动器导入 create_app；输出共享鉴权、业务、MCP 和监控的 FastAPI 应用。

## 先理解设计

入口保持薄层，业务规则集中在 supportflow，避免 CLI/HTTP/评测各自实现不同流程。

源码 SHA256：`f29d51494fec42134e33a1587f48dccf092704e74c587a2d5d563b65eb2009e9`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""Primary authenticated SupportFlow entry point; v1 is archived in legacy_main.py.txt."""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L3**

```python
from pathlib import Path
```

导入本段使用的标准库、依赖或项目组件。

**L4**

```python
import sys
```

导入本段使用的标准库、依赖或项目组件。

**L6**

```python
root = str(Path(__file__).resolve().parents[1])
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L7**

```python
if root not in sys.path:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L8**

```python
    sys.path.insert(0, root)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L10**

```python
from supportflow.api import create_app
```

导入本段使用的标准库、依赖或项目组件。

**L12**

```python
app = create_app()
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L14**

```python
if __name__ == "__main__":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L15**

```python
    import uvicorn
```

导入本段使用的标准库、依赖或项目组件。

**L17**

```python
    uvicorn.run(app, host="127.0.0.1", port=8000)
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

## 结合全项目看：边界与增强

生产需配置可达模型、受管凭据、HTTPS 和基础设施健康检查。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
