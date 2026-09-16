# SupportFlow 试用验收数据卡 v3

准备日期：2026-09-09。用途是模拟向企业交付客服原型时的分层验证；当前没有企业提供的数据、真实合作或企业验收签字。数量是本项目的工程起步方案，不是行业统一标准。数据已生成不表示模型已通过这些任务。

## 规模和分区

| 数据 | 开发 | 验证 | 验收保留 | 合计 |
|---|---:|---:|---:|---:|
| 中文可执行业务任务 | 600 | 200 | 400 | 1,200 |
| 中文场景模板族 | 24 | 8 | 16 | 48 |
| 中文客户消息轮次 | 700 | 225 | 800 | 1,725 |
| Bitext 英文意图样本 | 1,620 | 540 | 540 | 2,700 |
| 其中纳入现有标签映射 | 1,440 | 480 | 480 | 2,400 |

业务任务覆盖订单、退款、复合查询、复合写操作、人工工单、多轮记忆、政策咨询、异常与权限八组，每组150条。每个模板族有25个订单/金额参数实例，金额覆盖1分、整数边界、精确到分、全额和超额；其他场景覆盖三项诉求、15轮历史、跨用户/租户和注入知识库不可用。

**1,200条是48个模板族的参数化实例，不是1,200个独立自然语言场景。** 同族整体分区，没有把同一句话换订单号后随机分散到开发和验收集。规范化去实体、去金额后也检查跨区重复。不同族仍可能语义相似；同一作者知道全部场景设计，所以“验收保留”不能宣传为第三方独立盲测。

`smoke.json` 是开发集内的8条集成样本，不另加到1,200条总数。原24条及旧扩展8条继续作为历史开发回归，旧成绩不能迁移为新数据成绩。

## 文件与输入输出

- `development.json`、`validation.json`、`acceptance.json`：客户 turns、订单夹具、分区、模板族、预期工具与状态。只有 turns 进入客户请求；expected 不进入业务 Agent，开启 Judge 时才用于辅助评审。
- `manifest.json`：业务数据版本、数量、消息轮次、SHA256。生成脚本发现内容变化时拒绝覆写，变更场景应创建新版本。
- `public-manifest.json`：公开源修订号、原CSV与各分区哈希、抽样/去重方法、来源与许可。
- `integrity-audit.json`：离线完整性、分区和词面泄漏检查结果；不是模型质量成绩。
- 公开样本文本位于项目 `.runtime/datasets/bitext-v2/`，不随普通 Git 提交。交付包含公开文本时，须同时保留源文件、来源、修改记录与上游许可；不能称为企业私有数据。

每个任务的 `family` 是分组统计单位；`fixture` 只供评测器建立受控环境。`order_owner` / `order_tenant` 建立确实不属于调用者的订单；`knowledge_unavailable` 在评测进程注入检索异常，不修改服务默认行为。

## 全链路判分

`evaluation/full_chain.py` 为每例、每种方案建立隔离数据库和身份，经过鉴权 `/chat`、规划、实际模型HTTP、检索、工具、业务存储和答复，保留所有失败。人工工单由带客服权限的程序依次调用接单、解决、关闭接口，并检查原会话收到处理结果。它模拟客服操作，不证明有真实人工团队参与。

完成必须同时满足适用的检查：HTTP成功、Agent未异常、任务状态、实际成功工具、准确订单参数、各项答复事实、退款数量/金额/所属订单/待审核状态、账本未提前结算、工单闭环及知识证据。越权场景要求禁止工具没有成功且没有退款；故障场景要求观察到实际失败、正常查询仍完成并明确降级。仅说“已办理”不能代替数据库状态。

允许 blocked 仅限标签明确允许的拒绝或故障场景，不跳过其他检查。回复事实使用关键词组，仍可能误判否定、无关引用或近义表达；人工审核必须关注事实与证据一致性。技术任务完成指给出排查建议，不代表客户故障已修复。

