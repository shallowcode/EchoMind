# config/nginx/nginx.conf 解读

## 输入、输出与流向

**定位：** HTTP 网关：代理、基础 IP 限流和特定端点访问控制。

**输入：** 客户端 HTTP、Docker DNS 中 echomind 服务名；nginx 配置。

**输出 / 副作用：** 转发至 echomind:8000 的请求/响应、访问和错误日志、限流拒绝响应。

**流向：** listen 80→匹配 location→限流/头部/代理；metrics 单独网段控制；静态目录另走 alias。

[返回阅读入口](../../../README.md) · [对照原文件](../../../../config/nginx/nginx.conf)

当前工作区快照：155 行。原始行号列对应原文件；空白和纯注释可略读。 SHA-256：`58df9ca46ddf4589df63bc4537689e223f4c3d0025022cef63adf0a2ff41dbf0`。

## 按原行号阅读

读法：先看每个函数前的因果解释，再看逐行表。多行参数、词表、提示文本续行从属于起始语句；关键行另加粗说明。


### L1 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L1 | <code># Nginx 反向代理配置</code> | 注释/说明：Nginx 反向代理配置 |
| L2 | <code># 用于 EchoMind 智能客服系统的生产部署</code> | 注释/说明：用于 EchoMind 智能客服系统的生产部署 |
| L3 | （空行） | 空行/展示分隔。 |
| L4 | <code>user nginx;</code> | 工作进程身份，控制文件访问权限；具体取值见原行。 |
| L5 | <code>worker_processes auto;</code> | 工作进程数，auto让Nginx按环境决定；具体取值见原行。 |
| L6 | <code>error_log /var/log/nginx/error.log warn;</code> | 错误日志路径和等级；具体取值见原行。 |
| L7 | <code>pid /var/run/nginx.pid;</code> | 主进程PID文件位置；具体取值见原行。 |
| L8 | （空行） | 空行/展示分隔。 |
| L9 | <code>events {</code> | 事件处理配置块；具体取值见原行。 |
| L10 | <code>&nbsp;&nbsp;&nbsp;&nbsp;worker_connections 1024;</code> | 每个工作进程连接数上限；具体取值见原行。 |
| L11 | <code>&nbsp;&nbsp;&nbsp;&nbsp;use epoll;</code> | 选择事件通知机制，此处epoll对应Linux；具体取值见原行。 |
| L12 | <code>&nbsp;&nbsp;&nbsp;&nbsp;multi_accept on;</code> | 一次事件尽量接受多条新连接；具体取值见原行。 |
| L13 | <code>}</code> | Nginx多行参数或配置块边界，继承当前块的语义。 |
| L14 | （空行） | 空行/展示分隔。 |
| L15 | <code>http {</code> | HTTP配置范围；具体取值见原行。 |
| L16 | <code>&nbsp;&nbsp;&nbsp;&nbsp;include /etc/nginx/mime.types;</code> | 加载其他配置文件；具体取值见原行。 |
| L17 | <code>&nbsp;&nbsp;&nbsp;&nbsp;default_type application/octet-stream;</code> | 无匹配MIME类型时的默认响应类型；具体取值见原行。 |
| L18 | （空行） | 空行/展示分隔。 |
| L19 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 日志格式</code> | 注释/说明：日志格式 |
| L20 | <code>&nbsp;&nbsp;&nbsp;&nbsp;log_format main &#x27;$remote_addr - $remote_user [$time_local] &quot;$request&quot; &#x27;</code> | 定义访问日志字段格式；具体取值见原行。 |
| L21 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#x27;$status $body_bytes_sent &quot;$http_referer&quot; &#x27;</code> | Nginx多行参数或配置块边界，继承当前块的语义。 |
| L22 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&#x27;&quot;$http_user_agent&quot; &quot;$http_x_forwarded_for&quot;&#x27;;</code> | Nginx多行参数或配置块边界，继承当前块的语义。 |
| L23 | （空行） | 空行/展示分隔。 |
| L24 | <code>&nbsp;&nbsp;&nbsp;&nbsp;access_log /var/log/nginx/access.log main;</code> | 访问日志位置或关闭此位置的访问日志；具体取值见原行。 |
| L25 | （空行） | 空行/展示分隔。 |
| L26 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 性能优化</code> | 注释/说明：性能优化 |
| L27 | <code>&nbsp;&nbsp;&nbsp;&nbsp;sendfile on;</code> | 使用内核文件发送能力；具体取值见原行。 |
| L28 | <code>&nbsp;&nbsp;&nbsp;&nbsp;tcp_nopush on;</code> | 调整TCP发送，适配文件传输；具体取值见原行。 |
| L29 | <code>&nbsp;&nbsp;&nbsp;&nbsp;tcp_nodelay on;</code> | 减少小数据包等待；具体取值见原行。 |
| L30 | <code>&nbsp;&nbsp;&nbsp;&nbsp;keepalive_timeout 65;</code> | 客户端空闲长连接保留时间；具体取值见原行。 |
| L31 | <code>&nbsp;&nbsp;&nbsp;&nbsp;types_hash_max_size 2048;</code> | MIME映射哈希表容量；具体取值见原行。 |
| L32 | <code>&nbsp;&nbsp;&nbsp;&nbsp;client_max_body_size 10M;</code> | **关键：**网关层请求体上限；应用直连时仍依赖 Python 检查。 |
| L33 | （空行） | 空行/展示分隔。 |
| L34 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# Gzip 压缩</code> | 注释/说明：Gzip 压缩 |
| L35 | <code>&nbsp;&nbsp;&nbsp;&nbsp;gzip on;</code> | 响应压缩总开关；具体取值见原行。 |
| L36 | <code>&nbsp;&nbsp;&nbsp;&nbsp;gzip_vary on;</code> | 根据Accept-Encoding区分缓存表示；具体取值见原行。 |
| L37 | <code>&nbsp;&nbsp;&nbsp;&nbsp;gzip_proxied any;</code> | 决定哪些被代理响应可以压缩；具体取值见原行。 |
| L38 | <code>&nbsp;&nbsp;&nbsp;&nbsp;gzip_comp_level 6;</code> | 压缩等级与CPU成本取舍；具体取值见原行。 |
| L39 | <code>&nbsp;&nbsp;&nbsp;&nbsp;gzip_types text/plain text/css text/xml text/javascript</code> | 启用压缩的内容类型列表；具体取值见原行。 |
| L40 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;application/json application/javascript application/xml+rss</code> | Nginx多行参数或配置块边界，继承当前块的语义。 |

### L41 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L41 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;application/rss+xml font/truetype font/opentype</code> | Nginx多行参数或配置块边界，继承当前块的语义。 |
| L42 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;application/vnd.ms-fontobject image/svg+xml;</code> | Nginx多行参数或配置块边界，继承当前块的语义。 |
| L43 | （空行） | 空行/展示分隔。 |
| L44 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 上游服务器配置</code> | 注释/说明：上游服务器配置 |
| L45 | <code>&nbsp;&nbsp;&nbsp;&nbsp;upstream echomind_backend {</code> | 命名一组后端服务供proxy_pass引用；具体取值见原行。 |
| L46 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;least_conn;</code> | 选择当前连接少的上游；现配置只有一个候选；具体取值见原行。 |
| L47 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;server echomind:8000 max_fails=3 fail_timeout=30s;</code> | **关键：**只有一个上游 server，所以 least_conn 当前没有分配选择。 |
| L48 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;keepalive 32;</code> | 上游连接池缓存的空闲连接数量；具体取值见原行。 |
| L49 | <code>&nbsp;&nbsp;&nbsp;&nbsp;}</code> | Nginx多行参数或配置块边界，继承当前块的语义。 |
| L50 | （空行） | 空行/展示分隔。 |
| L51 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 限流配置</code> | 注释/说明：限流配置 |
| L52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;</code> | **关键：**按来源 IP 10 次/秒的区域，具体生效还需 location 的 limit_req。 |
| L53 | <code>&nbsp;&nbsp;&nbsp;&nbsp;limit_conn_zone $binary_remote_addr zone=conn_limit:10m;</code> | 声明并发连接统计共享区；具体取值见原行。 |
| L54 | （空行） | 空行/展示分隔。 |
| L55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# HTTP 服务器配置</code> | 注释/说明：HTTP 服务器配置 |
| L56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;server {</code> | 上游块内为后端地址，http块内则开始虚拟主机配置；具体取值见原行。 |
| L57 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;listen 80;</code> | 监听端口；具体取值见原行。 |
| L58 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;server_name localhost;</code> | 虚拟主机名称匹配；具体取值见原行。 |
| L59 | （空行） | 空行/展示分隔。 |
| L60 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 重定向到 HTTPS (生产环境)</code> | 注释/说明：重定向到 HTTPS (生产环境) |
| L61 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# return 301 https://$server_name$request_uri;</code> | 注释/说明：return 301 https://$server_name$request_uri; |
| L62 | （空行） | 空行/展示分隔。 |
| L63 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 安全头</code> | 注释/说明：安全头 |
| L64 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;add_header X-Frame-Options &quot;SAMEORIGIN&quot; always;</code> | 给响应添加指定头；always使错误响应也可带该头；具体取值见原行。 |
| L65 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;add_header X-Content-Type-Options &quot;nosniff&quot; always;</code> | 给响应添加指定头；always使错误响应也可带该头；具体取值见原行。 |
| L66 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;add_header X-XSS-Protection &quot;1; mode=block&quot; always;</code> | 给响应添加指定头；always使错误响应也可带该头；具体取值见原行。 |
| L67 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;add_header Referrer-Policy &quot;no-referrer-when-downgrade&quot; always;</code> | 给响应添加指定头；always使错误响应也可带该头；具体取值见原行。 |
| L68 | （空行） | 空行/展示分隔。 |
| L69 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# API 路由。FastAPI 真实接口没有 /api 前缀，因此这里代理所有未单独匹配的路径，</code> | 注释/说明：API 路由。FastAPI 真实接口没有 /api 前缀，因此这里代理所有未单独匹配的路径， |
| L70 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 保证 /chat、/search、/knowledge/*、/eval/run 以及 Swagger Try it out 都可用。</code> | 注释/说明：保证 /chat、/search、/knowledge/*、/eval/run 以及 Swagger Try it out 都可用。 |
| L71 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;location / {</code> | 按URL路径匹配本配置块；具体取值见原行。 |
| L72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;limit_req zone=api_limit burst=20 nodelay;</code> | **关键：**允许 20 请求突发并直接处理，超限将被网关拒绝。 |
| L73 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;limit_conn conn_limit 10;</code> | 对指定统计区域限制并发连接；具体取值见原行。 |
| L74 | （空行） | 空行/展示分隔。 |
| L75 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_pass http://echomind_backend;</code> | 把请求转发到命名后端或URL；具体取值见原行。 |
| L76 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_http_version 1.1;</code> | 访问上游时使用的HTTP版本；具体取值见原行。 |
| L77 | （空行） | 空行/展示分隔。 |
| L78 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 代理头设置</code> | 注释/说明：代理头设置 |
| L79 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_set_header Host $host;</code> | 向上游传递指定请求头；具体取值见原行。 |
| L80 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_set_header X-Real-IP $remote_addr;</code> | 向上游传递指定请求头；具体取值见原行。 |

### L81 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L81 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;</code> | 向上游传递指定请求头；具体取值见原行。 |
| L82 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_set_header X-Forwarded-Proto $scheme;</code> | 向上游传递指定请求头；具体取值见原行。 |
| L83 | （空行） | 空行/展示分隔。 |
| L84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 超时设置</code> | 注释/说明：超时设置 |
| L85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_connect_timeout 60s;</code> | 建立上游连接的等待上限；具体取值见原行。 |
| L86 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_send_timeout 60s;</code> | 向上游发送请求的等待上限；具体取值见原行。 |
| L87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_read_timeout 60s;</code> | **关键：**60 秒读超时不是整个 Agent 链路统一 deadline。 |
| L88 | （空行） | 空行/展示分隔。 |
| L89 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 缓冲设置</code> | 注释/说明：缓冲设置 |
| L90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_buffering on;</code> | **关键：**响应缓冲启用；未来流式输出需重新设计。 |
| L91 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_buffer_size 4k;</code> | 读取响应初始数据的缓冲大小；具体取值见原行。 |
| L92 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_buffers 8 4k;</code> | 响应缓冲数量与单块大小；具体取值见原行。 |
| L93 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_busy_buffers_size 8k;</code> | 忙碌响应缓冲区大小限制；具体取值见原行。 |
| L94 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | Nginx多行参数或配置块边界，继承当前块的语义。 |
| L95 | （空行） | 空行/展示分隔。 |
| L96 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 健康检查端点</code> | 注释/说明：健康检查端点 |
| L97 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;location /health {</code> | 按URL路径匹配本配置块；具体取值见原行。 |
| L98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_pass http://echomind_backend/health;</code> | 把请求转发到命名后端或URL；具体取值见原行。 |
| L99 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;access_log off;</code> | 访问日志位置或关闭此位置的访问日志；具体取值见原行。 |
| L100 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | Nginx多行参数或配置块边界，继承当前块的语义。 |
| L101 | （空行） | 空行/展示分隔。 |
| L102 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Prometheus 指标端点</code> | 注释/说明：Prometheus 指标端点 |
| L103 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;location /metrics {</code> | 按URL路径匹配本配置块；具体取值见原行。 |
| L104 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_pass http://echomind_backend/metrics;</code> | 把请求转发到命名后端或URL；具体取值见原行。 |
| L105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 限制访问</code> | 注释/说明：限制访问 |
| L106 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;allow 127.0.0.1;</code> | 允许来源地址/网段；具体取值见原行。 |
| L107 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;allow 172.28.0.0/16;  # Docker 网络</code> | **关键：**只限制经 Nginx 的 /metrics；不能约束应用 8000 直连。 |
| L108 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;deny all;</code> | 拒绝指定来源；具体取值见原行。 |
| L109 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | Nginx多行参数或配置块边界，继承当前块的语义。 |
| L110 | （空行） | 空行/展示分隔。 |
| L111 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# 静态文件服务</code> | 注释/说明：静态文件服务 |
| L112 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;location /static/ {</code> | 按URL路径匹配本配置块；具体取值见原行。 |
| L113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;alias /app/static/;</code> | 将URL前缀映射到文件系统目录；具体取值见原行。 |
| L114 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;expires 30d;</code> | 设置静态缓存过期时间；具体取值见原行。 |
| L115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;add_header Cache-Control &quot;public, immutable&quot;;</code> | 给响应添加指定头；always使错误响应也可带该头；具体取值见原行。 |
| L116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | Nginx多行参数或配置块边界，继承当前块的语义。 |
| L117 | （空行） | 空行/展示分隔。 |
| L118 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Swagger UI</code> | 注释/说明：Swagger UI |
| L119 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;location /docs {</code> | 按URL路径匹配本配置块；具体取值见原行。 |
| L120 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_pass http://echomind_backend/docs;</code> | 把请求转发到命名后端或URL；具体取值见原行。 |

### L121 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L121 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | Nginx多行参数或配置块边界，继承当前块的语义。 |
| L122 | （空行） | 空行/展示分隔。 |
| L123 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;location /redoc {</code> | 按URL路径匹配本配置块；具体取值见原行。 |
| L124 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_pass http://echomind_backend/redoc;</code> | 把请求转发到命名后端或URL；具体取值见原行。 |
| L125 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | Nginx多行参数或配置块边界，继承当前块的语义。 |
| L126 | （空行） | 空行/展示分隔。 |
| L127 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;location /openapi.json {</code> | 按URL路径匹配本配置块；具体取值见原行。 |
| L128 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;proxy_pass http://echomind_backend/openapi.json;</code> | 把请求转发到命名后端或URL；具体取值见原行。 |
| L129 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | Nginx多行参数或配置块边界，继承当前块的语义。 |
| L130 | （空行） | 空行/展示分隔。 |
| L131 | <code>&nbsp;&nbsp;&nbsp;&nbsp;}</code> | Nginx多行参数或配置块边界，继承当前块的语义。 |
| L132 | （空行） | 空行/展示分隔。 |
| L133 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# HTTPS 服务器配置 (生产环境)</code> | 注释/说明：HTTPS 服务器配置 (生产环境) |
| L134 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# server {</code> | **关键：**下面全部是注释模板，不会启用 TLS。 |
| L135 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#     listen 443 ssl http2;</code> | 注释/说明：listen 443 ssl http2; |
| L136 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#     server_name your-domain.com;</code> | 注释/说明：server_name your-domain.com; |
| L137 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#</code> | 注释/说明： |
| L138 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#     # SSL 证书配置</code> | 注释/说明：# SSL 证书配置 |
| L139 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#     ssl_certificate /etc/nginx/ssl/cert.pem;</code> | 注释/说明：ssl_certificate /etc/nginx/ssl/cert.pem; |
| L140 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#     ssl_certificate_key /etc/nginx/ssl/key.pem;</code> | 注释/说明：ssl_certificate_key /etc/nginx/ssl/key.pem; |
| L141 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#     ssl_protocols TLSv1.2 TLSv1.3;</code> | 注释/说明：ssl_protocols TLSv1.2 TLSv1.3; |
| L142 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#     ssl_ciphers HIGH:!aNULL:!MD5;</code> | 注释/说明：ssl_ciphers HIGH:!aNULL:!MD5; |
| L143 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#     ssl_prefer_server_ciphers on;</code> | 注释/说明：ssl_prefer_server_ciphers on; |
| L144 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#</code> | 注释/说明： |
| L145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#     # SSL 会话缓存</code> | 注释/说明：# SSL 会话缓存 |
| L146 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#     ssl_session_cache shared:SSL:10m;</code> | 注释/说明：ssl_session_cache shared:SSL:10m; |
| L147 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#     ssl_session_timeout 10m;</code> | 注释/说明：ssl_session_timeout 10m; |
| L148 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#</code> | 注释/说明： |
| L149 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#     # HSTS (可选)</code> | 注释/说明：# HSTS (可选) |
| L150 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#     add_header Strict-Transport-Security &quot;max-age=31536000; includeSubDomains&quot; always;</code> | 注释/说明：add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always; |
| L151 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#</code> | 注释/说明： |
| L152 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#     # 其他配置与 HTTP 相同</code> | 注释/说明：# 其他配置与 HTTP 相同 |
| L153 | <code>&nbsp;&nbsp;&nbsp;&nbsp;#     # ...</code> | 注释/说明：# ... |
| L154 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# }</code> | 注释/说明：} |
| L155 | <code>}</code> | Nginx多行参数或配置块边界，继承当前块的语义。 |

## 结合全项目：设计缺口与增强方向

- 只有一个上游，least_conn 只是预备负载均衡配置；没有多应用副本。
- HTTPS 配置整段注释，当前只监听 80；示例知识宣称所有传输 TLS 与实际配置不符。
- 限流位于 location /，独立 location 不继承它；应用 8000 直连也能绕过网关。
- /static 指向 /app/static，但当前 Compose 未挂载该目录，仓库也没有前端静态资产服务实现。
- proxy_buffering on，且 API 没 SSE；不能称已支持流式 token 返回。

**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。
