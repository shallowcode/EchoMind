# docker-compose.yml 解读

## 输入、输出与流向

**定位：** 将应用、两种存储、指标服务和反向代理放在同一个容器网络。

**输入：** .env 的替换参数、镜像/构建上下文、宿主绑定目录。

**输出 / 副作用：** 5 个服务、bridge 网络、命名数据卷；宿主端口 80/8000/6379/8001/9090。

**流向：** Redis/Chroma 健康后启动应用 → 应用健康后启动 Nginx；Prometheus 定时拉应用 /metrics。

[返回阅读入口](../README.md) · [对照原文件](../../docker-compose.yml)

当前工作区快照：142 行。原始行号列对应原文件；空白和纯注释可略读。 SHA-256：`c5314854187da7c9f57f5592b9301ad5fcc8e848eae858a4ed8df219f09a25bb`。

## 按原行号阅读

读法：先看每个函数前的因果解释，再看逐行表。多行参数、词表、提示文本续行从属于起始语句；关键行另加粗说明。


### L1 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L1 | <code># EchoMind 智能客服系统 — Docker Compose 服务编排</code> | 注释/说明：EchoMind 智能客服系统 — Docker Compose 服务编排 |
| L2 | <code># 三级记忆架构：Redis（工作记忆）+ ChromaDB（情景记忆 + 用户画像）</code> | 注释/说明：三级记忆架构：Redis（工作记忆）+ ChromaDB（情景记忆 + 用户画像） |
| L3 | （空行） | 空行/展示分隔。 |
| L4 | <code>services:</code> | 开始定义Compose服务集合；缩进决定该项属于哪个服务/抓取任务。 |
| L5 | （空行） | 空行/展示分隔。 |
| L6 | <code>&nbsp;&nbsp;# ── Redis 缓存（工作记忆）────────────────────────────────────────────────────</code> | 注释/说明：── Redis 缓存（工作记忆）──────────────────────────────────────────────────── |
| L7 | <code>&nbsp;&nbsp;redis:</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L8 | <code>&nbsp;&nbsp;&nbsp;&nbsp;image: redis:7-alpine</code> | 从镜像名与标签选择容器内容；缩进决定该项属于哪个服务/抓取任务。 |
| L9 | <code>&nbsp;&nbsp;&nbsp;&nbsp;container_name: echomind-redis</code> | 固定容器名称，运维脚本也依赖此名字；缩进决定该项属于哪个服务/抓取任务。 |
| L10 | <code>&nbsp;&nbsp;&nbsp;&nbsp;ports:</code> | 发布宿主端口到容器端口；缩进决定该项属于哪个服务/抓取任务。 |
| L11 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- &quot;6379:6379&quot;</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L12 | <code>&nbsp;&nbsp;&nbsp;&nbsp;command: redis-server --appendonly yes --requirepass ${REDIS_PASSWORD:-echomind123}</code> | **关键：**Redis 强制密码认证，应用 URL 也必须包含凭据。 |
| L13 | <code>&nbsp;&nbsp;&nbsp;&nbsp;volumes:</code> | 定义挂载；根级同名键声明命名卷；缩进决定该项属于哪个服务/抓取任务。 |
| L14 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- redis-data:/data</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L15 | <code>&nbsp;&nbsp;&nbsp;&nbsp;restart: unless-stopped</code> | 容器退出后的重启策略；缩进决定该项属于哪个服务/抓取任务。 |
| L16 | <code>&nbsp;&nbsp;&nbsp;&nbsp;networks:</code> | 指定服务所属网络；根级声明网络；缩进决定该项属于哪个服务/抓取任务。 |
| L17 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- echomind-network</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L18 | <code>&nbsp;&nbsp;&nbsp;&nbsp;healthcheck:</code> | 定义依赖可用性探测；缩进决定该项属于哪个服务/抓取任务。 |
| L19 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;test: [&quot;CMD&quot;, &quot;redis-cli&quot;, &quot;-a&quot;, &quot;${REDIS_PASSWORD:-echomind123}&quot;, &quot;ping&quot;]</code> | 健康检查执行的命令；缩进决定该项属于哪个服务/抓取任务。 |
| L20 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;interval: 10s</code> | 健康检查周期；缩进决定该项属于哪个服务/抓取任务。 |
| L21 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;timeout: 5s</code> | 单次检查超时；缩进决定该项属于哪个服务/抓取任务。 |
| L22 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;retries: 5</code> | 连续失败次数阈值；缩进决定该项属于哪个服务/抓取任务。 |
| L23 | （空行） | 空行/展示分隔。 |
| L24 | <code>&nbsp;&nbsp;# ── ChromaDB 向量数据库（情景记忆 + 用户画像）────────────────────────────────</code> | 注释/说明：── ChromaDB 向量数据库（情景记忆 + 用户画像）──────────────────────────────── |
| L25 | <code>&nbsp;&nbsp;chromadb:</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L26 | <code>&nbsp;&nbsp;&nbsp;&nbsp;image: chromadb/chroma:0.5.23</code> | 从镜像名与标签选择容器内容；缩进决定该项属于哪个服务/抓取任务。 |
| L27 | <code>&nbsp;&nbsp;&nbsp;&nbsp;container_name: echomind-chromadb</code> | 固定容器名称，运维脚本也依赖此名字；缩进决定该项属于哪个服务/抓取任务。 |
| L28 | <code>&nbsp;&nbsp;&nbsp;&nbsp;ports:</code> | 发布宿主端口到容器端口；缩进决定该项属于哪个服务/抓取任务。 |
| L29 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- &quot;8001:8000&quot;</code> | **关键：**宿主访问 8001，容器间访问 chromadb:8000。 |
| L30 | <code>&nbsp;&nbsp;&nbsp;&nbsp;environment:</code> | 注入变量，应用同名值覆盖env_file；缩进决定该项属于哪个服务/抓取任务。 |
| L31 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- IS_PERSISTENT=TRUE</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L32 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- PERSIST_DIRECTORY=/chroma/chroma</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L33 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- ANONYMIZED_TELEMETRY=FALSE</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L34 | <code>&nbsp;&nbsp;&nbsp;&nbsp;volumes:</code> | 定义挂载；根级同名键声明命名卷；缩进决定该项属于哪个服务/抓取任务。 |
| L35 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- chromadb-data:/chroma/chroma</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L36 | <code>&nbsp;&nbsp;&nbsp;&nbsp;restart: unless-stopped</code> | 容器退出后的重启策略；缩进决定该项属于哪个服务/抓取任务。 |
| L37 | <code>&nbsp;&nbsp;&nbsp;&nbsp;networks:</code> | 指定服务所属网络；根级声明网络；缩进决定该项属于哪个服务/抓取任务。 |
| L38 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- echomind-network</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L39 | <code>&nbsp;&nbsp;&nbsp;&nbsp;healthcheck:</code> | 定义依赖可用性探测；缩进决定该项属于哪个服务/抓取任务。 |
| L40 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;test: [&quot;CMD-SHELL&quot;, &quot;curl -sf http://localhost:8000/api/v1/heartbeat &#124;&#124; exit 1&quot;]</code> | 健康检查执行的命令；缩进决定该项属于哪个服务/抓取任务。 |

### L41 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L41 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;interval: 30s</code> | 健康检查周期；缩进决定该项属于哪个服务/抓取任务。 |
| L42 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;timeout: 10s</code> | 单次检查超时；缩进决定该项属于哪个服务/抓取任务。 |
| L43 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;retries: 3</code> | 连续失败次数阈值；缩进决定该项属于哪个服务/抓取任务。 |
| L44 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;start_period: 10s</code> | 启动宽限期；缩进决定该项属于哪个服务/抓取任务。 |
| L45 | （空行） | 空行/展示分隔。 |
| L46 | <code>&nbsp;&nbsp;# ── Prometheus 监控 ─────────────────────────────────────────────────────────</code> | 注释/说明：── Prometheus 监控 ───────────────────────────────────────────────────────── |
| L47 | <code>&nbsp;&nbsp;prometheus:</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L48 | <code>&nbsp;&nbsp;&nbsp;&nbsp;image: prom/prometheus:latest</code> | 从镜像名与标签选择容器内容；缩进决定该项属于哪个服务/抓取任务。 |
| L49 | <code>&nbsp;&nbsp;&nbsp;&nbsp;container_name: echomind-prometheus</code> | 固定容器名称，运维脚本也依赖此名字；缩进决定该项属于哪个服务/抓取任务。 |
| L50 | <code>&nbsp;&nbsp;&nbsp;&nbsp;ports:</code> | 发布宿主端口到容器端口；缩进决定该项属于哪个服务/抓取任务。 |
| L51 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- &quot;9090:9090&quot;</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;command:</code> | 覆盖镜像默认启动命令；缩进决定该项属于哪个服务/抓取任务。 |
| L53 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- &#x27;--config.file=/etc/prometheus/prometheus.yml&#x27;</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- &#x27;--storage.tsdb.path=/prometheus&#x27;</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- &#x27;--storage.tsdb.retention.time=200h&#x27;</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- &#x27;--web.enable-lifecycle&#x27;</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L57 | <code>&nbsp;&nbsp;&nbsp;&nbsp;volumes:</code> | 定义挂载；根级同名键声明命名卷；缩进决定该项属于哪个服务/抓取任务。 |
| L58 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- ./config/prometheus.yml:/etc/prometheus/prometheus.yml:ro</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L59 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- prometheus-data:/prometheus</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L60 | <code>&nbsp;&nbsp;&nbsp;&nbsp;restart: unless-stopped</code> | 容器退出后的重启策略；缩进决定该项属于哪个服务/抓取任务。 |
| L61 | <code>&nbsp;&nbsp;&nbsp;&nbsp;networks:</code> | 指定服务所属网络；根级声明网络；缩进决定该项属于哪个服务/抓取任务。 |
| L62 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- echomind-network</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L63 | <code>&nbsp;&nbsp;&nbsp;&nbsp;healthcheck:</code> | 定义依赖可用性探测；缩进决定该项属于哪个服务/抓取任务。 |
| L64 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;test: [&quot;CMD-SHELL&quot;, &quot;wget -q --spider http://localhost:9090/-/healthy &#124;&#124; exit 1&quot;]</code> | 健康检查执行的命令；缩进决定该项属于哪个服务/抓取任务。 |
| L65 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;interval: 30s</code> | 健康检查周期；缩进决定该项属于哪个服务/抓取任务。 |
| L66 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;timeout: 10s</code> | 单次检查超时；缩进决定该项属于哪个服务/抓取任务。 |
| L67 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;retries: 3</code> | 连续失败次数阈值；缩进决定该项属于哪个服务/抓取任务。 |
| L68 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;start_period: 10s</code> | 启动宽限期；缩进决定该项属于哪个服务/抓取任务。 |
| L69 | （空行） | 空行/展示分隔。 |
| L70 | <code>&nbsp;&nbsp;# ── EchoMind 主应用 ─────────────────────────────────────────────────────────</code> | 注释/说明：── EchoMind 主应用 ───────────────────────────────────────────────────────── |
| L71 | <code>&nbsp;&nbsp;echomind:</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;build:</code> | 声明本地构建参数；缩进决定该项属于哪个服务/抓取任务。 |
| L73 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;context: .</code> | Docker构建上下文目录；缩进决定该项属于哪个服务/抓取任务。 |
| L74 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dockerfile: Dockerfile</code> | 使用的构建文件；缩进决定该项属于哪个服务/抓取任务。 |
| L75 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;target: production</code> | **关键：**明确选 production，避免 Dockerfile 最后 development 阶段成为默认。 |
| L76 | <code>&nbsp;&nbsp;&nbsp;&nbsp;container_name: echomind-app</code> | 固定容器名称，运维脚本也依赖此名字；缩进决定该项属于哪个服务/抓取任务。 |
| L77 | <code>&nbsp;&nbsp;&nbsp;&nbsp;ports:</code> | 发布宿主端口到容器端口；缩进决定该项属于哪个服务/抓取任务。 |
| L78 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- &quot;8000:8000&quot;</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L79 | <code>&nbsp;&nbsp;&nbsp;&nbsp;env_file:</code> | 将此环境文件载入容器；缩进决定该项属于哪个服务/抓取任务。 |
| L80 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- .env</code> | **关键：**将 .env 变量注入应用容器；这一步不会自动把 localhost 改成服务名。 |

### L81 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L81 | <code>&nbsp;&nbsp;&nbsp;&nbsp;environment:</code> | 注入变量，应用同名值覆盖env_file；缩进决定该项属于哪个服务/抓取任务。 |
| L82 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 容器内固定值，覆盖 .env 中的本地路径</code> | 注释/说明：容器内固定值，覆盖 .env 中的本地路径 |
| L83 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- REDIS_URL=redis://:${REDIS_PASSWORD:-echomind123}@redis:6379/0</code> | **关键：**容器内 Redis 连接用服务名并带密码。 |
| L84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- CHROMA_PERSIST_DIRECTORY=/app/data/chroma</code> | **关键：**这是本地 fallback 路径，不是覆盖 CHROMA_HOST。 |
| L85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- EVAL_BASELINE_PATH=/app/data/eval/baseline.json</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L86 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- ECHOMIND_SKILLS_DIR=/app/skills</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;volumes:</code> | 定义挂载；根级同名键声明命名卷；缩进决定该项属于哪个服务/抓取任务。 |
| L88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- ./data/chroma:/app/data/chroma</code> | **关键：**应用本地 Chroma 文件绑定到宿主；和独立 chromadb-data 卷不是同一个存储。 |
| L89 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- ./data/eval:/app/data/eval</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- ./skills:/app/skills</code> | **关键：**挂载 Skills 使宿主修改可被 reload 读取。 |
| L91 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- ./logs:/app/logs</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L92 | <code>&nbsp;&nbsp;&nbsp;&nbsp;depends_on:</code> | 声明启动依赖关系；缩进决定该项属于哪个服务/抓取任务。 |
| L93 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;redis:</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L94 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;condition: service_healthy</code> | 等待依赖满足指定条件；缩进决定该项属于哪个服务/抓取任务。 |
| L95 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;chromadb:</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L96 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;condition: service_healthy</code> | 等待依赖满足指定条件；缩进决定该项属于哪个服务/抓取任务。 |
| L97 | <code>&nbsp;&nbsp;&nbsp;&nbsp;restart: unless-stopped</code> | 容器退出后的重启策略；缩进决定该项属于哪个服务/抓取任务。 |
| L98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;networks:</code> | 指定服务所属网络；根级声明网络；缩进决定该项属于哪个服务/抓取任务。 |
| L99 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- echomind-network</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L100 | <code>&nbsp;&nbsp;&nbsp;&nbsp;healthcheck:</code> | 定义依赖可用性探测；缩进决定该项属于哪个服务/抓取任务。 |
| L101 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;test: [&quot;CMD-SHELL&quot;, &quot;curl -sf http://localhost:8000/health &#124;&#124; exit 1&quot;]</code> | 健康检查执行的命令；缩进决定该项属于哪个服务/抓取任务。 |
| L102 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;interval: 30s</code> | 健康检查周期；缩进决定该项属于哪个服务/抓取任务。 |
| L103 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;timeout: 10s</code> | 单次检查超时；缩进决定该项属于哪个服务/抓取任务。 |
| L104 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;retries: 3</code> | 连续失败次数阈值；缩进决定该项属于哪个服务/抓取任务。 |
| L105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;start_period: 90s</code> | 启动宽限期；缩进决定该项属于哪个服务/抓取任务。 |
| L106 | （空行） | 空行/展示分隔。 |
| L107 | <code>&nbsp;&nbsp;# ── Nginx 反向代理 ──────────────────────────────────────────────────────────</code> | 注释/说明：── Nginx 反向代理 ────────────────────────────────────────────────────────── |
| L108 | <code>&nbsp;&nbsp;nginx:</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L109 | <code>&nbsp;&nbsp;&nbsp;&nbsp;image: nginx:alpine</code> | 从镜像名与标签选择容器内容；缩进决定该项属于哪个服务/抓取任务。 |
| L110 | <code>&nbsp;&nbsp;&nbsp;&nbsp;container_name: echomind-nginx</code> | 固定容器名称，运维脚本也依赖此名字；缩进决定该项属于哪个服务/抓取任务。 |
| L111 | <code>&nbsp;&nbsp;&nbsp;&nbsp;ports:</code> | 发布宿主端口到容器端口；缩进决定该项属于哪个服务/抓取任务。 |
| L112 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- &quot;80:80&quot;</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;volumes:</code> | 定义挂载；根级同名键声明命名卷；缩进决定该项属于哪个服务/抓取任务。 |
| L114 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- ./config/nginx/nginx.conf:/etc/nginx/nginx.conf:ro</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- nginx-logs:/var/log/nginx</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;depends_on:</code> | 声明启动依赖关系；缩进决定该项属于哪个服务/抓取任务。 |
| L117 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;echomind:</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L118 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;condition: service_healthy</code> | 等待依赖满足指定条件；缩进决定该项属于哪个服务/抓取任务。 |
| L119 | <code>&nbsp;&nbsp;&nbsp;&nbsp;restart: unless-stopped</code> | 容器退出后的重启策略；缩进决定该项属于哪个服务/抓取任务。 |
| L120 | <code>&nbsp;&nbsp;&nbsp;&nbsp;networks:</code> | 指定服务所属网络；根级声明网络；缩进决定该项属于哪个服务/抓取任务。 |

### L121 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L121 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- echomind-network</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L122 | <code>&nbsp;&nbsp;&nbsp;&nbsp;healthcheck:</code> | 定义依赖可用性探测；缩进决定该项属于哪个服务/抓取任务。 |
| L123 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;test: [&quot;CMD-SHELL&quot;, &quot;wget -q --spider http://localhost/health &#124;&#124; exit 1&quot;]</code> | 健康检查执行的命令；缩进决定该项属于哪个服务/抓取任务。 |
| L124 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;interval: 30s</code> | 健康检查周期；缩进决定该项属于哪个服务/抓取任务。 |
| L125 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;timeout: 10s</code> | 单次检查超时；缩进决定该项属于哪个服务/抓取任务。 |
| L126 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;retries: 3</code> | 连续失败次数阈值；缩进决定该项属于哪个服务/抓取任务。 |
| L127 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;start_period: 10s</code> | 启动宽限期；缩进决定该项属于哪个服务/抓取任务。 |
| L128 | （空行） | 空行/展示分隔。 |
| L129 | <code># ── 网络 ────────────────────────────────────────────────────────────────────</code> | 注释/说明：── 网络 ──────────────────────────────────────────────────────────────────── |
| L130 | <code>networks:</code> | 指定服务所属网络；根级声明网络；缩进决定该项属于哪个服务/抓取任务。 |
| L131 | <code>&nbsp;&nbsp;echomind-network:</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L132 | <code>&nbsp;&nbsp;&nbsp;&nbsp;driver: bridge</code> | 网络驱动；缩进决定该项属于哪个服务/抓取任务。 |
| L133 | <code>&nbsp;&nbsp;&nbsp;&nbsp;ipam:</code> | 容器地址分配配置；缩进决定该项属于哪个服务/抓取任务。 |
| L134 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;config:</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L135 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- subnet: 172.28.0.0/16</code> | **关键：**Nginx metrics allow 使用相同网段；改网段时需要同步。 |
| L136 | （空行） | 空行/展示分隔。 |
| L137 | <code># ── 数据卷 ──────────────────────────────────────────────────────────────────</code> | 注释/说明：── 数据卷 ────────────────────────────────────────────────────────────────── |
| L138 | <code>volumes:</code> | 定义挂载；根级同名键声明命名卷；缩进决定该项属于哪个服务/抓取任务。 |
| L139 | <code>&nbsp;&nbsp;redis-data:</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L140 | <code>&nbsp;&nbsp;chromadb-data:</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L141 | <code>&nbsp;&nbsp;prometheus-data:</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L142 | <code>&nbsp;&nbsp;nginx-logs:</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |

## 结合全项目：设计缺口与增强方向

- environment 覆盖了 Redis URL 和存储路径，却没有覆盖 CHROMA_HOST/CHROMA_PORT。按 .env.example 的 localhost:8001 启动应用容器，会连自己而非 chromadb:8000，可能触发本地降级。README 关于“已覆盖 Chroma 地址”的说法不成立。
- 同时存在 Chroma 服务命名卷与应用本地 fallback 绑定目录，需要记录实际使用后端，否则备份可能拿错数据。
- 当前没有 Grafana/Alertmanager 服务；不因模板有用户名密码或脚本创建目录就认为已部署。
- 应用端口 8000 直接发布，外部可绕过 Nginx 的限流/metrics 访问限制；固定 container_name 也限制横向多副本模式。

**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。
