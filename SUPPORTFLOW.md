# SupportFlow：运行、业务闭环与实测

> **简历演示入口：** `python scripts/start_resume.py` 使用独立 FastAPI + ChromaDB + Redis，不需要 Go。配置和指标证据见 [简历与实现对照](docs/RESUME_ALIGNMENT.md)。下面的 Go 入口属于产品扩展；历史评测数字不能当作当前版本新成绩。

> 当前默认启动架构为 **Go 业务服务 + Python AI worker（v3）**。请优先阅读 [Go 产品版运行指南](docs/GO_PRODUCT.md)，运行 `python scripts/start_product.py`。`scripts/start_glm.py` 默认同样启动 v3。下面的单 Python 进程、旧账本路径与令牌文件说明适用于显式 `--legacy` 模式；AI 编排与评测说明仍可参考。

默认入口现在是 `api.main:app`，HTTP、MCP 和评测共享 `supportflow/` 中的业务层。旧 API 源码存为 `api/legacy_main.py.txt`，不会作为可运行入口导入。原 `mcp/` 两个文件是旧本地工具实现；新版 `mcp` Python 包名属于官方 SDK，新业务工具在 `supportflow/tools.py`，避免同名导入冲突。

## 本地启动

### 网页界面

启动服务后打开 `http://127.0.0.1:8002/`（GLM）或 `http://127.0.0.1:8000/`（本地模型）。前端与 API 由同一个服务提供，无需单独安装 Node 依赖。

客户端仅保留对话界面。本机沙箱启用 `SF_LOCAL_DEMO_ACCESS=true` 后，自动连接固定演示用户 alice，无需登录或导入凭证，过期自动续接。该用户可查询 demo 租户的全部未删除订单；对话中说「查询全部订单」即可查看列表。普通客户 API 凭证仍按原订单归属隔离。

界面支持多轮聊天、新建和切换会话、复制回复、订单查询、退款记录。失败请求沿用原请求 ID 重试。接口文档仍在 `/docs`。

每条新答复上方的「执行过程」与答复正文独立。展开后可看实际记录的上下文读取、意图识别、记忆召回、任务分派、工具成功/失败、检索词、重排状态与资料来源。记录在请求结束后返回，不是实时流，也不展示模型私有推理。旧会话未保存该字段时不补造执行记录。答复正文保留业务结果、待审核/失败状态与下一步，知识 ID 收到资料详情中。

`GET /health` 的 `runtime` 返回当前进程的应用版本、模型、思考开关、编排模式和启动时计算的源码摘要；页面右上角展示模型名，悬停可查看版本与摘要。摘要用于核对本地运行代码，不代表上游最新发布版本。

本次选用 **GLM-4.5-Air**。私有配置已保存在 Git 忽略的 `.runtime/glm.env`；模型密钥不写入代码和报告。启动这个配置：

```powershell
.venv-supportflow/Scripts/python.exe scripts/start_glm.py
.venv-supportflow/Scripts/python.exe scripts/chat_cli.py --url http://127.0.0.1:8002 --token-file .runtime/glm-demo-tokens.json
```

默认端口 8002，独立沙箱账本，避免混用之前的本地 Qwen 服务。下面的 Qwen 启动方式仍可用于离线实验。GLM 使用官方 `https://open.bigmodel.cn/api/paas/v4`、`thinking.type=disabled` 和 `json_object`；结构 schema 由提示词传入并由 Pydantic 校验，不能声称服务端强制 JSON Schema。配置加载支持 `SF_ENV_FILE`。

增强版 `multi` 会生成 `tasks` 清单，每项包含负责人、必需工具、观察结果、尝试次数、缺失项及状态。技术子任务只接收技术片段；原始请求保留在执行层核对退款授权。缺少证据时在同一个子任务内补做；成功结果通过请求级锁和共享结果复用。最终逐项渲染，不再经一次自由合并而遗漏已完成内容。任一任务失败返回 `partial`，模型或缓存故障可标记 `degraded`。

GLM 评测命令：

```powershell
$env:SF_ENV_FILE='.runtime/glm.env'
.venv-supportflow/Scripts/python.exe evaluation/full_chain.py --concurrency 2 --judge
.venv-supportflow/Scripts/python.exe evaluation/full_chain.py --dataset evaluation/datasets/compound-v1.json --baseline legacy_multi --concurrency 2 --judge
.venv-supportflow/Scripts/python.exe evaluation/full_chain.py --dataset evaluation/datasets/compound-v2.json --concurrency 2 --judge
```

