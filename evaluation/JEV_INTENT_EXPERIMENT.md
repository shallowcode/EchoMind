# Jev 1.13 / GLM-4.5-Air 意图识别实验

只比较项目的意图识别部分，不启动客服 HTTP 服务，不执行订单、退款或工单工具，不改动生产路由。

## 环境与复现

Windows，Python 3.14.6；本次隔离环境为 `.runtime/jev-eval-venv`。

```powershell
.venv-supportflow/Scripts/python.exe -m venv .runtime/jev-eval-venv
.runtime/jev-eval-venv/Scripts/python.exe -m pip install -r evaluation/jev-intent-requirements.txt
.runtime/jev-eval-venv/Scripts/python.exe -m pytest tests/test_jev_intent_benchmark.py -q --basetemp=.runtime/jev-eval/tests-new
.runtime/jev-eval-venv/Scripts/python.exe evaluation/jev_intent_benchmark.py --prepare
.runtime/jev-eval-venv/Scripts/python.exe evaluation/jev_intent_benchmark.py
```

配置：原方案读取 `.runtime/glm.env` 的 `SF_MODEL_*`；候选方案读取 `.runtime/jev.env` 的 `OPENROUTER_API_KEY`。密钥不写入输出、源码和 Git。复现数据还需要项目已有的 `.runtime/datasets/bitext-v2/validation.json`，可用 `scripts/prepare_public_intents.py` 从固定版本 Bitext 源数据生成。

输出目录 `.runtime/jev-eval/run-20260920` 保存数据、环境、依赖锁、源码快照、每次请求、模型响应、预测、预算台账和报告。同一目录再次运行会跳过已有结果；若某次请求只有预算记录而无结果，会停止，避免自动重复扣费。源码发生变化也拒绝混入旧实验。`--max-calls 2` 可做两次真实请求的接口检查，接口检查样本保留在最终指标和费用中。

预算是同一输出目录内所有调用合计；新建输出目录会开启新的预算台账，不能靠更换目录规避本次授权的 0.5 美元总额。

## 比较口径

- 48 条固定样本：中文 24 条，英文 24 条；退款、发票、订单状态、转人工各 12 条。
- 英文按固定随机种子从现有 Bitext validation 分区抽取，保留原始行号、标签映射、来源和许可；中文为运行前编写的合成样本，未经独立人工复核。
- 两方都从项目的全部 19 类中选择。预期标签只用于本地评分，不放进请求。
- GLM 复用原 `IntentRecognizer._llm_recognize()` 和 `supportflow.Model`，原提示词、原解析逻辑、temperature=0、max_tokens=256、thinking=disabled。
- Jev 保留原方案的例子、最近对话位置、细粒度类别偏好，改用原生 Choice 接口；只去掉要求生成 JSON 解释文字的指令。
- 主指标针对模型语义分类分支。另记录保留原规则融合后的诊断结果；Jev 分支使用获选类别概率参与融合，不把它的 confidence 直接视为 GLM 自报置信度。两种分数未经校准，因此融合结果不能当作完成调优后的结论。
- 串行请求，逐样本交替先调用 GLM/Jev；每样本每模型一次，无预热、重试、其他模型回退、付费裁判或测试后改提示词。
- 指标包括总体及分语言准确率、四个目标类别的 Macro-F1、失败率、中位延迟、nearest-rank P95、混淆表、配对 bootstrap 区间及精确 McNemar 检验。
- GLM 直连智谱，Jev 经 OpenRouter；本机测得的延迟包含网络和路由差异，不能解释为纯模型推理速度。

## 预算与费用

授权总预算 0.5 美元；脚本上限 0.45 美元，保留 0.05 美元余量。发送前持久化保守预留，超时或缺失 usage 时保留全部预留，绝不按零费用处理。GLM 按夸大的美元费率（输入 1.2、输出 8 / 百万 token）占用预算，以避免人民币换算和价格小幅变化造成超支；这不是实际账单。

Jev 使用 OpenRouter `usage.cost` 记录美元费用，同时按输入 $0.042 / 百万 token 核对。GLM 用真实 token usage 和仓库 2026-09-08 保存的人民币价格表估算，缓存折扣不计；网页价格页本次无法静态核验，最终以平台账单为准。报告分别列美元和人民币，不将二者直接相加作为实际费用。

## 接口依据

- [OpenRouter Jev 1.13 模型页](https://openrouter.ai/typesafe/jev-1.13/)
- [OpenRouter 官方 OpenAPI](https://openrouter.ai/openapi.json)：`POST /api/alpha/decisions`；不是 Chat Completions。
- [TypeSafe Choice](https://docs.typesafe.ai/primitives/choice)
- [TypeSafe 已知限制](https://docs.typesafe.ai/model-jaggedness/jev-1.13)
- [智谱价格页](https://bigmodel.cn/pricing)

这是小样本探索实验，不能据此宣布中文客服全面优于原模型、生产 SLA 提升或退款流程已经通过验收。
