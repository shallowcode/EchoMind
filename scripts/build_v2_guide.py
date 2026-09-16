"""Create line-addressable study snapshots for new v2 source without modifying runtime code."""

import ast
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "项目解读与面试指南/v2逐行解读"
NOTES = {
    "run_full_evaluation.py": (
        "私有GLM配置、固定业务三分区和公开意图三分区进入独立后台脚本；输出源码/数据快照、逐例原子JSON、status.json及最终REPORT.md/report.json。",
        "业务并发2、意图串行1；完成记录包含失败且不重跑。恢复时核对源码/数据/配置哈希，未落盘的任务用新沙箱重启；身份令牌提前刷新，不依赖Codex持续检查。",
        "运行全部分区意味着验收样本暴露；公共意图流会竞争模型额度与本机资源，P95不能直接与旧单独运行对比。暂不开Judge，重复付费仅可能发生在中断但尚未落盘的任务。",
    ),
    "test_full_batch.py": (
        "临时文件和合成结果进入测试；输出断点保留失败、错误分母、配置/源码冻结与族级配对统计断言。",
        "关注长跑恢复与可比性，拒绝源码改变后混入同一报告；不使用真实模型或消费验收响应。",
        "测试通过不证明网络全天稳定；后台状态、最终报告和逐例原始数据才是实际执行证据。",
    ),
    "build_acceptance_dataset.py": (
        "48个场景模板族与25组整数金额进入 build；输出600/200/400条按族隔离的任务、8条开发冒烟子集及冻结哈希清单。标签供评测器使用，不传给业务Agent。",
        "先按模板族分区，再展开订单与金额，避免同一话术换参数后跨区泄漏。write_frozen拒绝静默覆写不同内容。",
        "1200实例只有48个模板族；缺乏独立人工复核、真实表达和企业确认。增加参数数量不能代替自然语言多样性。",
    ),
    "prepare_public_intents.py": (
        "固定修订Bitext CSV及旧54条已暴露样本进入过滤器；输出2700条分层意图样本到.runtime，以及受版本控制的来源、许可、哈希清单。",
        "排除旧样本近邻，按源标签对候选池的字符三元组做连通分量聚类，每簇取代表后分区；24个源标签进入当前意图映射。",
        "词面去重不证明语义独立；公开训练语料可能与模型预训练重合。数据不是企业客服日志，也不能证明事务完成率。",
    ),
    "audit_trial_dataset.py": (
        "冻结业务数据、公开分区、清单与旧样本进入只读核对；输出integrity-audit.json，记录哈希、数量、分区和近重复检查。",
        "校验器独立重算选中公开样本的相似度与暴露排除，防止仅相信生成器自己的声明；全程不调用模型。",
        "自动完整性审计不等于金标语义正确或人工签字。异常断言停止流程，不能删去失败样本后宣称通过。",
    ),
    "test_trial_dataset.py": (
        "冻结数据与独立数据库/知识故障夹具进入pytest；输出数据隔离、金额标签、参数核验、错误订单、权限、故障和族级权重断言。",
        "反例验证判分不会被流畅文字、正确金额但错误订单、或同族大量复制所误导。测试不调用验收集模型响应。",
        "测试替身只能证明评测工程行为。自然语言同义表达、否定和跨句事实仍需人工审核。",
    ),
    "planning.py": (
        "原始用户消息、已提取实体和退款授权标志进入规则规划器；输出带负责人、工具门槛和状态的 Subtask 清单。工具观察与答复进入 gaps，输出待补项；任务清单进入 render_tasks，输出逐项完整答复。",
        "拆分决定谁负责什么，工具授权决定谁能做什么，证据门槛决定哪些事项可以标完成。技术请求片段从上下文中独立提取，最终不做可能遗漏事项的自由合并。",
        "当前是已支持客服领域的规则规划，不是任意任务 DAG。回复关键词门槛不是完整语义证明；复杂多订单指代、否定范围和跨任务依赖仍需扩大标注与测试。",
    ),
    "pricing.py": (
        "配置与单次调用输入/输出 token 进入计价函数；输出本次未扣缓存优惠的价目表估算或 None。",
        "GLM-Air 价格同时受单次输入和输出长度影响，因此必须先逐次计价再汇总。版本化 profile 将估算依据固定下来。",
        "价目表不是账户账单；缓存命中、套餐、赠额与后续调价需要与供应商账单校准。",
    ),
    "contracts.py": (
        "HTTP/环境变量与服务器生成的身份进入 schema；输出经过类型、长度和枚举限制的请求、配置及 trace。",
        "严格数据契约不等于授权；Principal.require 与 Store 的属主检查共同完成权限判断。",
        "企业 IdP、集中策略、配置启动检查仍应按目标部署继续增强。",
    ),
    "store.py": (
        "可信 Principal、业务参数和幂等键进入 SQL 事务；输出订单、退款、工单、会话状态和审计记录。",
        "SQL 是权威状态。退款额度检查与预留在同一事务内完成；会话提交把消息、状态、幂等响应一起保存。",
        "SQLite 串行写入、跨会话画像合并、数据保留与恢复演练需要进一步验证。",
    ),
    "model.py": (
        "标准 messages/system 与输出预算进入供应商适配器；输出文本并累计真实 usage、耗时和失败。",
        "不通过异常自动切换付费模型。ContextVar 让并行 Agent 的模型调用回到同一个请求 trace。",
        "GLM JSON object 适配与真实 usage 已验证，评委用量已单列；其他供应商契约、截断恢复及账单校准仍可增强。",
    ),
    "knowledge.py": (
        "租户、文档或查询进入知识层；输出带版本与 chunk ID 的候选片段，或写入摘要/画像投影。",
        "SQL 当前 ID 集合约束 Chroma 结果；增强检索中的改写与重排可以失败，但不能编造检索证据。",
        "需要中文检索标注集、Recall@k、向量投影重建队列和 embedding 消融验证。",
    ),
    "tools.py": (
        "可信用户、Agent 类型、工具名与模型参数进入执行边界；输出真实工具结果、计数和 trace。",
        "工具 schema、角色能力、业务属主校验分层执行。缓存按权限与版本隔离，半开熔断只允许一个探测。",
        "缓存/熔断状态目前在进程内；生产需要共享配额、调用审计与按工具细化预算。",
    ),
    "service.py": (
        "已鉴权用户与 ChatInput 进入同一聊天链路；输出回复、实际 Agent、路由理由、工具、来源、版本和 trace。",
        "先处理幂等与会话租约，再读记忆和路由。工具结果回到 Agent 后再生成回答，提交完成才返回可重放结果。",
        "multi 已加入任务清单、有限补做、角色与任务双层能力限制及请求级结果复用；一般语义真实性、复杂依赖与高并发指标仍需继续验证。",
    ),
    "protocol.py": (
        "MCP Streamable HTTP 消息与 Bearer token 进入官方 SDK；输出标准协议响应并复用相同业务工具。",
        "协议层不复制业务规则，身份从 token 重查；MCP 名称不是本地函数管理器的别名。",
        "公开 HTTPS 资源地址、企业 OAuth/OIDC 元数据和权限范围需要目标环境配置。",
    ),
    "api.py": (
        "HTTP 路径、严格请求体和 token 进入 FastAPI；输出身份范围内的数据或明确 401/403/409/422/504。",
        "所有业务入口走可信 Principal。客户、客服、财务与运维操作分开，监控观测实际完成 HTTP 请求。",
        "资源配额、公开部署地址、统一错误分类和生产审计/日志脱敏需要继续完善。",
    ),
    "payments.py": (
        "已审批退款进入外部 outbox；HTTPS 接收确认与签名最终事件进入结算核验；输出 processing/settled/rejected。",
        "网络收到成功响应仅表示已受理。只有匹配租户、订单和金额的最终事件，才能更新退款账本。",
        "模拟回调丢失对账已测试；真实支付商契约、凭证轮换、调度与人工核对需要最终集成。",
    ),
    "full_chain.py": (
        "固定任务、模型配置、实验方案和并发进入真实 HTTP 链路；输出逐例记录、状态检查、延迟/成本/区间与报告。",
        "先固定条件再运行，标签不进入 Agent；错误留在分母。v3支持变动订单、权限与检索故障夹具、逐项事实检查和按模板族配对统计，原始trace与账本状态可复查。",
        "参数化实例不能视为同数量独立场景；关键词核验不是完整语义证明，人工独立评分与盲测仍需补充。",
    ),
    "public_intents.py": (
        "固定外部样本和显式标签映射进入 /intents；输出准确率、宏 F1、逐类指标及混淆矩阵。",
        "公共英文单轮意图结果单独报告，不能混入中文事务完成率。",
        "需扩大样本并由独立标注者复核映射，评估其他语言与分布偏移。",
    ),
    "compare_runs.py": (
        "显式旧/新报告路径进入可比性检查；输出相对退化事件并用退出码支持 CI。",
        "从不覆写基线；5% 是工程门槛，不是统计显著性的证明。",
        "应加入多次重复、稳定性区间与更细的配置兼容约束。",
    ),
}
MEANINGS = {
    "answer_contains": "保留原词匹配，同时规范待财务/人工/客服审核的状态表达；这是开发期修正的关键词判分，不是独立语义评委。",
    "prepare_fixture": "根据评测标签建立不同订单、属主和租户；可只在本例应用注入知识不可用。客户Agent只收到用户消息，不读取夹具与金标。",
    "expected_for": "从预先定义的业务类型推导工具、金额、所属订单、答复事实及负向门槛；标签不能根据模型答复事后自动生成。",
    "canonical": "去除消息中的订单/咨询编号及金额，检查模板换参数后是否跨分区重复；不等于语义相似度判定。",
    "write_frozen": "序列化并哈希内容；文件存在且不同则拒绝覆写，防止悄悄改变已报告数据集。",
    "representatives": "按字符三元组Jaccard阈值建立候选近重复图，以并查集形成连通分量，每个分量选一个原始代表。",
    "audit": "重新读取生成产物与固定哈希，检查标签平衡、族分区、源行唯一及近重复；成功写审计JSON，失败立即中断。",
    "plan_tasks": "独立识别技术、订单、退款、人工及发票诉求，为每项指定负责人及完成必须具备的工具证据。",
    "scope_message": "将技术片段从完整请求中抽离，降低同一个 Agent 继续回答其他领域问题的概率；原文仍由执行层保留作授权依据。",
    "gaps": "检查这个任务自己的成功工具结果、可用知识、实质答复与领域要求，不用其他任务的成功替代它。",
    "render_tasks": "按任务顺序保留每项已验证的答复和未完成原因，不再交给模型自由压缩。",
    "_execute_tool": "按任务限制工具，统一写入摘要/原因，并用请求级锁与共享结果避免并行 Agent 重复操作。",
    "execute_task": "派生任务上下文并调用负责 Agent；异常留在原任务，不用通用 Agent 的返回偷偷替代成功。",
    "estimate_call": "使用单次调用长度选择版本化费率；未配置单价返回 None，不把未知费用写成零。",
    "commit_turn": "在同一事务里提交原始消息、会话状态、画像、幂等响应和 trace，避免只保存了回答却没保存状态。",
    "acquire_conversation": "校验会话属主并抢占有期限的会话租约，防止两个聊天轮次覆盖状态。",
    "cached_request": "校验请求指纹并读取已完成响应，使网络重试不重做业务。",
    "release": "只允许当前租约持有者释放，错误请求不能解锁别人的会话。",
    "refund_request": "检查订单归属与未占用余额，在事务中创建待审核申请；相同键不同载荷必须冲突。",
    "approve_refund": "要求财务权限并禁止申请者自批，pending 才能转审核结果。",
    "settle_refund": "沙箱内核验审批、幂等更新退款与订单；不向外部支付商发请求。",
    "create_ticket": "要求会话属主，使用持久幂等键创建 open 工单。",
    "update_ticket": "校验状态机、受理人和乐观版本；解决说明写回原会话。",
    "issue_token": "签发随机不透明 token，数据库只保存摘要、租户、角色和到期时间。",
    "authenticate": "把 token 摘要转换成可信 Principal，同时检查撤销和过期。",
    "verify_token": "将本项目 token 校验适配为官方 MCP SDK 的 AccessToken。",
    "retrieve": "把查询改写、并发检索、按稳定 ID 去重和重排接成一条可降级链路。",
    "call": "将模型提出的工具操作先验证再执行，并在 finally 中记录成功/失败与耗时。",
    "_call_llm": "在固定预算内交替生成结构化决策和执行工具；遇到缺少证据时不能凭空声称完成。",
    "chat": "为整个请求建立 trace、预算与会话租约，完成业务后原子提交并更新非权威投影。",
    "_run": "读取记忆与意图；multi 建立任务清单并逐项验证和渲染，legacy_multi 保留旧合并路径，返回带证据的结果。",
    "complete": "执行一次真实模型 HTTP 请求；把供应商返回的 usage 累加到当前请求 trace。",
    "enqueue": "把批准退款和待发送消息在同一事务内写入，保证崩溃后仍知道要发送什么。",
    "dispatch": "领取待发送记录，使用稳定幂等键发送；网络异常保留预留额度，不能猜测支付是否成功。",
    "event": "先校验 HMAC 与时间窗口，再核验业务字段，最后在同一事务中事件去重和入账。",
    "verify": "只在测试验证器中检查实际工具调用与最终业务状态，期望值不注入客服链路。",
    "run_case": "为每个案例与实验组隔离用户和账本，通过 HTTP 执行每轮消息及人工流程。",
    "aggregate": "以全部任务为分母聚合完成率、nearest-rank P95、真实token与可用成本；另按模板族等权汇总，避免把同族重复实例当作新独立场景。",
    "compare": "先验证两个报告可比较，再按方向检测相对退化，保留原报告不变。",
}


