# run-image.sh 解读

## 输入、输出与流向

**定位：** 只运行一个应用镜像的便捷脚本。

**输入：** run/run-dev/run-test/run-prod 等子命令、端口/目录/环境文件/名称参数。

**输出 / 副作用：** docker run 命令与容器状态；可能先停止删除同名容器。

**流向：** main→run_container 解析参数→拼端口/卷/env→按模式调整→删除同名容器→eval docker run。

[返回阅读入口](../README.md) · [对照原文件](../../run-image.sh)

当前工作区快照：355 行。原始行号列对应原文件；空白和纯注释可略读。 SHA-256：`3dc430aa1c04f7e1a34292163cc7ecde518d2eef7b8a3f675333e4f176930aa7`。

## 按原行号阅读

读法：先看每个函数前的因果解释，再看逐行表。多行参数、词表、提示文本续行从属于起始语句；关键行另加粗说明。


### L1 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L1 | <code>#!/bin/bash</code> | 注释/说明：!/bin/bash |
| L2 | （空行） | 空行/展示分隔。 |
| L3 | <code># EchoMind 镜像运行脚本</code> | 注释/说明：EchoMind 镜像运行脚本 |
| L4 | <code># 提供多种运行配置选项</code> | 注释/说明：提供多种运行配置选项 |
| L5 | （空行） | 空行/展示分隔。 |
| L6 | <code>set -e</code> | 设置 Bash 执行策略；失败退出行为影响后续控制流。 |
| L7 | （空行） | 空行/展示分隔。 |
| L8 | <code># 配置</code> | 注释/说明：配置 |
| L9 | <code>IMAGE_NAME=&quot;echomind&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L10 | <code>CONTAINER_NAME=&quot;echomind-app&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L11 | <code>VERSION=${VERSION:-latest}</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L12 | <code>REGISTRY=&quot;&quot;  # 如果镜像在私有仓库，设置为 registry.example.com/</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L13 | （空行） | 空行/展示分隔。 |
| L14 | <code># 默认端口映射</code> | 注释/说明：默认端口映射 |
| L15 | <code>API_PORT=8000</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L16 | <code>PROMETHEUS_PORT=9090</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L17 | （空行） | 空行/展示分隔。 |
| L18 | <code># 默认卷映射</code> | 注释/说明：默认卷映射 |
| L19 | <code>DATA_DIR=&quot;./data&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L20 | <code>LOGS_DIR=&quot;./logs&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L21 | <code>CONFIG_DIR=&quot;./config&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L22 | （空行） | 空行/展示分隔。 |
| L23 | <code># 颜色定义</code> | 注释/说明：颜色定义 |
| L24 | <code>GREEN=&#x27;\033[0;32m&#x27;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L25 | <code>YELLOW=&#x27;\033[1;33m&#x27;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L26 | <code>RED=&#x27;\033[0;31m&#x27;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L27 | <code>NC=&#x27;\033[0m&#x27;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L28 | （空行） | 空行/展示分隔。 |
| L29 | <code>print_info() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L30 | <code>&nbsp;&nbsp;&nbsp;&nbsp;echo -e &quot;${GREEN}[INFO]${NC} $1&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L31 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L32 | （空行） | 空行/展示分隔。 |
| L33 | <code>print_warn() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L34 | <code>&nbsp;&nbsp;&nbsp;&nbsp;echo -e &quot;${YELLOW}[WARN]${NC} $1&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L35 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L36 | （空行） | 空行/展示分隔。 |
| L37 | <code>print_error() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L38 | <code>&nbsp;&nbsp;&nbsp;&nbsp;echo -e &quot;${RED}[ERROR]${NC} $1&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L39 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L40 | （空行） | 空行/展示分隔。 |