`single` 为同模型通用 Agent 与单次检索基线；`legacy_multi` 保留旧路由并行与自由合并，使用同一版工具保护和模型适配，因此这是编排消融，而不是历史代码原样复现。v1 是已看过的开发回归集，v2 是开发后补写的扩展回归集；两者都不能称为独立盲测。

费用按每次调用的真实 token 与版本化价目表估算；GLM-Air 的输出长度会影响单价，不能直接用全任务 token 总量乘最低价。`trace.usage` 保留逐次估算；评审模型 token 单列。该金额未抵扣缓存优惠或账户赠额，不是实际账单。

推荐先在工作区执行以下 PowerShell 命令。本次已建立 `.venv-supportflow`，已下载两个官方 Qwen GGUF 和 llama.cpp CPU 可执行文件；这些大文件均被 Git 忽略。

```powershell
python -m venv .venv-supportflow
.venv-supportflow/Scripts/python.exe -m pip install -r requirements-dev.txt
.venv-supportflow/Scripts/python.exe scripts/prepare_local_model.py --size 1.7B
```

在独立终端启动模型（命令以项目根目录为当前目录）：

```powershell
.runtime/llama/llama-server.exe -m .runtime/Qwen3-1.7B-Q8_0.gguf --host 127.0.0.1 --port 8081 -c 16384 -np 2 -t 6 --jinja
```

然后启动应用：

