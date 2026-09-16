"""部署、配置、业务规则、已有材料的人工解读。"""
from content import FILES, file

file('Dockerfile', '构建 Python 应用镜像，而非启动全套服务。',
     'Docker 构建上下文、requirements.txt、模型下载地址、--target。',
     'base/dependencies/production/development 构建阶段；默认容器命令启动 api.main:app。',
     '基础 Python 3.12 → 安装依赖并预下载 ONNX → production 复制依赖与代码、切非 root → development 保留开发环境。',
     ['最后阶段是 development，docker build 不带 --target 默认构建该阶段；Compose 显式 production 才是生产配置。',
      '没有 test 阶段，与 build-image.sh build-test 冲突；开发阶段也没安装 pytest/debugpy。',
      '预下载模型与“无本地 ML 模型”注释不一致；Chroma 默认 embedding 仍依赖 ONNX 资源。下载未校验摘要，依赖未锁传递版本。',
      'COPY . . 会包含不在 .dockerignore 中的资料和新解读文档，后续可按运行目录精确复制，降低镜像体积。'], {},
     {5:'固定应用 Python 主次版本，避免用当前宿主机 Python 版本推断生产运行时。',23:'先复制依赖清单，使改业务代码时能复用安装层缓存。',28:'构建时准备 Chroma ONNX 模型缓存，避免首次查询再下载。',45:'把 root 下载缓存复制到运行用户主目录并设所有权。',48:'复制整个未被 .dockerignore 排除的上下文。',53:'生产应用以 echomind 用户运行，宿主机绑定目录仍需实际可写。',60:'直接 uvicorn 启动，不经过 api.main.py 的 __main__ 配置分支。',63:'最后构建阶段；不指定 target 会选到 development。'})

file('docker-compose.yml', '将应用、两种存储、指标服务和反向代理放在同一个容器网络。',
     '.env 的替换参数、镜像/构建上下文、宿主绑定目录。',
     '5 个服务、bridge 网络、命名数据卷；宿主端口 80/8000/6379/8001/9090。',
     'Redis/Chroma 健康后启动应用 → 应用健康后启动 Nginx；Prometheus 定时拉应用 /metrics。',
     ['environment 覆盖了 Redis URL 和存储路径，却没有覆盖 CHROMA_HOST/CHROMA_PORT。按 .env.example 的 localhost:8001 启动应用容器，会连自己而非 chromadb:8000，可能触发本地降级。README 关于“已覆盖 Chroma 地址”的说法不成立。',
      '同时存在 Chroma 服务命名卷与应用本地 fallback 绑定目录，需要记录实际使用后端，否则备份可能拿错数据。',
      '当前没有 Grafana/Alertmanager 服务；不因模板有用户名密码或脚本创建目录就认为已部署。',
      '应用端口 8000 直接发布，外部可绕过 Nginx 的限流/metrics 访问限制；固定 container_name 也限制横向多副本模式。'], {},
     {12:'Redis 强制密码认证，应用 URL 也必须包含凭据。',29:'宿主访问 8001，容器间访问 chromadb:8000。',75:'明确选 production，避免 Dockerfile 最后 development 阶段成为默认。',80:'将 .env 变量注入应用容器；这一步不会自动把 localhost 改成服务名。',83:'容器内 Redis 连接用服务名并带密码。',84:'这是本地 fallback 路径，不是覆盖 CHROMA_HOST。',88:'应用本地 Chroma 文件绑定到宿主；和独立 chromadb-data 卷不是同一个存储。',90:'挂载 Skills 使宿主修改可被 reload 读取。',135:'Nginx metrics allow 使用相同网段；改网段时需要同步。'})

