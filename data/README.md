# 演示数据

这里提交的是合成数据与格式样例，不包含真实用户记录、访问令牌或本地运行数据库。

## 新版 SupportFlow

`demo_supportflow/` 对应当前 `api.main:app`：

| 文件 | 对应接口或用途 |
|---|---|
| `chat.request.json` | `POST /chat` 的请求体；身份通过 Authorization 请求头传递 |
| `knowledge.request.json` | 管理员调用 `POST /knowledge` 的单条知识文档 |
| `refund.request.json` | 客户调用 `POST /refunds`，金额单位为整数分 |
| `order.response.json` | 初始化后 `GET /orders/ORD1001` 的响应形状 |
| `evaluation.sample.json` | 全链路评测输入；含环境夹具及预期结果，不可整体发送给聊天接口 |

样例与初始化脚本使用同一演示租户 `demo`、客户 `alice` 和订单 `ORD1001`，订单总额 5000 分。`conv_id` 是可选会话标识，后续消息应使用首次聊天返回的值。重试同一业务操作时复用原 `request_id` 或 `idempotency_key`，发起新操作时使用新值。

安装依赖后，在项目根目录运行：

```sh
python scripts/demo_business_flow.py
```

该脚本用临时数据库执行真实 HTTP 业务路由，包括订单查询、知识导入、退款申请、财务审批和沙箱结算。它不调用模型、不连接支付商、不修改已有账本；通过不代表模型效果已验证。

要建立供应用使用的演示账本，复制 `.env.supportflow.example` 为 `.env`，设置 `SF_STORAGE=sqlite` 后运行：

```sh
python scripts/bootstrap_supportflow.py
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```

初始化脚本创建客户、客服、财务和管理员身份，订单，以及内置知识。令牌仅写入本机 `.runtime/demo-tokens.json`，默认一小时过期，重新初始化可获得新令牌。聊天功能还需要配置可用的模型服务，详见 [交接说明](../docs/PROJECT_HANDOFF.md)。

## 旧版样例

`demo_docs/` 为旧版 JSON 知识导入和 Markdown 文档示例；其中业务叙述仅作合成演示，不是产品认证、真实服务承诺或新版 API 契约。新版知识导入使用 `demo_supportflow/knowledge.request.json`。

## 完整评测数据

`evaluation/datasets/` 保留项目自建的合成业务用例和数据卡。公开 Bitext 原始 CSV 与本地模型不放进 Git；来源、固定版本及获取方式见 `scripts/prepare_public_intents.py`、`scripts/prepare_local_model.py` 和对应数据卡。

原数据库、Chroma 向量索引、模型和日志均可留在本机，不需要为上传删除。新环境通过初始化和知识导入重新建立数据。