```powershell
$env:SF_MODEL_NAME='Qwen3-1.7B-Q8_0'
$env:SF_STORAGE='chroma'
.venv-supportflow/Scripts/python.exe scripts/bootstrap_supportflow.py
.venv-supportflow/Scripts/python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

`bootstrap` 创建 demo 租户、alice/bob 客户、operator 客服、finance 财务、admin 管理员与 alice 的 ORD1001（5000 分）测试订单。token 写入 `.runtime/demo-tokens.json`，默认 1 小时到期；重复运行会生成新 token，不会重复创建订单。token 明文只在该本地文件保存，数据库只存 SHA256 摘要。生产身份接入方式需要最后确认，不在模型提示词中携带权限。

```powershell
$sfTokens=Get-Content .runtime/demo-tokens.json -Raw | ConvertFrom-Json
$sfHeaders=@{Authorization="Bearer $($sfTokens.alice)"}
$sfBody=@{message='请查询订单 ORD1001';request_id='demo-request-001'} | ConvertTo-Json
Invoke-RestMethod http://127.0.0.1:8000/chat -Method Post -Headers $sfHeaders -ContentType 'application/json; charset=utf-8' -Body ([Text.Encoding]::UTF8.GetBytes($sfBody))
```

相同 `request_id` 与相同请求体返回已保存的响应，`replayed=true`；相同 ID 换内容返回 409。后续轮次传入第一次返回的 `conv_id`。身份由 Bearer token 决定，客户端不能提交任意 `user_id` 或 `tenant`。

`.env.supportflow.example` 展示新版配置。应用读取 `.env` 的 `SF_*` 字段；旧 `ANTHROPIC_*` 字段不会触发隐式付费回退。`SF_STORAGE=sqlite` 是明确的轻量词法检索；只有 `chroma` 才是向量检索。Redis 是可选工作记忆缓存；SQL 会话日志与版本是权威数据，Redis 失效时可继续回复并标记降级。

## 业务操作与权限

一键本地启动：`.venv-supportflow/Scripts/python.exe scripts/start_local.py`。它自动复用或启动本地模型与沙箱应用，不会关闭已占用端口的其他服务。交互式客户端使用 `.venv-supportflow/Scripts/python.exe scripts/chat_cli.py`，同样走鉴权 HTTP 链路，支持 `/new`、`/retry`、`/quit`。

| 接口 | 身份/权限 | 结果 |
|---|---|---|
| `POST /chat`、`POST /intents` | 已登录用户 | 完整客服链路 / 单独意图识别 |
| `GET /conversations/{id}` | 会话本人 | 顺序会话记录，包括人工解决说明 |
| `GET /orders/{id}` | 本人或同租户客服/财务/管理员 | 真实沙箱订单账本 |
| `POST /refunds` | 订单本人 | 幂等创建 pending 退款并预留额度 |
| `GET /refunds` | 本人；财务可看同租户全部 | 退款进度 |
| `POST /refunds/{id}/approval` | 财务，不能审批自己申请 | approved / rejected |
| `POST /refunds/{id}/settle` | 财务，不能执行自己申请 | 默认沙箱入账；external 模式入待发送队列 |
| `POST /tickets` | 会话本人 | open 工单 |
| `GET /tickets` | 客服/管理员 | 同租户工单队列 |
| `GET /tickets/{id}` | 本人或同租户客服 | 工单状态 |
| `PATCH /tickets/{id}` | 客服，校验版本与受理人 | assigned → resolved → closed |
| `POST /knowledge` | 管理员 | 版本化知识替换 |
| `POST /skills/reload` | 管理员 | 从受管本地目录重载 SOP |
| `POST /auth/tokens`、`POST /auth/revoke` | 管理员 | 同租户授权、撤销 |
| `GET /audit` | 管理员 | 同租户业务审计 |
| `GET /metrics` | ops/管理员 | 实际 HTTP 请求计数和耗时直方图 |
| `POST /ops/payments/dispatch` | ops/管理员 | 显式发送外部退款待办 |
| `POST /ops/payments/reconcile` | ops/管理员 | 查询回调缺失退款，核验同一签名事件契约 |
| `POST /payments/events` | 验证时间戳及 HMAC 签名 | 外部退款最终状态核验、幂等入账 |
| `/mcp/` | 与 HTTP 相同的 Bearer token | 官方 SDK Streamable HTTP 协议 |

FastAPI `/docs` 提供严格请求体 schema。工单更新必须传当前 `version`；例如初始 open 的版本为 0，分配后版本为 1，解决时必须传 1。解决说明由后端写入原会话；聊天 Agent 无权冒充客服关闭工单。

退款金额统一使用整数分。pending、approved、processing 都占用可退余额，事务内检查余额，避免两个并发申请同时通过。LLM 只能申请，不能审批或支付；聊天退款参数还必须与用户明确提供的订单号、金额相符。

多轮退款会保留用户已明确的订单和金额；缺信息时返回 `awaiting_input`。例如「我要退款」→「ORD1001」→「全退给我」，最后一轮会按该订单当前可退余额提交待审核申请。「全退」对应工具参数 `full_refund=true`，不由模型填写金额；账本在同一事务中计算实付减已退及待审核/处理中占用的余额并预留。`full_refund` 与 `amount_cents` 只能二选一。换订单会清除旧订单的金额，取消或切换话题会结束待补充流程；询问“能全退吗”不会授权提交退款。已有旧会话中的“全退”只从用户自己的历史消息承接订单号。

## MCP 接入

使用官方 Python SDK 的 `streamable_http_client('http://127.0.0.1:8000/mcp/', http_client=authenticated_client)`，再创建 `ClientSession` 并 `initialize()`。服务暴露知识检索、订单查询、退款申请、工单创建和状态查询；未授权请求返回 401。

退款和工单工具要求调用方提供幂等键。MCP 调用时的身份重新从 token 存储校验，不能用工具参数跨租户。这里实现的是带 token 校验的 MCP 资源服务，不是一个企业 OIDC 身份提供商。HTTPS 反向代理地址用 `SF_PUBLIC_URL` 配置，SSO 与 IdP 需按目标环境接入。

## 商户后台

客服每条新回复的「执行过程」支持展开「记忆」「知识库」「最终送给模型的输入」。记忆显示读取的历史消息、摘要、偏好、召回结果及业务上下文；知识库显示各次检索与原文；模型输入按调用顺序保留发送给提供商的完整 JSON 请求体（系统提示、消息、参数及结构化输出约束），不记录认证请求头。旧回复没有采集过的输入不会补造。

本地运行后访问 `/admin`（GLM 启动脚本默认 http://127.0.0.1:8002/admin），也可从客服页面侧栏进入「商户后台」。GLM 本地启动脚本默认启用 `SF_LOCAL_DEMO_ACCESS=true`，后台自动进入 demo 租户的演示商户（订单管理与退款审批权限），令牌过期自动续接，无需导入凭证。该入口仅接受本机沙箱请求；普通部署默认关闭。客服页面也自动进入固定演示用户 alice；关闭本地演示模式时，后台仍支持手动连接商户凭证。

- 订单管理：查询、新增、删除订单，设置商品、数量、总额和初始状态；模拟支付、发货、完成或取消未支付订单。默认单用户模式新增订单统一归属 alice，不再填写客户账号。删除后不再出现在客服查询中，可从「已删除」筛选中恢复；退款处理中的订单须先完成或拒绝退款后再删除。
- 退款审批：查看客户申请，批准或拒绝，批准后点击「执行退款」更新沙箱账本。订单页分别展示履约状态、退款状态和可退金额。
- 客服追问退款进度时通过 `refund_status` 读取当前账本，沿用用户此前提供的订单号，返回真实申请编号、金额与审批/执行状态；批准待执行与退款完成分开显示，历史答复不作为当前状态。订单查询也返回关联退款记录。
- 客服支持按商品名称、简称或描述定位订单，无需先填写订单号。匹配唯一订单后读取当前状态；同商品多笔时列出候选，支持「第一笔／第二笔」选择；切换商品时重新匹配。只使用当前用户可访问、未删除的真实订单，无法匹配时追问，不虚构物流或到货时间。
- 后台新增订单后，客户端可直接在对话里查询或申请退款；已有的演示订单也对默认用户可见。数据保存在同一个数据库，刷新页面仍保留。

后台接口强制校验角色与租户；staff 管理订单，finance 审批退款，admin 可执行两类操作。不能审批自己提交的退款。新增订单及状态模拟仅允许沙箱模式，执行沙箱退款不发生真实资金转移。

## 外部支付适配边界

默认 `SF_BUSINESS_MODE=sandbox`，结算只更新测试账本，不发生真实资金转移。已实现的通用外部契约：

1. `SF_PAYMENT_URL` 必须是 HTTPS，并配置 API key 与 webhook secret。
2. 审批通过后建立 `payment_outbox`，退款变为 processing。发送 `POST {url}/refunds`，使用退款 ID 作为 `Idempotency-Key`。
3. 发送成功仅标记 accepted，不推断资金已到账；超时保持 processing 和额度预留，重试使用原键。
4. 对方回调 `POST /payments/events`；`X-Timestamp` 为 Unix 秒，`X-Signature=HMAC-SHA256(secret,timestamp + '.' + raw_body)`，最多接受前后 300 秒。
5. JSON 必須含 `event_id/refund_id/tenant/order_id/amount_cents/currency/status/payment_ref`。当前业务币种固定 CNY，与模型费用币种分离；校验订单、金额和最终状态后，事务内去重事件并记账。

这个适配器已通过模拟 HTTP、签名回调和回调丢失后的主动对账测试，尚未对接任何真实支付商。`reconcile` 查询 `{url}/refunds/{id}`，202 表示仍在处理；200 必须返回与回调相同的签名事件。供应商实际 API、回调/对账规范和凭证需最终确认，不能据此写“已经实现真实生产退款”。

## 可复现评测

```powershell
.venv-supportflow/Scripts/python.exe scripts/build_supportflow_dataset.py --bitext
$env:SF_MODEL_NAME='Qwen3-1.7B-Q8_0'
$env:SF_STORAGE='chroma'
# 仅本地模型的外部 API 费用为 0；不是机器总成本为 0。
$env:SF_MODEL_INPUT_PRICE='0'
$env:SF_MODEL_OUTPUT_PRICE='0'
.venv-supportflow/Scripts/python.exe evaluation/full_chain.py --concurrency 1 --judge
.venv-supportflow/Scripts/python.exe evaluation/public_intents.py
```

每次产生新的 `artifacts/<UTC时间>/`，包括完整报告、逐例响应、调用 trace、最终业务状态和隔离的 SQLite 数据库。测试用例标签不进入客服提示词。单 Agent 与多 Agent 使用相同模型、工具和权限；单 Agent 可用所有业务工具，只有编排方式、Agent SOP 范围和检索策略不同，所以这是组合方案对比，不能把全部差异归因于“并行”。

24 条自建任务包含 8 条复合任务、订单、退款、人工闭环、政策、多轮订单记忆及超额退款拒绝。它是开发回归集：前 2 条用于试跑，首次全量结果也已用于发现工程问题，因此后续复测不能称为盲测。公有 Bitext 另抽 54 条、27 类，明确映射其中 24 类，排除 3 类语义不清或范围不合适的标签，最终 48 条用于英文意图评测；不混入业务完成率。

完成率以任务为分母，失败和 HTTP 错误保留在分母；退款看数据库状态与金额，人工任务经 staff HTTP 操作后验证会话回写。P95 是 nearest-rank，分别报告 HTTP 请求与完整任务；ASGI 模式包括鉴权、服务、数据库和实际模型 HTTP 调用，不包括外部网络/反向代理。后台桌面负载与小样本会影响耗时，不能据此声称生产 SLA。

成本按真实 usage 和配置的每百万 token 单价计算，缺失单价或 usage 时报告 null。可另设 `SF_MACHINE_HOURLY_COST` 估算本地运行成本，但该估计尚未按共享机器利用率分摊。LLM-as-Judge 四维评分仅为辅助观测，同一小模型作评委有相关偏差，不能替代业务状态判定和人工复核。

```powershell
.venv-supportflow/Scripts/python.exe evaluation/compare_runs.py --baseline artifacts/<旧运行>/report.json --candidate artifacts/<新运行>/report.json
```

比较器校验数据集、传输、任务数、并发和检索后端，检测完成率下降、延迟/模型成本上升超过 5% 的相对退化；不覆盖旧基线，5% 也不等于统计显著。模型、提示词或服务代码改动后要生成新报告；运行过程中若参评代码发生变化，报告会记录 `source_changed_during_run=true`。

## 测试与容器

```powershell
.venv-supportflow/Scripts/python.exe -m pytest tests -q --basetemp=.runtime/test-new-unique-name
docker compose -f compose.supportflow.yml up --build -d
docker compose -f compose.supportflow.yml exec app python scripts/bootstrap_supportflow.py --output /app/data/demo-tokens.json
```

每次本地测试可使用不同 basetemp，避免 Windows 现有 Temp 目录权限问题。容器需先设置 `SF_REDIS_PASSWORD`；如果密码包含 URI 保留字符，需要对 `SF_REDIS_URL` 密码做 URL 编码。模型服务在宿主机上时，需允许 Docker 网络访问模型端口，或设置可达的模型 URL。此机器没有 Docker，容器配置只做静态检查，不冒充部署实测；Redis 测试使用 fakeredis，Chroma 与 MCP 则进行真实本地集成验证。

## 仍需最终确认的内容

2026-09-09 已新增 [v3试用数据卡](evaluation/datasets/trial-v3/README.md)：1,200条可执行业务参数实例、48个模板族，按600/200/400分区；另准备2,700条Bitext英文意图样本。数据来源、生成、泄漏检查、GLM执行命令和建议验收门槛均在数据卡中。完整技术解读见[第12章](项目解读与面试指南/12_企业试用验收数据方案.md)。数据准备不表示全量模型验收通过，验收保留集尚未运行。

GLM-4.5-Air 已按用户选择接入，费用按已记录价目表估算，实际账单需另行核对。仍待集成或验证：支付供应商及其回调/对账协议；企业 IdP/SSO；目标容器环境与真实客服流程；独立人工标注盲测集和目标并发。功能实现与测试证据已经可以复查，这些外部条件到位后才能验证对应生产质量。

来源：[Qwen 官方 1.7B 模型卡](https://huggingface.co/Qwen/Qwen3-1.7B-GGUF)、[MCP 官方 Python SDK v1](https://github.com/modelcontextprotocol/python-sdk/tree/v1.x)、[Bitext 数据集与许可](https://huggingface.co/datasets/bitext/Bitext-customer-support-llm-chatbot-training-dataset)。模型与数据集下载脚本固定 revision，并记录 SHA256。
## 能力工作台

打开 `/lab`，本机沙箱商户自动连接。客户页仍只保留对话，侧栏提供工作台入口。

- 复合任务：可创建独立的“演示耳机”订单，运行真实客服请求。执行过程记录各子任务起止时间、隔离输入、职责、工具证据、共享结果、补做原因与预算。订单查询直接渲染本轮工具结果，避免将旧记忆中的退款编号混入订单答复。
- 知识与记忆：聊天执行过程展示历史、摘要、画像、召回记忆、查询改写、各路召回耗时与候选、重排结果、实际 Skills 注入及完整模型请求。工作台可以查看知识库、按角色查看并编辑现有 Markdown Skills；保存后立即重载，版本冲突拒绝覆盖。
- 业务工具：商户后台管理订单与退款审批/结算；工作台处理人工工单，解决说明写回原会话。MCP 页使用真实 JSON-RPC 握手、列工具并调用 `order_list`。聊天链路直接调用共享服务，并不通过 MCP HTTP；两条入口共用权限、状态机和幂等实现。工具详情与工作台显示执行约束、熔断器状态和业务审计。
- 意图评测：读取 `artifacts/glm-full-20260909/records/public-*.json` 的 1,200 条真实归档，复算准确率、宏 F1、混淆矩阵，展示 20 个源意图的映射及可筛选误判样本。对应 2026-09-09 英文公开合成开发集，不能当作当前代码重跑结果或业务完成率；宏 F1 保留原报告的 11 类口径，包括无真实支持的 `order_status`。

工作台数据及 Skills 修改接口同时要求本机、沙箱模式、自定义请求头和 staff 权限，不向普通客户或外部部署开放。演示创建的订单及退款会保留在沙箱账本，供后台后续操作。