file('build-image.sh', '封装 Docker 镜像构建、标签、推送与构建缓存清理。',
     '命令行 command/--version/--registry/--platform/--no-cache、VERSION 环境变量。',
     '本地镜像/标签，push 会写远程仓库，clean 会清构建缓存；终端日志与退出码。',
     'main→parse_args→对应函数→构造 docker 命令→eval；只是读此文件，不执行任何部署动作。',
     ['build 不指定 target 会落到 development；build-test 目标 test 在 Dockerfile 不存在。',
      'main 已 shift，再在 push/tag 分支 shift 一次，会丢参数；parse_args 只消费自身函数参数，push/tag 的位置参数传递与帮助示例不一致。',
      '命令拼字符串再 eval，含空格路径/参数和 shell 特殊字符不稳；建议改 Bash 数组并严格校验参数。',
      '--registry 在构建路径没有统一尾部 /，push_image 才添加；set -e 可使后面的 $? 失败分支来不及执行。',
      '此文件被 .gitignore 的 build-image*.sh 匹配，不能只用 rg 默认输出判断它不存在。'], {},
     {6:'失败即退出；后面通过 $? 判断失败的代码不一定能够执行。',79:'把命令保存在字符串而不是 argv 数组。',108:'eval 二次解释参数，可能错误拆分或执行参数中的 shell 语法。',194:'空 target 使用 Dockerfile 最后阶段，当前是 development。',203:'test 阶段不存在，调用会构建失败。',206:'main 先 shift 过一次，这里再次移动位置参数，需与帮助示例逐项核对。'})

file('docker-deploy.sh', '对已有 Compose 栈执行启动、状态、备份、恢复等运维操作。',
     '首个子命令、可选服务名/备份目录；当前工作目录下 .env、config、docker-compose.yml。',
     '容器状态变化、目录/备份文件、终端输出；cleanup/restore 会删除或覆盖数据。',
     'main case 分发→依赖/配置准备或生命周期函数→docker-compose；backup/restore 包含真实文件副作用。',
     ['脚本使用 docker-compose 命令，README 使用 docker compose；只装后者时依赖检查可能拒绝运行。',
      'health/backup 的 redis-cli 未传密码，而 Compose requirepass 已启用；Redis 健康和 SAVE 分支会失败。',
      '创建 Grafana/alerts 目录不等于启用监控服务；PROJECT_NAME/COMPOSE_FILE 等变量没有全部接入命令。',
      '运行中复制 Chroma 文件缺少一致性快照；Redis AOF 已启用但备份主要拿 dump.rdb；restore 含 rm -rf config，恢复策略需先演练。',
      '本次任务仅解读这些动作，没有执行脚本、恢复或清理。'], {},
     {41:'只查独立 docker-compose 可执行文件，不检测 docker compose 子命令。',87:'每次禁用构建缓存，重复安装依赖和下载资源。',154:'这里没提供 Redis 密码，和 Compose 的认证设置不一致。',183:'down -v 会删除命名卷，属于真正破坏性操作。',199:'SAVE 缺认证，不能据此宣称已有可用备份。',206:'备份会包含 .env；学习文档不复制其中实际值。',242:'恢复阶段先删现有 config，再复制备份，不是事务性恢复。'})

file('run-image.sh', '只运行一个应用镜像的便捷脚本。',
     'run/run-dev/run-test/run-prod 等子命令、端口/目录/环境文件/名称参数。',
     'docker run 命令与容器状态；可能先停止删除同名容器。',
     'main→run_container 解析参数→拼端口/卷/env→按模式调整→删除同名容器→eval docker run。',
     ['帮助写 --network，但参数解析没有该分支，容器不自动加入 Compose 网络；也不启动 Redis/Chroma。',
      'dev/test/prod 都使用同一 image_tag，dev 只是多映射 5678，没有选开发镜像或启动调试器；test 也没有自动运行测试。',
      '默认把本地 9090 映射容器 9090，但 .env.example 的 PROMETHEUS_PORT=9091，且可能与独立 Prometheus 占用冲突。',
      'clean 文案说删除数据卷，实际只 stop/rm 容器，未删绑定目录或执行 rm -v；文字与副作用要分清。',
      'eval 与相对路径绑定使带空格目录容易出问题；本工作区路径恰有空格，不应盲目复制脚本运行。'], {},
     {134:'未知选项直接忽略，所以帮助里的 --network 不会生效。',151:'三种模式共用这个镜像标签，没有模式到镜像映射。',152:'默认容器指标端口写死 9090，不读取 env_file 中的实际监听值。',159:'开放端口不代表 debugpy 在运行。',195:'有同名容器时自动停止，会中断其现有服务。',200:'字符串 eval 对空格路径和参数引用脆弱。',296:'这里只删除容器，不删除宿主绑定数据目录。'})

