# build-image.sh 解读

## 输入、输出与流向

**定位：** 封装 Docker 镜像构建、标签、推送与构建缓存清理。

**输入：** 命令行 command/--version/--registry/--platform/--no-cache、VERSION 环境变量。

**输出 / 副作用：** 本地镜像/标签，push 会写远程仓库，clean 会清构建缓存；终端日志与退出码。

**流向：** main→parse_args→对应函数→构造 docker 命令→eval；只是读此文件，不执行任何部署动作。

[返回阅读入口](../README.md) · [对照原文件](../../build-image.sh)

当前工作区快照：228 行。原始行号列对应原文件；空白和纯注释可略读。 SHA-256：`3e0edfbe434680fcc2c84e5b40534b300668adc26eeab4c035ecd4056879b052`。

## 按原行号阅读

读法：先看每个函数前的因果解释，再看逐行表。多行参数、词表、提示文本续行从属于起始语句；关键行另加粗说明。


### L1 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L1 | <code>#!/bin/bash</code> | 注释/说明：!/bin/bash |
| L2 | （空行） | 空行/展示分隔。 |
| L3 | <code># EchoMind 镜像构建脚本</code> | 注释/说明：EchoMind 镜像构建脚本 |
| L4 | <code># 提供多种构建选项供不同场景使用</code> | 注释/说明：提供多种构建选项供不同场景使用 |
| L5 | （空行） | 空行/展示分隔。 |
| L6 | <code>set -e</code> | **关键：**失败即退出；后面通过 $? 判断失败的代码不一定能够执行。 |
| L7 | （空行） | 空行/展示分隔。 |
| L8 | <code># 颜色定义</code> | 注释/说明：颜色定义 |
| L9 | <code>RED=&#x27;\033[0;31m&#x27;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L10 | <code>GREEN=&#x27;\033[0;32m&#x27;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L11 | <code>YELLOW=&#x27;\033[1;33m&#x27;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L12 | <code>BLUE=&#x27;\033[0;34m&#x27;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L13 | <code>NC=&#x27;\033[0m&#x27;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L14 | （空行） | 空行/展示分隔。 |
| L15 | <code># 配置</code> | 注释/说明：配置 |
| L16 | <code>IMAGE_NAME=&quot;echomind&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L17 | <code>REGISTRY=&quot;&quot;  # 如果需要推送到私有仓库，设置为 registry.example.com/</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L18 | <code>VERSION=${VERSION:-latest}</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L19 | <code>BUILD_ARGS=&quot;&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L20 | （空行） | 空行/展示分隔。 |
| L21 | <code>print_info() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L22 | <code>&nbsp;&nbsp;&nbsp;&nbsp;echo -e &quot;${GREEN}[INFO]${NC} $1&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L23 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L24 | （空行） | 空行/展示分隔。 |
| L25 | <code>print_warn() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L26 | <code>&nbsp;&nbsp;&nbsp;&nbsp;echo -e &quot;${YELLOW}[WARN]${NC} $1&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L27 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L28 | （空行） | 空行/展示分隔。 |
| L29 | <code>print_error() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L30 | <code>&nbsp;&nbsp;&nbsp;&nbsp;echo -e &quot;${RED}[ERROR]${NC} $1&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L31 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L32 | （空行） | 空行/展示分隔。 |
| L33 | <code>print_step() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L34 | <code>&nbsp;&nbsp;&nbsp;&nbsp;echo -e &quot;${BLUE}[STEP]${NC} $1&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L35 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L36 | （空行） | 空行/展示分隔。 |
| L37 | <code># 显示使用帮助</code> | 注释/说明：显示使用帮助 |
| L38 | <code>show_help() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L39 | <code>&nbsp;&nbsp;&nbsp;&nbsp;cat &lt;&lt; EOF</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L40 | <code>EchoMind Docker 镜像构建工具</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |

