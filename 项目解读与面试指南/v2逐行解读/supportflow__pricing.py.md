# supportflow\pricing.py

## 输入输出流

配置与单次调用输入/输出 token 进入计价函数；输出本次未扣缓存优惠的价目表估算或 None。

## 先理解设计

GLM-Air 价格同时受单次输入和输出长度影响，因此必须先逐次计价再汇总。版本化 profile 将估算依据固定下来。

源码 SHA256：`ebe3dc90284a4b88884cc88f1301ae645db70878a8acfe8ef2ba48df4891f0cb`。下面的行号属于这一快照。
## 逐行阅读

简单语法简述；重要业务操作在所在函数入口与对应调用行解释。

**L1**

```python
"""Versioned, uncached list-price estimates; never a provider billing statement.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L3**

```python
Source https://bigmodel.cn/pricing, checked 2026-09-08. GLM-4.5-Air has
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L4**

```python
per-call input AND output length tiers. Cache discounts and account credits are excluded.
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L5**

```python
"""
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

### L8 · estimate_call

使用单次调用长度选择版本化费率；未配置单价返回 None，不把未知费用写成零。

**L8**

```python
def estimate_call(settings, input_tokens, output_tokens):
```

使用单次调用长度选择版本化费率；未配置单价返回 None，不把未知费用写成零。

**L9**

```python
    if settings.pricing_profile == "glm-air-20260908":
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L10**

```python
        if input_tokens >= 128000:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L11**

```python
            return None
```

结束当前函数并把本行构造的结果交给调用方。

**L12**

```python
        inp, out = (
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L13**

```python
            (1.2, 8.0)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L14**

```python
            if input_tokens >= 32000
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L15**

```python
            else (0.8, 2.0 if output_tokens < 200 else 6.0)
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L16**

```python
        )
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L17**

```python
    elif (
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L18**

```python
        settings.model_input_price is not None
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L19**

```python
        and settings.model_output_price is not None
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L20**

```python
    ):
```

上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。

**L21**

```python
        inp, out = settings.model_input_price, settings.model_output_price
```

保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。

**L22**

```python
    else:
```

按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。

**L23**

```python
        return None
```

结束当前函数并把本行构造的结果交给调用方。

**L24**

```python
    return (input_tokens * inp + output_tokens * out) / 1e6
```

结束当前函数并把本行构造的结果交给调用方。

## 结合全项目看：边界与增强

价目表不是账户账单；缓存命中、套餐、赠额与后续调价需要与供应商账单校准。

文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。
