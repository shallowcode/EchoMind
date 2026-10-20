# 项目结构与数据格式

> **2026-10-10 简历对照：** 独立 FastAPI 入口为 `scripts/start_resume.py`，使用真实 ChromaDB/Redis；Go 产品入口另见 `GO_PRODUCT.md`。公开意图数据已按固定版本恢复，本机仍缺历史全量逐例预测。详见 [简历与实现对照](RESUME_ALIGNMENT.md)。

此文档供首次接手本项目的开发者或 AI 阅读。当前可运行主线是 **SupportFlow v2**，历史 EchoMind 实现也保留在仓库中。请以代码、当前接口 schema 和测试为准，旧版 README 后续章节作为历史参考。

## 阅读顺序与业务结构

1. `api/main.py`：默认启动入口，调用 `supportflow.api.create_app()`。
2. `supportflow/api.py`、`contracts.py`：鉴权接口、严格请求模型、配置项。
3. `supportflow/service.py`、`planning.py`：客服请求、任务拆分及执行编排。
4. `agents/agent_orchestrator.py`、`core/`、`skills/`：Agent、意图识别、SOP；部分代码由新版复用。
5. `supportflow/tools.py`、`store.py`：业务工具及事务账本，包含订单、退款、工单和权限检查。
6. `supportflow/knowledge.py`、`model.py`：知识检索与模型适配。
7. `supportflow/protocol.py`、`payments.py`：MCP 接入及外部支付适配边界。
8. `tests/`、`evaluation/`：行为验证和模型全链路评测。

请求主线为：HTTP/MCP 身份校验 → 客服服务 → 意图/任务规划 → Agent 与工具 → 事务数据库及知识检索 → 回复与跟踪记录。

旧实现位于 `api/legacy_main.py.txt`、`mcp/`、`memory/`、`monitor/` 等位置。`api/legacy_main.py.txt` 是归档源码；不要把它当默认入口。新版 MCP 协议使用第三方 `mcp` SDK，业务实现位于 `supportflow/protocol.py`。更详细的设计说明见 `SUPPORTFLOW.md` 及 `项目解读与面试指南/`。

## 在新环境运行

在项目根目录创建 Python 环境并安装依赖：

```sh
python -m venv .venv
# 激活方式：Windows PowerShell 为 .venv/Scripts/Activate.ps1；Linux/macOS 为 source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python scripts/demo_business_flow.py
```

项目依赖曾在 Windows Python 3.14 验证；容器配置目标为 Python 3.12，具体平台兼容性以目标环境安装与测试结果为准。演示脚本无需模型或 API key，使用真实路由验证业务闭环，数据库在运行结束后清理。

启动交互服务时，将 `.env.supportflow.example` 复制为本机 `.env`，按需设置 `SF_*` 配置：

- `SF_STORAGE=sqlite`：轻量词法检索，无需预先创建数据库或下载向量模型；`chroma` 才是向量检索。
- `SF_MODEL_URL`、`SF_MODEL_NAME`、`SF_MODEL_KEY`：由你使用的模型服务提供。聊天与意图识别需要模型服务；订单及退款 HTTP 接口不依赖模型生成。
- `SF_LOCAL_CHAT_TEMPLATE`、`SF_SUPPORTS_JSON_SCHEMA`：按服务商实际支持能力配置；GLM 示例见模板注释及 `SUPPORTFLOW.md`。
- `SF_BUSINESS_MODE=sandbox`：本地演示账本，不发生真实支付。

```sh
python scripts/bootstrap_supportflow.py
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

打开 `http://127.0.0.1:8000/docs` 查看当前接口；`/openapi.json` 提供机器可读 schema。本地 Qwen 模型可通过 `scripts/prepare_local_model.py` 下载，服务启动命令见 `SUPPORTFLOW.md`。初始化 token 在本机 `.runtime/demo-tokens.json`，用 `Authorization: Bearer <token>` 传递，不写入样例或提交。

## 接口与 JSON 格式

请求使用 UTF-8 JSON。`supportflow/contracts.py` 和 `supportflow/api.py` 是接口字段、类型和约束的权威定义。`docs/api.openapi.json` 为交付时导出的 schema 快照；代码更新后应从运行服务重新导出。

| 数据 | 样例与规则 |
|---|---|
| 聊天请求 | `data/demo_supportflow/chat.request.json`；`message`、`request_id` 必填，`conv_id` 可选。身份来自 token，不能用请求体指定任意用户或租户 |
| 知识文档 | `knowledge.request.json`；单条 `id/title/content`，由管理员导入。服务切片并计算内容版本 |
| 订单响应 | `order.response.json`；`total/refunded` 单位均为整数分 |
| 退款请求 | `refund.request.json`；`amount_cents` 必须为正整数分，幂等键用于避免重复申请 |
| 工单 | 请求字段为 `conv_id/summary/idempotency_key`；更新含 `status/version`，按状态需要 `assignee/resolution` |
| 评测任务 | `evaluation.sample.json`；`cases` 含 `turns/order/expected`，`order` 是准备环境的数据，`expected` 只给评测器使用 |

聊天首轮返回会话标识，后续消息传相同 `conv_id`。同一请求重试需复用请求 ID 与原请求体；不同业务操作应使用新 ID。样例退款依赖初始化订单，退款后的订单响应会与初始样例不同。

## 数据库及持久化

`supportflow/store.py` 的 `Store` 在首次运行时自动建表。`docs/database.schema.sql` 为当前 SQLite 表结构快照，用于阅读；初始化以实际代码为准。

| 表/存储 | 内容 |
|---|---|
| `orders` | 租户、订单号、所属用户、总额、已退款额、状态 |
| `refunds` | 退款金额、状态、原因、幂等键、支付引用 |
| `tickets` | 会话关联、受理人、解决说明、状态和乐观锁版本 |
| `conversations/messages` | 会话所有权、版本/执行租约、顺序消息 |
| `tokens` | token 的 SHA256 摘要、身份、角色、过期与撤销状态 |
| `requests` | 幂等请求指纹和已保存响应 |
| `knowledge` | 知识切片、标题、正文及版本 |
| `audit/traces/profiles` | 业务审计、调用跟踪和用户画像 |
| `payment_outbox/payment_events` | 外部支付待发送记录和事件去重 |
| Chroma | 可选知识、情景记忆和画像检索索引，可重新生成 |
| Redis | 可选工作记忆缓存；SQL 会话记录仍是权威数据 |

业务币种当前固定为 CNY。订单、退款和工单实际状态来自账本；模型文字不等于已完成业务操作。演示退款经过客户申请、财务审批、沙箱结算，不允许客户自行审批。

## 数据来源及上传范围

仓库保留业务源码、依赖、容器配置、运行脚本、SOP、测试、项目解读、自建合成评测数据及演示样例。历史评测结果不是本次上传的重新实测结论。公开数据下载地址、固定修订和来源记录保留在脚本及数据卡中。

不提交 `.env`、访问令牌、运行数据库、向量索引、日志、模型权重、Python 环境和临时产物。新环境通过初始化脚本和知识导入重新建立数据，不需要旧数据库才能理解结构。真实业务接入时应自行提供授权数据和外部服务配置。
