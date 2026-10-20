# 简历：AI 应用开发 / Go 后端方向

面向「AI 应用开发」「大模型应用后端」「Go 后端 / 全栈偏后端」岗位。旧版写法突出 Agent 编排和意图识别，这版的重点是：模型能力怎样被一个可靠、可计量、可运维的后端用起来。每条都能在仓库里找到实现和测试，对照见文末。

## 项目名与技术栈

```text
supportFlow 智能客服平台（Go 业务后端 + LLM 应用）
技术栈：Go / net/http / SQLite / SSE / Prometheus / Python FastAPI / ChromaDB / Redis / OpenAI 兼容 API（GLM-4.5-Air）/ Docker Compose / GitHub Actions / 原生 JavaScript
```

## 完整版（7 条，按需删减）

```text
- 设计 Go + Python 双服务架构：Go 作为唯一对外入口，负责多租户鉴权与 RBAC、订单/退款/工单事务和 LLM 网关；
  Python 只承载 Agent 编排与 RAG，经「服务密钥 + 操作白名单」的内部 RPC 读写业务数据，模型故障时业务接口不受影响。
- 用 Go 实现 OpenAI 兼容的 LLM 网关：SSE 流式解析、多供应商优先级路由、指数退避重试、首字超时、三态熔断器；
  明确「首个 token 前可重试/切换供应商，开始输出后不再切换」的边界，避免流式回复重复或前后矛盾。
- 开发客服 Copilot：按 token 预算截断会话上下文，Prompt 模板按内容哈希自动版本化并加入注入防护，SSE 逐字推送建议回复；
  交接摘要采用 JSON 结构化输出 + Go 端字段/枚举校验，不合格时带上校验错误自动修复一次。
- 设计租户级 AI 成本治理：令牌桶限流 + 每日 token 预算「预占-结算」，50 路并发测试无超支；
  每次调用落库供应商、模型、Prompt 版本、tokens、首字与总耗时，提供 P50/P95 报表与 Prometheus 直方图。
- 实现结果缓存（LRU + TTL），缓存键覆盖租户、Prompt 版本、模型路由链和完整上下文，只缓存校验通过的完整结果，
  会话更新或 Prompt/模型变更时自动失效，缓存命中同样计量，命中率可统计。
- 基于 SQLite 实现持久化知识入库队列：提交即返回 202，worker pool 以条件更新领取租约，长文档按段落分片并逐片 checkpoint，
  指数退避 + 抖动重试，失败进入死信并支持人工重试，内容哈希幂等去重；worker 以提交人身份签发短期令牌调用 AI 服务，用后立即撤销。
- 保障业务一致性：订单状态机 + 乐观锁版本号，退款申请/审批/结算幂等并占用可退余额，AI 转人工会话租约，
  业务变更与事件同事务写入并通过 SSE 断点续传；40 个 Go 单测通过 -race，CI 拉起真实 Go + Python 进程跑端到端验收。
```

## 精简版（5 条）

```text
- Go + Python 双服务：Go 负责鉴权/RBAC、订单退款工单事务与 LLM 网关，Python 负责 Agent 与 RAG，经带白名单的内部 RPC 通信。
- Go LLM 网关：OpenAI 兼容 SSE 流式、多供应商故障转移、首字超时、熔断器，首 token 前可切换、出字后不切换。
- 客服 Copilot：SSE 流式建议回复、JSON 结构化摘要校验与自动修复、Prompt 内容哈希版本化、上下文 token 预算截断。
- AI 成本治理：租户令牌桶限流 + token 预算预占/结算、调用级计量（tokens/首字/P95）、LRU+TTL 缓存与命中率统计。
- 异步知识入库：持久化队列 + worker pool 租约、分片 checkpoint 续传、指数退避重试、死信与幂等去重。
```

## 偏全栈的补充条

岗位写了「全栈」时，把下面一条替换进去：

```text
- 前端（原生 JS）实现客服工作台「AI 助手」面板，用 fetch + ReadableStream 解析 SSE 逐字渲染建议回复，
  并开发「AI 运营」看板展示调用量、tokens、缓存命中率、P50/P95 耗时、模型路由熔断状态和入库任务进度。
```

## 可选：保留 Agent 方向的量化结果

