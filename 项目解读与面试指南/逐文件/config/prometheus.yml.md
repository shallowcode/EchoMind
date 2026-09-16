# config/prometheus.yml 解读

## 输入、输出与流向

**定位：** 配置 Prometheus 从应用指标注册表抓取数据。

**输入：** echomind:8000/metrics、localhost:9090 自身指标。

**输出 / 副作用：** 带 cluster/environment/service 标签的时序数据，由 Prometheus 服务保存。

**流向：** 每 10 秒抓主应用，每 15 秒默认抓自身；rule_files 声明潜在规则目录。

[返回阅读入口](../../README.md) · [对照原文件](../../../config/prometheus.yml)

当前工作区快照：26 行。原始行号列对应原文件；空白和纯注释可略读。 SHA-256：`0ba284e25ab6868f88a78023fda9dadda4c30388e7df46e28434696f1a5ba339`。

## 按原行号阅读

读法：先看每个函数前的因果解释，再看逐行表。多行参数、词表、提示文本续行从属于起始语句；关键行另加粗说明。


### L1 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L1 | <code># Prometheus 配置文件 — EchoMind 智能客服系统</code> | 注释/说明：Prometheus 配置文件 — EchoMind 智能客服系统 |
| L2 | （空行） | 空行/展示分隔。 |
| L3 | <code>global:</code> | Prometheus全局抓取默认值；缩进决定该项属于哪个服务/抓取任务。 |
| L4 | <code>&nbsp;&nbsp;scrape_interval: 15s</code> | 抓取指标的时间间隔；缩进决定该项属于哪个服务/抓取任务。 |
| L5 | <code>&nbsp;&nbsp;evaluation_interval: 15s</code> | 评估记录/告警规则的周期；缩进决定该项属于哪个服务/抓取任务。 |
| L6 | <code>&nbsp;&nbsp;external_labels:</code> | 发送指标时附带的外部标签；缩进决定该项属于哪个服务/抓取任务。 |
| L7 | <code>&nbsp;&nbsp;&nbsp;&nbsp;cluster: &#x27;echomind&#x27;</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L8 | <code>&nbsp;&nbsp;&nbsp;&nbsp;environment: &#x27;production&#x27;</code> | 注入变量，应用同名值覆盖env_file；缩进决定该项属于哪个服务/抓取任务。 |
| L9 | （空行） | 空行/展示分隔。 |
| L10 | <code>rule_files:</code> | 待加载的规则文件路径模式；缩进决定该项属于哪个服务/抓取任务。 |
| L11 | <code>&nbsp;&nbsp;- &quot;alerts/*.yml&quot;</code> | **关键：**规则 glob 是路径声明，当前仓库无实际 alerts YAML。 |
| L12 | （空行） | 空行/展示分隔。 |
| L13 | <code>scrape_configs:</code> | 定义指标抓取任务列表；缩进决定该项属于哪个服务/抓取任务。 |
| L14 | <code>&nbsp;&nbsp;# EchoMind 主应用指标</code> | 注释/说明：EchoMind 主应用指标 |
| L15 | <code>&nbsp;&nbsp;- job_name: &#x27;echomind-app&#x27;</code> | 指标任务名称；缩进决定该项属于哪个服务/抓取任务。 |
| L16 | <code>&nbsp;&nbsp;&nbsp;&nbsp;static_configs:</code> | 静态配置抓取目标；缩进决定该项属于哪个服务/抓取任务。 |
| L17 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- targets: [&#x27;echomind:8000&#x27;]</code> | **关键：**抓主 API 8000，不抓额外的 PROMETHEUS_PORT。 |
| L18 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;labels:</code> | 为抓取的时间序列附加标签；缩进决定该项属于哪个服务/抓取任务。 |
| L19 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;service: &#x27;echomind&#x27;</code> | 当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。 |
| L20 | <code>&nbsp;&nbsp;&nbsp;&nbsp;scrape_interval: 10s</code> | **关键：**覆盖 global 的 15 秒为 10 秒。 |
| L21 | <code>&nbsp;&nbsp;&nbsp;&nbsp;metrics_path: &#x27;/metrics&#x27;</code> | HTTP指标路径；缩进决定该项属于哪个服务/抓取任务。 |
| L22 | （空行） | 空行/展示分隔。 |
| L23 | <code>&nbsp;&nbsp;# Prometheus 自监控</code> | 注释/说明：Prometheus 自监控 |
| L24 | <code>&nbsp;&nbsp;- job_name: &#x27;prometheus&#x27;</code> | 指标任务名称；缩进决定该项属于哪个服务/抓取任务。 |
| L25 | <code>&nbsp;&nbsp;&nbsp;&nbsp;static_configs:</code> | 静态配置抓取目标；缩进决定该项属于哪个服务/抓取任务。 |
| L26 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;- targets: [&#x27;localhost:9090&#x27;]</code> | **关键：**这里 localhost 是 Prometheus 容器自己。 |

## 结合全项目：设计缺口与增强方向

- alerts/*.yml 没有对应现存规则文件，也没有 Alertmanager 服务配置；不是完整 Prometheus 告警投递链。
- 能抓到端点不代表业务 metrics 已注册，需结合 PROMETHEUS_PORT 和 Monitor 初始化判断。
- 真实请求延迟分布、token、费用、RAG 命中质量没有在应用埋点，本文件无法弥补缺失。

**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。
