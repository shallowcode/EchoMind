# tests\test_supportflow_skills.py

## 输入输出流

隔离的测试目录、身份、请求或模拟依赖进入测试；输出断言通过/失败与 pytest 结果。

## 先理解设计

测试替身验证工程行为，不能充当真实模型准确率或生产性能证据。

源码 SHA256：`66e82cefe7a59d6d3edc30daca2728340c1c3cb73d99a472643870864f861f74`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
from core.skill_loader import SkillManager
```

导入本段使用的标准库、依赖或项目组件。

**L2**

```python
from core.intent_recognizer import IntentRecognizer
```

导入本段使用的标准库、依赖或项目组件。

### L5 · test_skill_reload_and_agent_scope

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L5**

```python
def test_skill_reload_and_agent_scope(tmp_path):
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L6**

```python
    path = tmp_path / "SKILL.md"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L7**

```python
    path.write_text(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L8**

```python
        "---\nname: refund policy\nagents: billing\nkeywords: 退款，账单\n---\n# Policy\n第一版待审核。",
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L9**

```python
        encoding="utf-8",
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L10**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L11**

```python
    manager = SkillManager(str(tmp_path))
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L12**

```python
    manager.load()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L13**

```python
    assert "第一版" in manager.prompt_for("退款", "billing")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L14**

```python
    assert not manager.prompt_for("退款", "technical")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L15**

```python
    path.write_text(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L16**

```python
        path.read_text(encoding="utf-8").replace("第一版", "第二版"), encoding="utf-8"
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L17**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L18**

```python
    manager.reload()
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L19**

```python
    assert "第二版" in manager.prompt_for("账单", "billing")
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L22 · test_intent_cache_uses_full_message_and_history

结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。

**L22**

```python
def test_intent_cache_uses_full_message_and_history():
```

定义此函数的参数与入口；下面的小节说明它在全链路中的职责。

**L23**

```python
    recognizer = IntentRecognizer("test")
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L24**

```python
    assert recognizer._cache_key("a" * 200 + "订单") != recognizer._cache_key(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L25**

```python
        "a" * 200 + "退款"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L26**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L27**

```python
    assert recognizer._cache_key(
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L28**

```python
        "same", [{"role": "user", "content": "b" * 160 + "订单"}]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L29**

```python
    ) != recognizer._cache_key(
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L30**

```python
        "same", [{"role": "user", "content": "b" * 160 + "退款"}]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L31**

```python
    )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L32**

```python
    assert recognizer._extract_entities("订单编号是 ORD1001，登录401")["order_id"] == [
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L33**

```python
        "ORD1001"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L34**

```python
    ]
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L35**

```python
    assert recognizer._extract_entities("订单编号是 ORD1001，登录401")[
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L36**

```python
        "error_code"
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L37**

```python
    ] == ["401"]
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

## 结合全项目看：边界与增强

增加真实供应商、并发进程、故障恢复和独立业务标签验证。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