原 Python 版有历史评测，想保留一条 AI 能力的量化可以用下面这条，但要说清口径：2026-09 的开发回归，不是生产数据，见 `docs/RESUME_ALIGNMENT.md`。

```text
- 在 600 条参数化客服任务上，多 Agent 协作方案任务完成率 88.0%，单 Agent 为 67.7%（GLM-4.5-Air，开发回归口径）。
```

## 30 秒介绍

> supportFlow 是一个智能客服平台，我主要做后端：Go 负责业务事务，也负责把大模型接进来。这部分我解决了四个问题。第一是可靠性：LLM 网关支持多供应商故障转移、首字超时和熔断，流式场景下只在首个 token 前切换。第二是成本：租户级限流和 token 预算预占、结算，加上逐次计量和缓存。第三是输出可控：Prompt 版本化，摘要用 JSON 结构化输出并在 Go 端校验和修复。第四是数据进来的链路：知识入库做成持久化异步队列，带分片续传、重试和死信。业务侧有订单状态机、退款幂等和 AI 转人工，用 SSE 做实时推送。

## 高频追问

**为什么流式开始后不做故障转移？** 已推给用户的文字收不回来。换模型重新生成，内容会重复或者矛盾。所以只在首 token 前重试或切换；中途断开就返回 `llm_interrupted`，前端保留已显示的部分并提示重试。

**token 预算怎么防并发超支？** 先预占「估算 prompt + max_tokens」，结束后按真实 usage 结算并释放预占。检查和预占在同一把锁里完成，所以并发请求看到的是「已用 + 已预占」。这和退款占用可退余额是同一个模式。

**多实例部署怎么办？** 现在是单 Go 实例，限流、预算、缓存都在进程内。多副本时改成 Redis：`INCRBY` 加 Lua 脚本原子检查预算，令牌桶用 Lua 实现，缓存放 Redis。入库队列改为 PostgreSQL `FOR UPDATE SKIP LOCKED` 或者 MQ。

**怎么知道新 Prompt 好不好？** 每条调用记录都带 `prompt_version`，可以按版本对比 tokens、耗时和失败率。效果评测沿用 Python 侧的离线评测集；线上可以按租户或比例灰度两个版本。

**SSE 和 WebSocket 怎么选？** 生成回复是服务端单向推送，SSE 基于普通 HTTP，过网关和代理更简单，也能断点续传。业务事件流用的同样是 SSE 加持久化事件 ID。前端用 fetch 而不是 EventSource，因为令牌要放在请求头里，不能出现在 URL 中。

**模型没返回 usage 怎么计量？** 按中文 1 字约 1 token、其他字符约 4 字符 1 token 估算，并在记录里打 `estimated` 标记，报表可以区分真实值和估算值。

## 表述边界

- 可以说：设计并实现、单测/端到端/浏览器验证通过、并发测试无超支。
- 不要说：线上 QPS、真实用户量、生产 P95、节省 xx% 成本。目前的延迟数字都来自离线 fixture，不代表真实模型。拿真实模型压测后，用 `/usage` 的 P95 和缓存命中率替换。
- 配额和缓存是单实例内存实现，被问到时主动说明多实例方案。

## 简历条目与代码对照

| 条目 | 代码 | 测试 |
| --- | --- | --- |
| LLM 网关 | `backend/internal/llm/router.go`、`openai.go`、`breaker.go` | `internal/llm/llm_test.go` |
| Copilot / 结构化输出 | `backend/internal/copilot/copilot.go`、`prompts/` | `internal/copilot/copilot_test.go` |
| 限流与预算 | `backend/internal/quota/quota.go` | `internal/quota/quota_test.go` |
| 计量与报表 | `backend/internal/store/usage.go` | `internal/app/ai_test.go` |
| 异步入库 | `backend/internal/ingest/ingest.go`、`store/ingest.go` | `internal/ingest/ingest_test.go` |
| SSE 接口 | `backend/internal/app/ai.go` | `internal/app/ai_test.go`、`scripts/verify_product.py` |
| 前端 | `frontend/desk.js` | 浏览器手动验证 |
| 业务一致性 | `backend/internal/store/business.go`、`conversations.go` | `internal/store/store_test.go` |