file('config/nginx/nginx.conf', 'HTTP 网关：代理、基础 IP 限流和特定端点访问控制。',
     '客户端 HTTP、Docker DNS 中 echomind 服务名；nginx 配置。',
     '转发至 echomind:8000 的请求/响应、访问和错误日志、限流拒绝响应。',
     'listen 80→匹配 location→限流/头部/代理；metrics 单独网段控制；静态目录另走 alias。',
     ['只有一个上游，least_conn 只是预备负载均衡配置；没有多应用副本。',
      'HTTPS 配置整段注释，当前只监听 80；示例知识宣称所有传输 TLS 与实际配置不符。',
      '限流位于 location /，独立 location 不继承它；应用 8000 直连也能绕过网关。',
      '/static 指向 /app/static，但当前 Compose 未挂载该目录，仓库也没有前端静态资产服务实现。',
      'proxy_buffering on，且 API 没 SSE；不能称已支持流式 token 返回。'], {},
     {32:'网关层请求体上限；应用直连时仍依赖 Python 检查。',47:'只有一个上游 server，所以 least_conn 当前没有分配选择。',52:'按来源 IP 10 次/秒的区域，具体生效还需 location 的 limit_req。',72:'允许 20 请求突发并直接处理，超限将被网关拒绝。',87:'60 秒读超时不是整个 Agent 链路统一 deadline。',90:'响应缓冲启用；未来流式输出需重新设计。',107:'只限制经 Nginx 的 /metrics；不能约束应用 8000 直连。',134:'下面全部是注释模板，不会启用 TLS。'})

file('config/prometheus.yml', '配置 Prometheus 从应用指标注册表抓取数据。',
     'echomind:8000/metrics、localhost:9090 自身指标。',
     '带 cluster/environment/service 标签的时序数据，由 Prometheus 服务保存。',
     '每 10 秒抓主应用，每 15 秒默认抓自身；rule_files 声明潜在规则目录。',
     ['alerts/*.yml 没有对应现存规则文件，也没有 Alertmanager 服务配置；不是完整 Prometheus 告警投递链。',
      '能抓到端点不代表业务 metrics 已注册，需结合 PROMETHEUS_PORT 和 Monitor 初始化判断。',
      '真实请求延迟分布、token、费用、RAG 命中质量没有在应用埋点，本文件无法弥补缺失。'], {},
     {11:'规则 glob 是路径声明，当前仓库无实际 alerts YAML。',17:'抓主 API 8000，不抓额外的 PROMETHEUS_PORT。',20:'覆盖 global 的 15 秒为 10 秒。',26:'这里 localhost 是 Prometheus 容器自己。'})

file('requirements.txt', 'Python 直接依赖的固定版本列表。', 'pip install -r requirements.txt。',
     '当前环境安装 LLM SDK、Web、存储、监控和工具库。',
     'Docker dependencies 阶段读取→安装→复制到 production。',
     ['锁了直接依赖，未固定全部传递依赖和下载哈希，不是完整 lockfile。',
      '没有 MCP 协议 SDK、LangChain/LangGraph、PyTorch 训练依赖；不要将未使用框架列为本仓库技术栈。',
      '没有开发测试依赖或 CI 配置；当前解释验证使用标准库隔离执行，不证明已安装环境集成可用。'], {},
     {4:'Anthropic 风格 messages.create 客户端，多个模块复用调用范式。',7:'提供 HTTP 路由和 lifespan。',8:'ASGI 服务运行器，与 Docker CMD 对应。',9:'HTTP 输入输出模型验证/序列化。',10:'UploadFile multipart/form-data 解析依赖。',13:'redis.asyncio 支撑工作记忆异步访问。',14:'Chroma 同时存知识、摘要、画像，代码把同步运行操作放线程。',17:'Gauge/Histogram/Counter 和 /metrics 导出。',20:'Monitor webhook HTTP 调用。',23:'load_dotenv 读取本地 .env。'})