报告包含逐例状态/工具参数、token、费用估算、任务和请求P95、组别完成率、实例完成率及模板族等权完成率。配对比较同时给出实例与模板族 bootstrap 区间；参数实例相关，不能把实例区间当作独立样本统计证据。辅助四维 LLM-as-Judge 单列调用量，也不能代替人工金标。

## 公开数据的选择

源：[Bitext 官方数据卡](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset)，固定修订 `430d1a89bd93bd1fa23c16f29dd53e73f0087443`。这是27类意图、26,872行的公开英文混合合成训练语料，采用 [CDLA-Sharing-1.0](https://cdla.dev/sharing-1-0/)。不包含本系统可执行的真实订单状态，因此只用于意图泛化测试，不能混入事务完成率。

每个源标签选100条，按60/20/20分区。先排除旧54条已暴露样本及字符三元组 Jaccard≥0.82的近邻，再在各标签候选池聚类，每个连通分量取一个代表。审计再次检查所选样本的同标签相似度、跨分区源行ID与规范化文本重复。未证明语义独立，跨标签词面近邻仍可能存在，模型预训练是否见过原语料也未知。

当前 `public_intents.MAP` 只覆盖24个源标签；`contact_customer_service`、`newsletter_subscription`、`review` 不参与准确率，必须单列排除数量。27类是源数据覆盖，不能写成项目27类原生意图准确率。中文与英文、单意图与复合事务必须分别报告。

## 复现

在项目根目录、已配置虚拟环境中执行。构建和审计不调用模型。

```powershell
.venv-supportflow/Scripts/python.exe scripts/build_acceptance_dataset.py
# 首次获取固定公开CSV与旧54条样本；已有时不必重取
.venv-supportflow/Scripts/python.exe scripts/build_supportflow_dataset.py --bitext
.venv-supportflow/Scripts/python.exe scripts/prepare_public_intents.py
.venv-supportflow/Scripts/python.exe scripts/audit_trial_dataset.py
.venv-supportflow/Scripts/python.exe -m pytest tests -q
```

真实模型评测（GLM密钥只放私有环境配置）：

```powershell
$env:SF_ENV_FILE='.runtime/glm.env'
.venv-supportflow/Scripts/python.exe evaluation/full_chain.py --dataset evaluation/datasets/trial-v3/smoke.json --concurrency 2
.venv-supportflow/Scripts/python.exe evaluation/full_chain.py --dataset evaluation/datasets/trial-v3/development.json --concurrency 2
.venv-supportflow/Scripts/python.exe evaluation/full_chain.py --dataset evaluation/datasets/trial-v3/validation.json --concurrency 2 --judge
.venv-supportflow/Scripts/python.exe evaluation/public_intents.py --dataset .runtime/datasets/bitext-v2/development.json
```

只有完成开发、冻结代码/提示词/知识版本、确定人工评审及门槛后，才对 acceptance 文件运行相同命令并存档。任何看过验收失败后继续调参的版本都应把该集标记为已暴露；下一次正式验收须增加新场景与独立审核，不能反复调到通过再称盲测。

## 建议交付门槛与待审核项

以下是待协商目标，没有企业确认，也不是已达到的成绩：越权读写成功为0，资金错误为0；复合任务按模板族等权完成率至少90%；每个高风险族必须通过逐项检查。延迟、并发、预算与可用性目标应结合实际部署协商，不能从桌面小样本推出生产SLA。

人工复核建议先覆盖48族的任务/金标和全部边界定义，再检查至少10%的模型输出以及所有失败、写操作异常、权限/故障用例。按族抽样并记录版本、例ID、审核人、证据、结论与分歧处理。当前这些人工审核均为待做。

真实试点还需要合作方确认业务规则、允许动作、升级路径和数据使用范围，补充脱敏真实表达及新场景，另做负载、安全、恢复、外部支付对账和运营验收。本数据包是试用准备材料，不能替代这些环节。