### L41 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L41 | <code>show_help() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L42 | <code>&nbsp;&nbsp;&nbsp;&nbsp;cat &lt;&lt; EOF</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L43 | <code>EchoMind Docker 镜像运行工具</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L44 | （空行） | 空行/展示分隔。 |
| L45 | <code>用法: ./run-image.sh [命令] [选项]</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L46 | （空行） | 空行/展示分隔。 |
| L47 | <code>命令:</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L48 | <code>&nbsp;&nbsp;&nbsp;&nbsp;run             运行容器（默认模式）</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L49 | <code>&nbsp;&nbsp;&nbsp;&nbsp;run-dev         运行开发模式容器</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L50 | <code>&nbsp;&nbsp;&nbsp;&nbsp;run-test        运行测试容器</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L51 | <code>&nbsp;&nbsp;&nbsp;&nbsp;stop            停止容器</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;restart         重启容器</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L53 | <code>&nbsp;&nbsp;&nbsp;&nbsp;logs            查看容器日志</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;shell           进入容器 shell</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;status          查看容器状态</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;clean           清理容器和数据</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L57 | <code>&nbsp;&nbsp;&nbsp;&nbsp;help            显示此帮助</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L58 | （空行） | 空行/展示分隔。 |
| L59 | <code>选项:</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L60 | <code>&nbsp;&nbsp;&nbsp;&nbsp;--detach        后台运行</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L61 | <code>&nbsp;&nbsp;&nbsp;&nbsp;--ports         自定义端口映射</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L62 | <code>&nbsp;&nbsp;&nbsp;&nbsp;--env-file      指定环境变量文件</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L63 | <code>&nbsp;&nbsp;&nbsp;&nbsp;--volume        自定义卷映射</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L64 | <code>&nbsp;&nbsp;&nbsp;&nbsp;--name          自定义容器名称</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L65 | <code>&nbsp;&nbsp;&nbsp;&nbsp;--network       自定义网络</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L66 | （空行） | 空行/展示分隔。 |
| L67 | <code>示例:</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L68 | <code>&nbsp;&nbsp;&nbsp;&nbsp;./run-image.sh run</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L69 | <code>&nbsp;&nbsp;&nbsp;&nbsp;./run-image.sh run-dev --detach</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L70 | <code>&nbsp;&nbsp;&nbsp;&nbsp;./run-image.sh run --env-file .env.prod</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L71 | <code>&nbsp;&nbsp;&nbsp;&nbsp;./run-image.sh logs</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;./run-image.sh shell</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L73 | （空行） | 空行/展示分隔。 |
| L74 | <code>生产环境运行:</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L75 | <code>&nbsp;&nbsp;&nbsp;&nbsp;./run-image.sh run \\</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L76 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--env-file .env.prod \\</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L77 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--detach \\</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L78 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--restart unless-stopped</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L79 | （空行） | 空行/展示分隔。 |
| L80 | <code>开发环境运行:</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |

### L81 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L81 | <code>&nbsp;&nbsp;&nbsp;&nbsp;./run-image.sh run-dev \\</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L82 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--volume ./src:/app/src \\</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L83 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--detach</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L84 | （空行） | 空行/展示分隔。 |
| L85 | <code>EOF</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L86 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L87 | （空行） | 空行/展示分隔。 |
| L88 | <code># 创建必要的目录</code> | 注释/说明：创建必要的目录 |
| L89 | <code>ensure_directories() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;mkdir -p &quot;$DATA_DIR&quot;</code> | 文件系统操作：<code>mkdir -p &quot;$DATA_DIR&quot;</code>；仅解读，未执行。 |
| L91 | <code>&nbsp;&nbsp;&nbsp;&nbsp;mkdir -p &quot;$LOGS_DIR&quot;</code> | 文件系统操作：<code>mkdir -p &quot;$LOGS_DIR&quot;</code>；仅解读，未执行。 |
| L92 | <code>&nbsp;&nbsp;&nbsp;&nbsp;mkdir -p &quot;$CONFIG_DIR&quot;</code> | 文件系统操作：<code>mkdir -p &quot;$CONFIG_DIR&quot;</code>；仅解读，未执行。 |
| L93 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L94 | （空行） | 空行/展示分隔。 |
| L95 | <code># 运行容器</code> | 注释/说明：运行容器 |
| L96 | <code>run_container() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L97 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local mode=$1</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;shift &#124;&#124; true</code> | 移动位置参数，决定下一次 $1/$2 代表什么。 |
| L99 | （空行） | 空行/展示分隔。 |
| L100 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local detach=false</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L101 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local env_file=&quot;.env&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L102 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local custom_ports=&quot;&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L103 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local custom_volumes=&quot;&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L104 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local container_name=&quot;$CONTAINER_NAME&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local restart_policy=&quot;no&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L106 | （空行） | 空行/展示分隔。 |
| L107 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 解析参数</code> | 注释/说明：解析参数 |
| L108 | <code>&nbsp;&nbsp;&nbsp;&nbsp;while [[ $# -gt 0 ]]; do</code> | 按条件循环消费参数或数据。 |
| L109 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;case $1 in</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L110 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--detach&#124;-d)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L111 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;detach=true</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L112 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;shift</code> | 移动位置参数，决定下一次 $1/$2 代表什么。 |
| L113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L114 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--env-file)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;env_file=&quot;$2&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;shift 2</code> | 移动位置参数，决定下一次 $1/$2 代表什么。 |
| L117 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L118 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--ports&#124;-p)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L119 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;custom_ports=&quot;-p $2&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L120 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;shift 2</code> | 移动位置参数，决定下一次 $1/$2 代表什么。 |

### L121 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L121 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L122 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--volume&#124;-v)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L123 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;custom_volumes=&quot;$custom_volumes -v $2&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L124 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;shift 2</code> | 移动位置参数，决定下一次 $1/$2 代表什么。 |
| L125 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L126 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--name)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L127 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;container_name=&quot;$2&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L128 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;shift 2</code> | 移动位置参数，决定下一次 $1/$2 代表什么。 |
| L129 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L130 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--restart)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L131 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;restart_policy=&quot;$2&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L132 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;shift 2</code> | 移动位置参数，决定下一次 $1/$2 代表什么。 |
| L133 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L134 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*)</code> | **关键：**未知选项直接忽略，所以帮助里的 --network 不会生效。 |
| L135 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;shift</code> | 移动位置参数，决定下一次 $1/$2 代表什么。 |
| L136 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L137 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;esac</code> | 结束条件/循环/分支/函数结构。 |
| L138 | <code>&nbsp;&nbsp;&nbsp;&nbsp;done</code> | 结束条件/循环/分支/函数结构。 |
| L139 | （空行） | 空行/展示分隔。 |
| L140 | <code>&nbsp;&nbsp;&nbsp;&nbsp;ensure_directories</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L141 | （空行） | 空行/展示分隔。 |
| L142 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 检查环境文件</code> | 注释/说明：检查环境文件 |
| L143 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if [ ! -f &quot;$env_file&quot; ]; then</code> | 判断文件、参数或命令结果，选择后续操作。 |
| L144 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_warn &quot;环境文件 $env_file 不存在，使用默认配置&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;env_file=&quot;&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L146 | <code>&nbsp;&nbsp;&nbsp;&nbsp;else</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L147 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;env_file=&quot;--env-file $env_file&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L148 | <code>&nbsp;&nbsp;&nbsp;&nbsp;fi</code> | 结束条件/循环/分支/函数结构。 |
| L149 | （空行） | 空行/展示分隔。 |
| L150 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 基础配置</code> | 注释/说明：基础配置 |
| L151 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local image_tag=&quot;${REGISTRY}${IMAGE_NAME}:${VERSION}&quot;</code> | **关键：**三种模式共用这个镜像标签，没有模式到镜像映射。 |
| L152 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local default_ports=&quot;-p ${API_PORT}:8000 -p ${PROMETHEUS_PORT}:9090&quot;</code> | **关键：**默认容器指标端口写死 9090，不读取 env_file 中的实际监听值。 |
| L153 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local default_volumes=&quot;-v ${DATA_DIR}:/app/data -v ${LOGS_DIR}:/app/logs -v ${CONFIG_DIR}:/app/config&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L154 | （空行） | 空行/展示分隔。 |
| L155 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 根据模式调整配置</code> | 注释/说明：根据模式调整配置 |
| L156 | <code>&nbsp;&nbsp;&nbsp;&nbsp;case $mode in</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L157 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;dev)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L158 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;运行开发模式容器&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L159 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;default_ports=&quot;$default_ports -p 5678:5678&quot;  # 添加调试端口</code> | **关键：**开放端口不代表 debugpy 在运行。 |
| L160 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;restart_policy=&quot;no&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |

### L161 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L161 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L162 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;test)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L163 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;运行测试容器&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L164 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;restart_policy=&quot;no&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L165 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L166 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;prod)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L167 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;运行生产模式容器&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L168 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;restart_policy=&quot;unless-stopped&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L169 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L170 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L171 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;运行标准容器&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L172 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L173 | <code>&nbsp;&nbsp;&nbsp;&nbsp;esac</code> | 结束条件/循环/分支/函数结构。 |
| L174 | （空行） | 空行/展示分隔。 |
| L175 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 构建运行命令</code> | 注释/说明：构建运行命令 |
| L176 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local run_cmd=&quot;docker run&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L177 | （空行） | 空行/展示分隔。 |
| L178 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if [ &quot;$detach&quot; = true ]; then</code> | 判断文件、参数或命令结果，选择后续操作。 |
| L179 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;run_cmd=&quot;$run_cmd -d&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L180 | <code>&nbsp;&nbsp;&nbsp;&nbsp;fi</code> | 结束条件/循环/分支/函数结构。 |
| L181 | （空行） | 空行/展示分隔。 |
| L182 | <code>&nbsp;&nbsp;&nbsp;&nbsp;run_cmd=&quot;$run_cmd --name $container_name&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L183 | <code>&nbsp;&nbsp;&nbsp;&nbsp;run_cmd=&quot;$run_cmd --restart $restart_policy&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L184 | <code>&nbsp;&nbsp;&nbsp;&nbsp;run_cmd=&quot;$run_cmd $default_ports $custom_ports&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L185 | <code>&nbsp;&nbsp;&nbsp;&nbsp;run_cmd=&quot;$run_cmd $default_volumes $custom_volumes&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L186 | <code>&nbsp;&nbsp;&nbsp;&nbsp;run_cmd=&quot;$run_cmd $env_file&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L187 | <code>&nbsp;&nbsp;&nbsp;&nbsp;run_cmd=&quot;$run_cmd $image_tag&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L188 | （空行） | 空行/展示分隔。 |
| L189 | <code>&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;启动容器: $container_name&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L190 | <code>&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;镜像: $image_tag&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L191 | （空行） | 空行/展示分隔。 |
| L192 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 检查容器是否已存在</code> | 注释/说明：检查容器是否已存在 |
| L193 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if docker ps -a --format &#x27;{{.Names}}&#x27; &#124; grep -q &quot;^${container_name}$&quot;; then</code> | 判断文件、参数或命令结果，选择后续操作。 |
| L194 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_warn &quot;容器 $container_name 已存在，先停止并删除&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L195 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;docker stop &quot;$container_name&quot; 2&gt;/dev/null &#124;&#124; true</code> | **关键：**有同名容器时自动停止，会中断其现有服务。 |
| L196 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;docker rm &quot;$container_name&quot; 2&gt;/dev/null &#124;&#124; true</code> | 调用 Docker 操作：<code>docker rm &quot;$container_name&quot; 2&gt;/dev/null &#124;&#124; true</code>；具体副作用须看命令。 |
| L197 | <code>&nbsp;&nbsp;&nbsp;&nbsp;fi</code> | 结束条件/循环/分支/函数结构。 |
| L198 | （空行） | 空行/展示分隔。 |
| L199 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 运行容器</code> | 注释/说明：运行容器 |
| L200 | <code>&nbsp;&nbsp;&nbsp;&nbsp;eval $run_cmd</code> | **关键：**字符串 eval 对空格路径和参数引用脆弱。 |