for path in ['.env', '.env.example', '.env.example.env']:
    file(path, '环境配置' + ('实例（本解读只展示键名，值全部脱敏）。' if path == '.env' else '模板，不等于所有字段都有实现。'),
         '启动器、dotenv/Compose 读取键值。', '进程环境变量；被代码消费的键才改变行为。',
         '模板复制为 .env→启动加载→os.getenv 或 Compose 插值→组件构造。参见总览中的配置消费表。',
         ['许多字段如 JWT_SECRET_KEY、MEMORY_MAX_TOKENS、INTENT_CACHE_TTL、ENABLE_SWAGGER_UI 没有 Python 消费者；设置它们不会启用所暗示能力。',
          'MONITORING_INTERVAL 与实际读取 MONITOR_INTERVAL 名字不同。Chroma 本地地址不能直接用于 Compose 应用容器。',
          '模板中的模型名/URL 只视为配置示例，本次没有联网验证外部产品现状。真实凭据不复制进面试资料。'], {})

file('.gitignore', '规定 Git 默认忽略的文件模式。', 'git add/status 与忽略模式。',
     '影响未跟踪文件发现；不会移除已跟踪文件。', '忽略环境、数据、虚拟环境、IDE、构建产物。',
     ['data/ 被忽略但工作区存在 demo_docs 和 baseline，不能只用 git ls-files 或默认 rg 当全文件地图。',
      'build-image*.sh 也被忽略，却是现存业务辅助脚本；重要可复用脚本应审视版本管理规则。'], {})
file('.dockerignore', '过滤 Docker 构建上下文。', 'Docker build 扫描的项目文件。',
     '减少传入镜像构建的本地文件，排除 .env 与本地 Chroma 等。', '目录扫描→ignore 规则→Docker COPY。',
     ['!.env.example 重新包含示例，.env.example.env 仍排除。',
      'README/wiki 以及本解读文件夹未排除，会被 COPY . . 带入镜像；将部署上下文与学习资料分开可进一步精简。'], {})

for kind, name, problem in [
 ('general_customer_service','通用客服接待规范','通过澄清和分流组织首轮答复，不能代替编排器的实际路由。'),
 ('technical_support','技术支持处理规范','按故障现象、日志、影响范围给排查步骤，没有真实读取日志或修复后台的权限。'),
 ('billing_support','账单退款处理规范','约束账务解释和审核边界，没有查询支付流水、退款、开票的执行工具。')]:
    file(f'skills/{kind}/SKILL.md', f'{name}，作为业务规则输入给模型。',
         'front matter：name/description/keywords/agents/enabled；正文 SOP。',
         '匹配后进入 Agent system prompt；不会直接执行其中描述的业务动作。',
         'SkillManager.load 解析→匹配当前 message+agent_type→裁剪正文→BaseAgent._build_system_prompt→模型生成。',
         [problem,'只有关键词命中才注入，业务底线可能在未匹配请求中缺失。规则还受每项 3200 字符与总预算约束，应确保关键规则靠前。',
          '转人工/核验只是文字指引，当前代码没有身份核验、人工工单状态机。新增真工具时必须在执行层落实审核和权限。'], {})
file('skills/README.md', '教运营编写 Skill 的人读文档。', 'Skill 文件格式与 reload 接口约定。',
     '人工编写的业务文件；此 README 被加载器排除，不直接注入模型。', '阅读格式→编写 Skill→调用 /skills/reload→通过 /skills 检查。',
     ['文中中文逗号分隔也支持的说法与 _as_list 实际英文逗号 split 不一致。',
      '热加载是手动接口，不是自动监听，也没有多 worker 同步机制。'], {})

file('data/demo_docs/sample_knowledge.json', '用于演示导入的六篇知识材料，不是系统功能规格或事实证明。',
     '人工读取或 /knowledge/upload 上传 JSON 数组。', 'knowledge_base 文档片段；若导入，会影响模型回答事实。',
     '上传解析→KB.add_documents→切片/向量→检索→生成模型引用。启动默认知识来自代码内置列表，不自动读此文件。',
     ['SOC2、全部 TLS、92% 准确率、召回提升40%、镜像500MB 等文字没有当前仓库可复验依据，不能放入简历当实绩。',
      'API Key 控制台、订阅套餐、自动退款等产品话术没有对应后端实现；这种材料导入会把不真实内容包装成“检索证据”。',
      '资料需建立审核、来源、时间、版本和租户权限；RAG 能引用材料并不保证材料正确。'], {})
