# 简历与当前实现对照

核对日期：2026-10-10。依据《张天宇2.0.pdf》，只核对 SupportFlow 项目；简历中的其他经历不属于本仓库。

核心功能能够对应，但原先 ChromaDB 使用嵌入式模式、Redis 可选，后续产品入口加入 Go。现补充独立 Python/FastAPI 简历入口、独立 ChromaDB 服务、必需 Redis 和数据恢复工具。SQLite 承载业务事务、完整消息及幂等记录，Redis 承载工作上下文，Chroma 承载向量索引。更换部署方式不会使历史成绩变成当前版本成绩。

| 简历条目 | 实现与核对结果 |
|---|---|
| 显式拆分、并行协作、上下文隔离、结果共享、有限补做 | `supportflow/planning.py`、`service.py`、`agents/agent_orchestrator.py`；已有实现，测试覆盖并行时间及角色输入隔离 |
| 查询改写、并行召回、LLM 重排、记忆、Skills 热更新 | `knowledge.py`、`service.py`、`working_memory.py`、`core/skill_loader.py`；Chroma HTTP/嵌入式可选，Redis 保存最近 20 条消息、摘要和画像快照，TTL 24 小时。画像维护目前包含语言与答复长度偏好，不能描述为完整客户画像系统 |
| MCP、退款、人工工单、隔离、权限、事务、幂等、熔断 | `protocol.py`、`tools.py`、`store.py`；已有实现。退款依次申请、审批、沙箱结算；工单解决后回写会话。沙箱不发生真实资金转移 |
| GLM-4.5-Air / 1,200 条 / 20 类 | 历史复核汇总存在；公开数据已恢复，开发分区前 1,200 条可映射样本为 20 类、每类 60 条，符合原哈希。恢复数据不包含历史模型预测 |
| 600 条 / 150 条复合 / 完成率 / P95 | 600 条开发任务来自 24 个模板族，150 条复合任务来自 6 族。复核汇总支持简历数字，但本机缺少完整逐例归档，尚未用当前版本重跑 |

## 简历版本启动

在 `EchoMind` 目录执行，先复制配置并填写模型密钥和 Redis 密码，Redis URL 中的密码也要对应修改。容器配置拼接 Redis URL，建议使用随机十六进制密码，避免 URL 保留字符。

```powershell
Copy-Item .env.resume.example .env.resume
.venv-supportflow/Scripts/python.exe -m pip install -r requirements-dev.txt
docker compose --env-file .env.resume -f compose.supportflow.yml up -d redis chromadb
.venv-supportflow/Scripts/python.exe scripts/start_resume.py
```

入口 `http://localhost:8000/`，API 文档 `/docs`，存活检查 `/health`，依赖就绪检查 `/ready`。令牌写入 `.runtime/resume-demo-tokens.json`。默认 Chroma 为 `localhost:8001`，Redis 为 `localhost:6379`。应用也放进容器时执行：

```powershell
docker compose --env-file .env.resume -f compose.supportflow.yml up -d --build
```

此入口要求 Chroma/Redis 可达，缺失时启动失败，不会悄悄改为词法检索。`--fixture` 只替换模型，仍要求真实存储；不能用于测量模型准确率。Go 产品扩展仍通过 `scripts/start_product.py` 运行。

Redis 键包含租户、用户、会话。读取前校验 SQL 所有权、轮次和消息内容，人工回写会使旧缓存失效。过期、损坏或中断时用 SQL 恢复，故障进入 trace。这是带持久化后备的工作记忆，不能描述为 Redis 独占所有会话数据。`trace.memory` 显示命中、失效、故障及写入情况。

独立 Chroma 使用 `SF_CHROMA_MODE=http`、`SF_CHROMA_HOST`、`SF_CHROMA_PORT`、`SF_CHROMA_SSL`。初始化时从已有 SQL 知识切片重建租户索引，换电脑或换服务器不需要旧向量目录。轻量测试可显式选择 `SF_STORAGE=sqlite`，其检索为词法检索。

## 数据与指标证据

```powershell
.venv-supportflow/Scripts/python.exe scripts/prepare_public_intents.py --download
.venv-supportflow/Scripts/python.exe scripts/audit_resume.py
```

公开源 CSV SHA256 为 `6f81102b0100b97b8468eb04368033a23206bf1fde9d53500d5806ec1001a434`。原始与派生数据位于 `.runtime/datasets/`，不提交到 Git。来源、许可、固定修订见 `evaluation/datasets/trial-v3/public-manifest.json`。业务与公开数据六个分区均通过原清单哈希核对；`.gitattributes` 固定冻结文件 LF 换行，避免 Windows 检出改变哈希。

历史证据：`评测结果/GLM-1200复核/README.md`、`audit.json`。

| 历史口径 | single | multi |
|---|---:|---:|
| 600 条开发任务，复核后 | 406/600 = 67.67% | 528/600 = 88.00% |
| 150 条复合子集，复核后 | 85/150 = 56.67% | 125/150 = 83.33% |
| 整体 HTTP 请求 P95 | 8.45 秒 | 12.78 秒 |

公开意图历史准确率为 766/1,200 = 63.83%。固定 11 个映射类别的宏 F1 为 0.6786；实际出现 10 类，缺少 `order_status`，不能与仅计算出现类别的 0.7465 混写。复核修正了一条用例的订单号误触发 401 检查，两个方案各增加一条完成任务；原自动评分为 405/600、527/600。

这是 2026-09-09 的开发回归结果：任务并发 2，部分时段同时运行一条意图流，使用 ASGI 进程内 HTTP。参数化任务不是独立真实客户场景，未执行验证/验收评测，不是生产 SLA。当前机器缺少 `artifacts/glm-full-20260909/report.json`、`records/` 和完整冻结 `source/`；需要从另一台电脑带回此目录，才能逐例重核。`audit_resume.py` 明确列出缺失记录，没有生成替代预测或新模型成绩。

简历项目日期为 2026.03—2026.05，现存评测证据日期为 2026.09。如果早期项目在 3—5 月完成、9 月补测，应按实际经历区分说明；现有文件不能证明这些数字在 5 月前已取得。

## 本次验证范围

- Python 回归测试：129 项通过。包括 Redis 命中、隔离、TTL、人工回写失效、故障降级和幂等回复，以及 Chroma 后端选择和索引恢复。
- 真实 Chroma 嵌入式与独立 HTTP 服务：租户隔离、文档替换、索引重建、摘要召回、画像写入通过；临时 HTTP 服务结束后已停止。
- 六个数据分区哈希核对、公开来源和近重复过滤离线审计通过。
- Compose 配置解析通过。本机 Docker daemon 未启动，未运行完整容器联调；Redis 行为测试使用 fakeredis，尚未在本机验证真实 Redis 与模型全链路。GLM 完成率与 P95 未重新测量。