### L201 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L201 | （空行） | 空行/展示分隔。 |
| L202 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if [ $? -eq 0 ]; then</code> | 判断文件、参数或命令结果，选择后续操作。 |
| L203 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;✓ 容器启动成功&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L204 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;API地址: http://localhost:${API_PORT}&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L205 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;Prometheus: http://localhost:${PROMETHEUS_PORT}&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L206 | （空行） | 空行/展示分隔。 |
| L207 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if [ &quot;$detach&quot; = true ]; then</code> | 判断文件、参数或命令结果，选择后续操作。 |
| L208 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;容器在后台运行&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L209 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;查看日志: ./run-image.sh logs&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L210 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fi</code> | 结束条件/循环/分支/函数结构。 |
| L211 | <code>&nbsp;&nbsp;&nbsp;&nbsp;else</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L212 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_error &quot;✗ 容器启动失败&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L213 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;exit 1</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L214 | <code>&nbsp;&nbsp;&nbsp;&nbsp;fi</code> | 结束条件/循环/分支/函数结构。 |
| L215 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L216 | （空行） | 空行/展示分隔。 |
| L217 | <code># 停止容器</code> | 注释/说明：停止容器 |
| L218 | <code>stop_container() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L219 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local name=${1:-$CONTAINER_NAME}</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L220 | （空行） | 空行/展示分隔。 |
| L221 | <code>&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;停止容器: $name&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L222 | （空行） | 空行/展示分隔。 |
| L223 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if docker ps --format &#x27;{{.Names}}&#x27; &#124; grep -q &quot;^${name}$&quot;; then</code> | 判断文件、参数或命令结果，选择后续操作。 |
| L224 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;docker stop &quot;$name&quot;</code> | 调用 Docker 操作：<code>docker stop &quot;$name&quot;</code>；具体副作用须看命令。 |
| L225 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;✓ 容器已停止&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L226 | <code>&nbsp;&nbsp;&nbsp;&nbsp;else</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L227 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_warn &quot;容器 $name 未运行&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L228 | <code>&nbsp;&nbsp;&nbsp;&nbsp;fi</code> | 结束条件/循环/分支/函数结构。 |
| L229 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L230 | （空行） | 空行/展示分隔。 |
| L231 | <code># 重启容器</code> | 注释/说明：重启容器 |
| L232 | <code>restart_container() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L233 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local name=${1:-$CONTAINER_NAME}</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L234 | （空行） | 空行/展示分隔。 |
| L235 | <code>&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;重启容器: $name&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L236 | （空行） | 空行/展示分隔。 |
| L237 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if docker ps -a --format &#x27;{{.Names}}&#x27; &#124; grep -q &quot;^${name}$&quot;; then</code> | 判断文件、参数或命令结果，选择后续操作。 |
| L238 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;docker restart &quot;$name&quot;</code> | 调用 Docker 操作：<code>docker restart &quot;$name&quot;</code>；具体副作用须看命令。 |
| L239 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;✓ 容器已重启&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L240 | <code>&nbsp;&nbsp;&nbsp;&nbsp;else</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |

### L241 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L241 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_error &quot;容器 $name 不存在&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L242 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;exit 1</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L243 | <code>&nbsp;&nbsp;&nbsp;&nbsp;fi</code> | 结束条件/循环/分支/函数结构。 |
| L244 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L245 | （空行） | 空行/展示分隔。 |
| L246 | <code># 查看日志</code> | 注释/说明：查看日志 |
| L247 | <code>view_logs() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L248 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local name=${1:-$CONTAINER_NAME}</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L249 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local follow=${2:-true}</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L250 | （空行） | 空行/展示分隔。 |
| L251 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if [ &quot;$follow&quot; = &quot;true&quot; ]; then</code> | 判断文件、参数或命令结果，选择后续操作。 |
| L252 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;docker logs -f &quot;$name&quot;</code> | 调用 Docker 操作：<code>docker logs -f &quot;$name&quot;</code>；具体副作用须看命令。 |
| L253 | <code>&nbsp;&nbsp;&nbsp;&nbsp;else</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L254 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;docker logs &quot;$name&quot;</code> | 调用 Docker 操作：<code>docker logs &quot;$name&quot;</code>；具体副作用须看命令。 |
| L255 | <code>&nbsp;&nbsp;&nbsp;&nbsp;fi</code> | 结束条件/循环/分支/函数结构。 |
| L256 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L257 | （空行） | 空行/展示分隔。 |
| L258 | <code># 进入容器 shell</code> | 注释/说明：进入容器 shell |
| L259 | <code>enter_shell() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L260 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local name=${1:-$CONTAINER_NAME}</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L261 | （空行） | 空行/展示分隔。 |
| L262 | <code>&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;进入容器 shell: $name&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L263 | （空行） | 空行/展示分隔。 |
| L264 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if docker ps --format &#x27;{{.Names}}&#x27; &#124; grep -q &quot;^${name}$&quot;; then</code> | 判断文件、参数或命令结果，选择后续操作。 |
| L265 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;docker exec -it &quot;$name&quot; /bin/bash</code> | 调用 Docker 操作：<code>docker exec -it &quot;$name&quot; /bin/bash</code>；具体副作用须看命令。 |
| L266 | <code>&nbsp;&nbsp;&nbsp;&nbsp;else</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L267 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_error &quot;容器 $name 未运行&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L268 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;exit 1</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L269 | <code>&nbsp;&nbsp;&nbsp;&nbsp;fi</code> | 结束条件/循环/分支/函数结构。 |
| L270 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L271 | （空行） | 空行/展示分隔。 |
| L272 | <code># 查看状态</code> | 注释/说明：查看状态 |
| L273 | <code>show_status() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L274 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local name=${1:-$CONTAINER_NAME}</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L275 | （空行） | 空行/展示分隔。 |
| L276 | <code>&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;容器状态: $name&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L277 | （空行） | 空行/展示分隔。 |
| L278 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if docker ps -a --format &#x27;{{.Names}}&#x27; &#124; grep -q &quot;^${name}$&quot;; then</code> | 判断文件、参数或命令结果，选择后续操作。 |
| L279 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;docker ps -a --filter &quot;name=$name&quot; --format &quot;table {{.Names}}\t{{.Status}}\t{{.Ports}}&quot;</code> | 调用 Docker 操作：<code>docker ps -a --filter &quot;name=$name&quot; --format &quot;table {{.Names}}\t{{.Status}}\t{{.Ports}}&quot;</code>；具体副作用须看命令。 |
| L280 | <code>&nbsp;&nbsp;&nbsp;&nbsp;else</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |

### L281 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L281 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_warn &quot;容器 $name 不存在&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L282 | <code>&nbsp;&nbsp;&nbsp;&nbsp;fi</code> | 结束条件/循环/分支/函数结构。 |
| L283 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L284 | （空行） | 空行/展示分隔。 |
| L285 | <code># 清理容器</code> | 注释/说明：清理容器 |
| L286 | <code>clean_container() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L287 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local name=${1:-$CONTAINER_NAME}</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L288 | （空行） | 空行/展示分隔。 |
| L289 | <code>&nbsp;&nbsp;&nbsp;&nbsp;print_warn &quot;清理容器和数据卷&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L290 | （空行） | 空行/展示分隔。 |
| L291 | <code>&nbsp;&nbsp;&nbsp;&nbsp;read -p &quot;确认清理？这将删除容器和数据 (y/N): &quot; -n 1 -r</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L292 | <code>&nbsp;&nbsp;&nbsp;&nbsp;echo</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L293 | （空行） | 空行/展示分隔。 |
| L294 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if [[ $REPLY =~ ^[Yy]$ ]]; then</code> | 判断文件、参数或命令结果，选择后续操作。 |
| L295 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;docker stop &quot;$name&quot; 2&gt;/dev/null &#124;&#124; true</code> | 调用 Docker 操作：<code>docker stop &quot;$name&quot; 2&gt;/dev/null &#124;&#124; true</code>；具体副作用须看命令。 |
| L296 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;docker rm &quot;$name&quot; 2&gt;/dev/null &#124;&#124; true</code> | **关键：**这里只删除容器，不删除宿主绑定数据目录。 |
| L297 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;✓ 容器已清理&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L298 | <code>&nbsp;&nbsp;&nbsp;&nbsp;else</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L299 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;清理已取消&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L300 | <code>&nbsp;&nbsp;&nbsp;&nbsp;fi</code> | 结束条件/循环/分支/函数结构。 |
| L301 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L302 | （空行） | 空行/展示分隔。 |
| L303 | <code># 主函数</code> | 注释/说明：主函数 |
| L304 | <code>main() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L305 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local command=${1:-run}</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L306 | <code>&nbsp;&nbsp;&nbsp;&nbsp;shift &#124;&#124; true</code> | 移动位置参数，决定下一次 $1/$2 代表什么。 |
| L307 | （空行） | 空行/展示分隔。 |
| L308 | <code>&nbsp;&nbsp;&nbsp;&nbsp;case $command in</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L309 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;run)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L310 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;run_container &quot;&quot; &quot;$@&quot;</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L311 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L312 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;run-dev)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L313 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;run_container &quot;dev&quot; &quot;$@&quot;</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L314 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L315 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;run-test)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L316 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;run_container &quot;test&quot; &quot;$@&quot;</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L317 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L318 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;run-prod)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L319 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;run_container &quot;prod&quot; &quot;$@&quot;</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L320 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |

### L321 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L321 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;stop)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L322 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;stop_container &quot;$1&quot;</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L323 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L324 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;restart)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L325 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;restart_container &quot;$1&quot;</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L326 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L327 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;logs)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L328 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;if [ &quot;$1&quot; = &quot;--no-follow&quot; ]; then</code> | 判断文件、参数或命令结果，选择后续操作。 |
| L329 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;view_logs &quot;$2&quot; &quot;false&quot;</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L330 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;else</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L331 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;view_logs &quot;$1&quot; &quot;true&quot;</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L332 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;fi</code> | 结束条件/循环/分支/函数结构。 |
| L333 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L334 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;shell)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L335 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;enter_shell &quot;$1&quot;</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L336 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L337 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;status)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L338 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;show_status &quot;$1&quot;</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L339 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L340 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;clean)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L341 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;clean_container &quot;$1&quot;</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L342 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L343 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;help&#124;--help&#124;-h)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L344 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;show_help</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L345 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L346 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L347 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_error &quot;未知命令: $command&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L348 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;show_help</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L349 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;exit 1</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L350 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L351 | <code>&nbsp;&nbsp;&nbsp;&nbsp;esac</code> | 结束条件/循环/分支/函数结构。 |
| L352 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L353 | （空行） | 空行/展示分隔。 |
| L354 | <code># 执行主函数</code> | 注释/说明：执行主函数 |
| L355 | <code>main &quot;$@&quot;</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |

## 结合全项目：设计缺口与增强方向

- 帮助写 --network，但参数解析没有该分支，容器不自动加入 Compose 网络；也不启动 Redis/Chroma。
- dev/test/prod 都使用同一 image_tag，dev 只是多映射 5678，没有选开发镜像或启动调试器；test 也没有自动运行测试。
- 默认把本地 9090 映射容器 9090，但 .env.example 的 PROMETHEUS_PORT=9091，且可能与独立 Prometheus 占用冲突。
- clean 文案说删除数据卷，实际只 stop/rm 容器，未删绑定目录或执行 rm -v；文字与副作用要分清。
- eval 与相对路径绑定使带空格目录容易出问题；本工作区路径恰有空格，不应盲目复制脚本运行。

**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。