file('data/demo_docs/troubleshooting.md', '演示故障排查知识材料。', '上传到知识库的 Markdown 文本。',
     '存储后被知识检索并进入背景 prompt。', '人工上传→按中文句号/换行切片→Chroma 检索→Agent 说明。',
     ['“24小时自动退回重复扣款”与 billing Skill 的需人工核验边界矛盾，仓库也无自动退款执行代码。',
      '版本 v2.0.3、移动应用设置等是示例内容，当前仓库未提供对应客户端实现。应标记 demo 并审核后再用于真实客服。'], {})
file('data/eval/baseline.json', '现存历史评测快照。', 'EndToEndEvaluator._load_baseline 读取 JSON。',
     '用于下次均分相对比较的 EvalReport；新运行会覆盖此文件。', '磁盘 JSON→报告对象→与本轮均分对比→保存最新报告。',
     ['文件记录 2026-05-31 的历史结果，非本次重新运行结果；该快照内意图样本为8条，当前 DEFAULT_INTENT_CASES 为11条且细化标签。',
      'pass_rate=1.0 是8个报告项通过，不能当成真实用户请求全量100%准确率。',
      '缺少模型、prompt、数据集、代码版本等实验元数据，不足以支撑严格跨版本回归结论。'], {})

for path, role, gaps in [
 ('README.md','部署、接口与排障总手册，适合操作查阅。',[
  '声称 Compose 覆盖 Chroma 连接地址，但 yml 未设置 HOST/PORT；按示例 localhost 会误连应用容器自己。',
  '复合问题示例声称会并行，但实际要看领域相对阈值；已在新文档给出可计算反例。',
  'API 示例与操作步骤不是本次实测证明；清空数据库、删除卷等步骤也不是学习所必需。']),
 ('wiki/重点代码.md','人工挑选的关键片段讲解，不是逐行源码快照。',[
  '含历史 _route 等片段，当前主链路是 _route_decision；部分简化片段省略分支，须回到实际源码。',
  '“端到端评测”仅覆盖编排器，没走完整 /chat；Chroma 服务端 embedding 和余弦注释也不能直接当事实。']),
 ('wiki/简历包装.md','面试表达素材，必须按实际职责和代码裁剪。',[
  'Java 21/Spring Boot/Spring AI 部分是材料中的另一种写法，当前没有 Java 源码、pom.xml 或 Spring 工程。',
  '不要把 MCP 风格本地工具说成协议服务器，不要把默认单实例降权说成实测多副本流量切换。']),
 ('wiki/NexusOps企业智能运营协同中枢.md','EchoMind 的产品定位材料，NexusOps 是叙述名称。',[
  '当前代码、应用标题、容器名仍为 EchoMind；没有另一套 NexusOps 代码或部署。',
  '“登录401且重复扣款”的示意主辅路由不保证被当前阈值触发；routing_confidence 数字是示例而非本次模型结果。']),
 ('wiki/架构图.md','链接既有六张 SVG 架构图的索引。',[
  '架构图表示设计方向，当前运行边界请以新结构图和源代码为准。',
  '监控反馈、评测、工具与 Agent 是不同链路，不能把图上的邻近节点理解为运行时相互调用。'])]:
    file(path, role, '读者、示例命令、代码片段和设计叙述。',
         '帮助人工理解或操作；文档本身不被业务 Python 自动执行。',
         '阅读→对应源文件/接口核实→仅采用有证据的表述。代码块按阅读材料处理，不执行。', gaps, {})

for path in [
 'wiki/assets/architecture/01-overall-architecture.svg',
 'wiki/assets/architecture/02-chat-flow.svg',
 'wiki/assets/architecture/03-agent-skills.svg',
 'wiki/assets/architecture/04-data-storage.svg',
 'wiki/assets/architecture/05-monitor-eval.svg',
 'wiki/assets/architecture/06-deployment.svg',
 'wiki/assets/posters/echomind-update-poster.svg']:
    file(path, '静态 SVG 展示资产：'+path.rsplit('/',1)[1],
         'XML 中的画布、样式、图形、文本和连接线。', '浏览器/Markdown 渲染后的架构图或宣传海报；无业务数据存储副作用。',
         'svg 画布→defs 样式/箭头→rect/text/path 等元素→静态图片。图中连线是作者画出的表达，不会执行 Python 调用。',
         ['需要与代码版本一起更新；图中的主辅协作、监控、部署语义不能代替对应函数证据。',
          '本解读对重复坐标和配色简略，保留逐行位置；重点读可见标签和它连接的实际模块。'], {})