def explain(line):
    t = line.strip()
    if not t:
        return "空行，分隔逻辑。"
    if t.startswith("#"):
        return "作者注释，说明约束或设计意图；本行不执行。"
    if t.startswith(("import ", "from ")):
        return "导入本段使用的标准库、依赖或项目组件。"
    if t.startswith("@"):
        return "注册路由/工具/异常处理或声明数据结构行为；具体权限仍由函数体校验。"
    if "CREATE TABLE" in t:
        return "声明持久化表与唯一键，供后续事务约束状态与重放。"
    if "c.execute" in t or "db.execute" in t:
        return "执行参数化 SQL；参数独立绑定，查询/更新的权限范围取决于这里的 WHERE 与当前事务。"
    for name, meaning in MEANINGS.items():
        if name + "(" in t:
            return meaning
    if ".require(" in t:
        return "在服务器检查角色；admin 的继承规则由 Principal.require 定义。"
    if ".model_validate(" in t or ".validate(" in t:
        return "检查实际数据是否符合完整 schema，失败时拒绝继续执行。"
    if "raise " in t:
        return "显式终止不满足约束的路径；调用方把错误转换为拒绝、冲突或降级。"
    if t.startswith(("except ", "except:")):
        return "处理这一类失败；注意哪些失败允许降级，哪些必须拒绝操作。"
    if t.startswith("finally:"):
        return "无论成功、失败还是取消都执行清理/记录，避免租约或 trace 泄漏。"
    if t.startswith(("async with ", "with ")):
        return "限定资源、事务、超时或上下文的生存范围，退出时清理。"
    if t.startswith(("async def ", "def ")):
        return "定义此函数的参数与入口；下面的小节说明它在全链路中的职责。"
    if t.startswith("class "):
        return "定义一组状态和行为，或定义可校验的数据契约。"
    if t.startswith(("if ", "elif ", "else:")):
        return "按条件选择路径；阅读条件即可判断哪些输入会进入执行、拒绝或降级。"
    if t.startswith(("for ", "while ")):
        return "遍历候选/任务或按预算推进循环；检查循环边界防止无限调用。"
    if t.startswith("return "):
        return "结束当前函数并把本行构造的结果交给调用方。"
    if "await " in t:
        return "等待异步 I/O 或并行任务，允许同一事件循环处理其他请求。"
    if ".append(" in t or ".extend(" in t:
        return "把这一轮的事实、输出或失败加入容器，供后续汇总或验证。"
    if "json." in t:
        return "在结构化 Python 数据与 JSON 之间转换；数据不会因此获得执行权限。"
    if "=" in t:
        return "保存配置、状态或计算结果；名称与右侧表达式对应本行数据含义。"
    return "上一条表达式/说明的续行，结合所在函数与相邻行阅读即可。"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    index = []
    paths = sorted((ROOT / "supportflow").glob("*.py")) + [
        ROOT / "evaluation" / n
        for n in ["full_chain.py", "public_intents.py", "compare_runs.py"]
    ]
    paths += sorted((ROOT / "scripts").glob("*.py")) + sorted(
        (ROOT / "tests").glob("*.py")
    )
    paths += sorted((ROOT / "core").glob("*.py")) + sorted(
        (ROOT / "agents").glob("*.py")
    )
    paths += [ROOT / "api/main.py", ROOT / "api/supportflow.py"]
    paths += [
        ROOT / name
        for name in [
            "Dockerfile",
            "compose.supportflow.yml",
            "requirements.txt",
            "requirements-dev.txt",
            ".env.supportflow.example",
            ".dockerignore",
            ".gitignore",
        ]
    ]
    for path in paths:
        if path.name == "__init__.py":
            continue
        source = path.read_text(encoding="utf-8-sig")
        lines = source.splitlines()
        tree = ast.parse(source) if path.suffix == ".py" else ast.parse("")
        language = "python" if path.suffix == ".py" else "text"
        if path.suffix != ".py":
            default = (
                "构建工具、依赖安装器或配置加载器读取本文件；输出构建上下文、容器服务、依赖版本或环境参数。具体消费入口参见 SUPPORTFLOW.md。",
                "配置文件只声明行为，不证明服务已经运行。注意默认 sandbox、认证口令、模型地址、持久卷和排除敏感运行数据。",
                "Docker/Redis 需要在目标运行环境验证；镜像摘要、供应链与备份恢复需进一步固定和演练。",
            )
        elif path.parent.name == "tests":
            default = (
                "隔离的测试目录、身份、请求或模拟依赖进入测试；输出断言通过/失败与 pytest 结果。",
                "测试替身验证工程行为，不能充当真实模型准确率或生产性能证据。",
                "增加真实供应商、并发进程、故障恢复和独立业务标签验证。",
            )
        elif path.parent.name == "scripts":
            default = (
                "命令行参数、工作区文件或固定下载源进入维护脚本；输出明确的本地模型、数据集、身份文件、验证记录或学习文档。",
                "下载源与结果哈希、文件落点和被忽略的敏感/大文件需一并核对；脚本不会隐式调用付费模型。",
                "跨平台运行与远程服务配置应在目标环境复验；学习文档行号需在源码变化后重新生成。",
            )
        elif path.parent.name in {"core", "agents"}:
            default = (
                "用户消息、历史、实体与模型/Skills 依赖进入原核心组件；输出意图、Agent 路由、技能上下文或模型结果。",
                "这部分是新版复用的原始核心。v2 在 ChatService 与 ToolAgent 中接入事务、权限与完整工具循环。",
                "单独运行旧编排方法与新版 HTTP 链路不同；置信度校准、真正多实例调度和路由消融仍需验证。",
            )
        else:
            default = (
                "应用启动器导入 create_app；输出共享鉴权、业务、MCP 和监控的 FastAPI 应用。",
                "入口保持薄层，业务规则集中在 supportflow，避免 CLI/HTTP/评测各自实现不同流程。",
                "生产需配置可达模型、受管凭据、HTTPS 和基础设施健康检查。",
            )
        flow, design, limits = NOTES.get(path.name, default)
        title = str(path.relative_to(ROOT))
        name = title.replace("\\", "__").replace("/", "__") + ".md"
        sections = [
            f"# {title}\n\n## 输入输出流\n\n{flow}\n\n## 先理解设计\n\n{design}\n\n源码 SHA256：`{hashlib.sha256(path.read_bytes()).hexdigest()}`。下面的行号属于这一快照。\n"
        ]
        functions = {
            n.lineno: n
            for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        sections.append(
            "## 逐行阅读\n\n简单语法简述；重要业务操作在所在函数入口与对应调用行解释。\n"
        )
        for i, line in enumerate(lines, 1):
            if i in functions:
                node = functions[i]
                meaning = MEANINGS.get(
                    node.name,
                    "结合输入参数、返回值及其调用方，观察此函数怎样推进本文件的输入输出流。",
                )
                sections.append(f"\n### L{i} · {node.name}\n\n{meaning}\n")
            if not line.strip():
                continue
            sections.append(
                f"\n**L{i}**\n\n```{language}\n{line}\n```\n\n{explain(line)}\n"
            )
        sections.append(
            f"\n## 结合全项目看：边界与增强\n\n{limits}\n\n文件存在相应代码并不代表已获得生产验证；请结合实测报告与 08 新版指南判断已运行的证据。\n"
        )
        (OUT / name).write_text("".join(sections), encoding="utf-8")
        index.append(f"- [{title}]({name})：{len(lines)} 行。")
    (OUT / "README.md").write_text(
        "# SupportFlow v2 逐行索引\n\n先阅读 [新版结构与设计](../08_SupportFlow实现与评测.md) 和 [复合任务改造](../10_复合任务改造与GLM实测.md)，再沿 service → planning → tools → store → evaluation 展开。每份文件包含输入输出流、设计、每个非空源码行的解释和跨文件增强建议。简单表达式按语法简述，不能用生成的句子代替阅读实际条件。\n\n"
        + "\n".join(index),
        encoding="utf-8",
    )
    print("Wrote", len(index), "source study files")


if __name__ == "__main__":
    main()