### L41 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L41 | （空行） | 空行/展示分隔。 |
| L42 | <code>用法: ./build-image.sh [命令] [选项]</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L43 | （空行） | 空行/展示分隔。 |
| L44 | <code>命令:</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L45 | <code>&nbsp;&nbsp;&nbsp;&nbsp;build           构建默认镜像</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L46 | <code>&nbsp;&nbsp;&nbsp;&nbsp;build-prod      构建生产镜像</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L47 | <code>&nbsp;&nbsp;&nbsp;&nbsp;build-dev       构建开发镜像</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L48 | <code>&nbsp;&nbsp;&nbsp;&nbsp;build-test      构建测试镜像</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L49 | <code>&nbsp;&nbsp;&nbsp;&nbsp;push            推送镜像到仓库</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L50 | <code>&nbsp;&nbsp;&nbsp;&nbsp;tag             为镜像添加标签</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L51 | <code>&nbsp;&nbsp;&nbsp;&nbsp;clean           清理构建缓存</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;help            显示此帮助</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L53 | （空行） | 空行/展示分隔。 |
| L54 | <code>选项:</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;--no-cache      禁用缓存构建</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;--platform      指定平台 (linux/amd64, linux/arm64)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L57 | <code>&nbsp;&nbsp;&nbsp;&nbsp;--registry      指定镜像仓库</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L58 | <code>&nbsp;&nbsp;&nbsp;&nbsp;--version       指定版本号</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L59 | （空行） | 空行/展示分隔。 |
| L60 | <code>示例:</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L61 | <code>&nbsp;&nbsp;&nbsp;&nbsp;./build-image.sh build-prod</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L62 | <code>&nbsp;&nbsp;&nbsp;&nbsp;./build-image.sh build --no-cache</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L63 | <code>&nbsp;&nbsp;&nbsp;&nbsp;./build-image.sh build --platform linux/amd64,linux/arm64</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L64 | <code>&nbsp;&nbsp;&nbsp;&nbsp;./build-image.sh push --registry my-registry.com</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L65 | <code>&nbsp;&nbsp;&nbsp;&nbsp;./build-image.sh tag --version v1.0.0</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L66 | （空行） | 空行/展示分隔。 |
| L67 | <code>EOF</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L68 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L69 | （空行） | 空行/展示分隔。 |
| L70 | <code># 构建镜像</code> | 注释/说明：构建镜像 |
| L71 | <code>build_image() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local target=$1</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L73 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local no_cache=$2</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L74 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local platforms=$3</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L75 | （空行） | 空行/展示分隔。 |
| L76 | <code>&nbsp;&nbsp;&nbsp;&nbsp;print_step &quot;开始构建镜像: ${IMAGE_NAME}:${VERSION}&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L77 | （空行） | 空行/展示分隔。 |
| L78 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 构建参数</code> | 注释/说明：构建参数 |
| L79 | <code>&nbsp;&nbsp;&nbsp;&nbsp;build_cmd=&quot;docker build&quot;</code> | **关键：**把命令保存在字符串而不是 argv 数组。 |
| L80 | （空行） | 空行/展示分隔。 |

### L81 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L81 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 添加目标</code> | 注释/说明：添加目标 |
| L82 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if [ -n &quot;$target&quot; ]; then</code> | 判断文件、参数或命令结果，选择后续操作。 |
| L83 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;build_cmd=&quot;$build_cmd --target $target&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;fi</code> | 结束条件/循环/分支/函数结构。 |
| L85 | （空行） | 空行/展示分隔。 |
| L86 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 添加缓存选项</code> | 注释/说明：添加缓存选项 |
| L87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if [ &quot;$no_cache&quot; = &quot;true&quot; ]; then</code> | 判断文件、参数或命令结果，选择后续操作。 |
| L88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;build_cmd=&quot;$build_cmd --no-cache&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L89 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_warn &quot;禁用构建缓存&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;fi</code> | 结束条件/循环/分支/函数结构。 |
| L91 | （空行） | 空行/展示分隔。 |
| L92 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 添加多平台支持</code> | 注释/说明：添加多平台支持 |
| L93 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if [ -n &quot;$platforms&quot; ]; then</code> | 判断文件、参数或命令结果，选择后续操作。 |
| L94 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;build_cmd=&quot;$build_cmd --platform $platforms&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L95 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;构建平台: $platforms&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L96 | <code>&nbsp;&nbsp;&nbsp;&nbsp;fi</code> | 结束条件/循环/分支/函数结构。 |
| L97 | （空行） | 空行/展示分隔。 |
| L98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 添加构建参数</code> | 注释/说明：添加构建参数 |
| L99 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if [ -n &quot;$BUILD_ARGS&quot; ]; then</code> | 判断文件、参数或命令结果，选择后续操作。 |
| L100 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;build_cmd=&quot;$build_cmd $BUILD_ARGS&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L101 | <code>&nbsp;&nbsp;&nbsp;&nbsp;fi</code> | 结束条件/循环/分支/函数结构。 |
| L102 | （空行） | 空行/展示分隔。 |
| L103 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 执行构建</code> | 注释/说明：执行构建 |
| L104 | <code>&nbsp;&nbsp;&nbsp;&nbsp;full_tag=&quot;${REGISTRY}${IMAGE_NAME}:${VERSION}&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;build_cmd=&quot;$build_cmd -t $full_tag -t ${REGISTRY}${IMAGE_NAME}:latest .&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L106 | （空行） | 空行/展示分隔。 |
| L107 | <code>&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;执行命令: $build_cmd&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L108 | <code>&nbsp;&nbsp;&nbsp;&nbsp;eval $build_cmd</code> | **关键：**eval 二次解释参数，可能错误拆分或执行参数中的 shell 语法。 |
| L109 | （空行） | 空行/展示分隔。 |
| L110 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if [ $? -eq 0 ]; then</code> | 判断文件、参数或命令结果，选择后续操作。 |
| L111 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;✓ 镜像构建成功: $full_tag&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L112 | <code>&nbsp;&nbsp;&nbsp;&nbsp;else</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_error &quot;✗ 镜像构建失败&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L114 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;exit 1</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;fi</code> | 结束条件/循环/分支/函数结构。 |
| L116 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L117 | （空行） | 空行/展示分隔。 |
| L118 | <code># 推送镜像</code> | 注释/说明：推送镜像 |
| L119 | <code>push_image() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L120 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local registry=$1</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |

### L121 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L121 | （空行） | 空行/展示分隔。 |
| L122 | <code>&nbsp;&nbsp;&nbsp;&nbsp;if [ -n &quot;$registry&quot; ]; then</code> | 判断文件、参数或命令结果，选择后续操作。 |
| L123 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;REGISTRY=&quot;$registry/&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L124 | <code>&nbsp;&nbsp;&nbsp;&nbsp;fi</code> | 结束条件/循环/分支/函数结构。 |
| L125 | （空行） | 空行/展示分隔。 |
| L126 | <code>&nbsp;&nbsp;&nbsp;&nbsp;print_step &quot;推送镜像到仓库&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L127 | （空行） | 空行/展示分隔。 |
| L128 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 推送版本标签</code> | 注释/说明：推送版本标签 |
| L129 | <code>&nbsp;&nbsp;&nbsp;&nbsp;docker push ${REGISTRY}${IMAGE_NAME}:${VERSION}</code> | 调用 Docker 操作：<code>docker push ${REGISTRY}${IMAGE_NAME}:${VERSION}</code>；具体副作用须看命令。 |
| L130 | （空行） | 空行/展示分隔。 |
| L131 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 推送最新标签</code> | 注释/说明：推送最新标签 |
| L132 | <code>&nbsp;&nbsp;&nbsp;&nbsp;docker push ${REGISTRY}${IMAGE_NAME}:latest</code> | 调用 Docker 操作：<code>docker push ${REGISTRY}${IMAGE_NAME}:latest</code>；具体副作用须看命令。 |
| L133 | （空行） | 空行/展示分隔。 |
| L134 | <code>&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;✓ 镜像推送成功&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L135 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L136 | （空行） | 空行/展示分隔。 |
| L137 | <code># 为镜像添加标签</code> | 注释/说明：为镜像添加标签 |
| L138 | <code>tag_image() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L139 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local new_version=$1</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L140 | （空行） | 空行/展示分隔。 |
| L141 | <code>&nbsp;&nbsp;&nbsp;&nbsp;print_step &quot;为镜像添加标签: $new_version&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L142 | （空行） | 空行/展示分隔。 |
| L143 | <code>&nbsp;&nbsp;&nbsp;&nbsp;docker tag ${REGISTRY}${IMAGE_NAME}:${VERSION} ${REGISTRY}${IMAGE_NAME}:${new_version}</code> | 调用 Docker 操作：<code>docker tag ${REGISTRY}${IMAGE_NAME}:${VERSION} ${REGISTRY}${IMAGE_NAME}:${new_version}</code>；具体副作用须看命令。 |
| L144 | （空行） | 空行/展示分隔。 |
| L145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;✓ 标签添加成功: ${REGISTRY}${IMAGE_NAME}:${new_version}&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L146 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L147 | （空行） | 空行/展示分隔。 |
| L148 | <code># 清理构建缓存</code> | 注释/说明：清理构建缓存 |
| L149 | <code>clean_build_cache() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L150 | <code>&nbsp;&nbsp;&nbsp;&nbsp;print_step &quot;清理 Docker 构建缓存&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L151 | （空行） | 空行/展示分隔。 |
| L152 | <code>&nbsp;&nbsp;&nbsp;&nbsp;docker builder prune -f</code> | 调用 Docker 操作：<code>docker builder prune -f</code>；具体副作用须看命令。 |
| L153 | （空行） | 空行/展示分隔。 |
| L154 | <code>&nbsp;&nbsp;&nbsp;&nbsp;print_info &quot;✓ 构建缓存已清理&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L155 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L156 | （空行） | 空行/展示分隔。 |
| L157 | <code># 解析参数</code> | 注释/说明：解析参数 |
| L158 | <code>parse_args() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L159 | <code>&nbsp;&nbsp;&nbsp;&nbsp;while [[ $# -gt 0 ]]; do</code> | 按条件循环消费参数或数据。 |
| L160 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;case $1 in</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |

### L161 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L161 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--no-cache)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L162 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;NO_CACHE=true</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L163 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;shift</code> | 移动位置参数，决定下一次 $1/$2 代表什么。 |
| L164 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L165 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--platform)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L166 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;PLATFORMS=&quot;$2&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L167 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;shift 2</code> | 移动位置参数，决定下一次 $1/$2 代表什么。 |
| L168 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L169 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--registry)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L170 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;REGISTRY=&quot;$2&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L171 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;shift 2</code> | 移动位置参数，决定下一次 $1/$2 代表什么。 |
| L172 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L173 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;--version)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L174 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;VERSION=&quot;$2&quot;</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L175 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;shift 2</code> | 移动位置参数，决定下一次 $1/$2 代表什么。 |
| L176 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L177 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L178 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;shift</code> | 移动位置参数，决定下一次 $1/$2 代表什么。 |
| L179 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L180 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;esac</code> | 结束条件/循环/分支/函数结构。 |
| L181 | <code>&nbsp;&nbsp;&nbsp;&nbsp;done</code> | 结束条件/循环/分支/函数结构。 |
| L182 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L183 | （空行） | 空行/展示分隔。 |
| L184 | <code># 主函数</code> | 注释/说明：主函数 |
| L185 | <code>main() {</code> | 定义 Bash 函数，只有被调用时才执行函数体。 |
| L186 | <code>&nbsp;&nbsp;&nbsp;&nbsp;local command=${1:-help}</code> | 设置脚本变量/命令字符串，为后续 Docker 参数构造输入。 |
| L187 | <code>&nbsp;&nbsp;&nbsp;&nbsp;shift &#124;&#124; true</code> | 移动位置参数，决定下一次 $1/$2 代表什么。 |
| L188 | （空行） | 空行/展示分隔。 |
| L189 | <code>&nbsp;&nbsp;&nbsp;&nbsp;# 解析选项</code> | 注释/说明：解析选项 |
| L190 | <code>&nbsp;&nbsp;&nbsp;&nbsp;parse_args &quot;$@&quot;</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L191 | （空行） | 空行/展示分隔。 |
| L192 | <code>&nbsp;&nbsp;&nbsp;&nbsp;case $command in</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L193 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;build)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L194 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;build_image &quot;&quot; &quot;$NO_CACHE&quot; &quot;$PLATFORMS&quot;</code> | **关键：**空 target 使用 Dockerfile 最后阶段，当前是 development。 |
| L195 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L196 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;build-prod)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L197 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;build_image &quot;production&quot; &quot;$NO_CACHE&quot; &quot;$PLATFORMS&quot;</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L198 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L199 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;build-dev)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L200 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;build_image &quot;development&quot; &quot;$NO_CACHE&quot; &quot;$PLATFORMS&quot;</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |

### L201 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L201 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L202 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;build-test)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L203 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;build_image &quot;test&quot; &quot;$NO_CACHE&quot; &quot;$PLATFORMS&quot;</code> | **关键：**test 阶段不存在，调用会构建失败。 |
| L204 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L205 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;push)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L206 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;shift</code> | **关键：**main 先 shift 过一次，这里再次移动位置参数，需与帮助示例逐项核对。 |
| L207 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;push_image &quot;$1&quot;</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L208 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L209 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tag)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L210 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;shift</code> | 移动位置参数，决定下一次 $1/$2 代表什么。 |
| L211 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;tag_image &quot;$1&quot;</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L212 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L213 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;clean)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L214 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;clean_build_cache</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L215 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L216 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;help&#124;--help&#124;-h)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L217 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;show_help</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L218 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L219 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;*)</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L220 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;print_error &quot;未知命令: $command&quot;</code> | 向终端输出帮助或状态，不代表依赖服务真实健康。 |
| L221 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;show_help</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L222 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;exit 1</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |
| L223 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;;;</code> | 结束条件/循环/分支/函数结构。 |
| L224 | <code>&nbsp;&nbsp;&nbsp;&nbsp;esac</code> | 结束条件/循环/分支/函数结构。 |
| L225 | <code>}</code> | 结束条件/循环/分支/函数结构。 |
| L226 | （空行） | 空行/展示分隔。 |
| L227 | <code># 执行主函数</code> | 注释/说明：执行主函数 |
| L228 | <code>main &quot;$@&quot;</code> | Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。 |

## 结合全项目：设计缺口与增强方向

- build 不指定 target 会落到 development；build-test 目标 test 在 Dockerfile 不存在。
- main 已 shift，再在 push/tag 分支 shift 一次，会丢参数；parse_args 只消费自身函数参数，push/tag 的位置参数传递与帮助示例不一致。
- 命令拼字符串再 eval，含空格路径/参数和 shell 特殊字符不稳；建议改 Bash 数组并严格校验参数。
- --registry 在构建路径没有统一尾部 /，push_image 才添加；set -e 可使后面的 $? 失败分支来不及执行。
- 此文件被 .gitignore 的 build-image*.sh 匹配，不能只用 rg 默认输出判断它不存在。

**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。
