# wiki/assets/architecture/03-agent-skills.svg 解读

## 输入、输出与流向

**定位：** 静态 SVG 展示资产：03-agent-skills.svg

**输入：** XML 中的画布、样式、图形、文本和连接线。

**输出 / 副作用：** 浏览器/Markdown 渲染后的架构图或宣传海报；无业务数据存储副作用。

**流向：** svg 画布→defs 样式/箭头→rect/text/path 等元素→静态图片。图中连线是作者画出的表达，不会执行 Python 调用。

[返回阅读入口](../../../../README.md) · [对照原文件](../../../../../wiki/assets/architecture/03-agent-skills.svg)

当前工作区快照：181 行。原始行号列对应原文件；空白和纯注释可略读。 SHA-256：`9313626f58fa9ed18a52cd616939bf70e9505dfad170e2d18326ce7133f7fbea`。

## 按原行号阅读

读法：先看每个函数前的因果解释，再看逐行表。多行参数、词表、提示文本续行从属于起始语句；关键行另加粗说明。


### L1 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L1 | <code>&lt;svg xmlns=&quot;http://www.w3.org/2000/svg&quot; width=&quot;1600&quot; height=&quot;1000&quot; viewBox=&quot;0 0 1600 1000&quot;&gt;</code> | 定义 SVG 画布尺寸和坐标系。 |
| L2 | <code>&nbsp;&nbsp;&lt;defs&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L3 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;style&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L4 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.bg { fill: #fbfcfb; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L5 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.header { fill: #eef6ff; stroke: #c9d7e9; stroke-width: 1.4; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L6 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.panel { fill: #f7fcf9; stroke: #cfe3d7; stroke-width: 1.5; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L7 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.band { fill: #f0faf4; stroke: #cfe3d7; stroke-width: 1.2; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L8 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.card { fill: #ffffff; stroke: #d7e1df; stroke-width: 1.4; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L9 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.blue-card { fill: #f3f9ff; stroke: #cad9e9; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L10 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.green-card { fill: #f7fcf9; stroke: #bfe2ce; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L11 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.orange-card { fill: #fff9ef; stroke: #efd7af; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L12 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.purple-card { fill: #f7f3ff; stroke: #d3c6ef; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L13 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.soft-card { fill: #fbfefd; stroke: #d6e6dc; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L14 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.title { font: 800 38px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #13213b; letter-spacing: 1px; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L15 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.subtitle { font: 500 18px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #657284; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L16 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.section-title { font: 800 27px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #08733d; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L17 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.label { font: 800 23px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #17243d; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L18 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.small { font: 500 18px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #25324b; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L19 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.muted { font: 500 16px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #657284; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L20 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.tiny { font: 800 15px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #ffffff; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L21 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.green-text { fill: #08733d; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L22 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.orange-text { fill: #a85b00; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L23 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.purple-text { fill: #573c9b; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L24 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.blue { fill: #3165b7; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L25 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.green { fill: #14945b; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L26 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.orange { fill: #f47d22; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L27 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.purple { fill: #6045a9; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L28 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.line { stroke: #aeb8c4; stroke-width: 3; fill: none; marker-end: url(#arrow); }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L29 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.green-line { stroke: #14945b; stroke-width: 3; fill: none; marker-end: url(#arrow-green); }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L30 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.dashed { stroke-dasharray: 9 9; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L31 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.shadow { filter: url(#shadow); }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L32 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;/style&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L33 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;filter id=&quot;shadow&quot; x=&quot;-20%&quot; y=&quot;-20%&quot; width=&quot;140%&quot; height=&quot;140%&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L34 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;feDropShadow dx=&quot;0&quot; dy=&quot;6&quot; stdDeviation=&quot;8&quot; flood-color=&quot;#d8e1df&quot; flood-opacity=&quot;0.42&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L35 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;/filter&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L36 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;marker id=&quot;arrow&quot; viewBox=&quot;0 0 10 10&quot; refX=&quot;9&quot; refY=&quot;5&quot; markerWidth=&quot;8&quot; markerHeight=&quot;8&quot; orient=&quot;auto&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L37 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M 0 0 L 10 5 L 0 10 z&quot; fill=&quot;#aeb8c4&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L38 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;/marker&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L39 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;marker id=&quot;arrow-green&quot; viewBox=&quot;0 0 10 10&quot; refX=&quot;9&quot; refY=&quot;5&quot; markerWidth=&quot;8&quot; markerHeight=&quot;8&quot; orient=&quot;auto&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L40 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M 0 0 L 10 5 L 0 10 z&quot; fill=&quot;#14945b&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |

### L41 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L41 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;/marker&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L42 | <code>&nbsp;&nbsp;&lt;/defs&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L43 | （空行） | 空行/展示分隔。 |
| L44 | <code>&nbsp;&nbsp;&lt;rect class=&quot;bg&quot; width=&quot;1600&quot; height=&quot;1000&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L45 | （空行） | 空行/展示分隔。 |
| L46 | <code>&nbsp;&nbsp;&lt;!-- Header --&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L47 | <code>&nbsp;&nbsp;&lt;rect class=&quot;header shadow&quot; x=&quot;32&quot; y=&quot;28&quot; width=&quot;1536&quot; height=&quot;112&quot; rx=&quot;18&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L48 | <code>&nbsp;&nbsp;&lt;text class=&quot;title&quot; x=&quot;66&quot; y=&quot;78&quot;&gt;多 Agent 与 Skills 注入关系&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L49 | <code>&nbsp;&nbsp;&lt;text class=&quot;subtitle&quot; x=&quot;66&quot; y=&quot;110&quot;&gt;用户消息先完成意图识别与结构化路由决策，再按 Agent 类型和关键词动态注入对应客服规范&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L50 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(1322,58)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L51 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;soft-card&quot; width=&quot;196&quot; height=&quot;48&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;green&quot; cx=&quot;28&quot; cy=&quot;24&quot; r=&quot;14&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L53 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;23&quot; y=&quot;29&quot;&gt;热&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;52&quot; y=&quot;30&quot;&gt;Skills 可热加载&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L55 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L56 | （空行） | 空行/展示分隔。 |
| L57 | <code>&nbsp;&nbsp;&lt;!-- Route flow --&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L58 | <code>&nbsp;&nbsp;&lt;rect class=&quot;panel shadow&quot; x=&quot;32&quot; y=&quot;170&quot; width=&quot;1536&quot; height=&quot;590&quot; rx=&quot;18&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L59 | <code>&nbsp;&nbsp;&lt;rect class=&quot;band&quot; x=&quot;62&quot; y=&quot;198&quot; width=&quot;1476&quot; height=&quot;72&quot; rx=&quot;14&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L60 | <code>&nbsp;&nbsp;&lt;text class=&quot;section-title&quot; x=&quot;92&quot; y=&quot;244&quot;&gt;路由链路：识别问题类型，生成主 Agent 与辅助 Agent 决策&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L61 | （空行） | 空行/展示分隔。 |
| L62 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(92,310)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L63 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card blue-card&quot; width=&quot;250&quot; height=&quot;126&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L64 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;blue&quot; cx=&quot;44&quot; cy=&quot;38&quot; r=&quot;19&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L65 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;39&quot; y=&quot;44&quot;&gt;1&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L66 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label&quot; x=&quot;78&quot; y=&quot;46&quot;&gt;用户消息&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L67 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M62 72 h130 a15 15 0 0 1 15 15 v24 a15 15 0 0 1 -15 15 h-62 l-25 20 v-20 h-43 a15 15 0 0 1 -15 -15 v-24 a15 15 0 0 1 15 -15z&quot; fill=&quot;#ffffff&quot; stroke=&quot;#3165b7&quot; stroke-width=&quot;5&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L68 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;68&quot; y=&quot;106&quot;&gt;咨询 / 报错 / 退款&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L69 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L70 | （空行） | 空行/展示分隔。 |
| L71 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(452,310)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card purple-card&quot; width=&quot;270&quot; height=&quot;126&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L73 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;purple&quot; cx=&quot;44&quot; cy=&quot;38&quot; r=&quot;19&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L74 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;39&quot; y=&quot;44&quot;&gt;2&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L75 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label&quot; x=&quot;78&quot; y=&quot;46&quot;&gt;意图识别&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L76 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle cx=&quot;116&quot; cy=&quot;88&quot; r=&quot;30&quot; fill=&quot;#ffffff&quot; stroke=&quot;#6045a9&quot; stroke-width=&quot;5&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L77 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M90 88 h52 M116 62 v52 M96 68 c13 13 26 26 39 39 M136 68 c-13 13 -26 26 -39 39&quot; stroke=&quot;#6045a9&quot; stroke-width=&quot;3&quot; fill=&quot;none&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L78 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;165&quot; y=&quot;84&quot;&gt;LLM&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L79 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;165&quot; y=&quot;108&quot;&gt;语义 + 规则&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L80 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |

### L81 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L81 | （空行） | 空行/展示分隔。 |
| L82 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(832,310)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L83 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card green-card&quot; width=&quot;286&quot; height=&quot;126&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;green&quot; cx=&quot;44&quot; cy=&quot;38&quot; r=&quot;19&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;39&quot; y=&quot;44&quot;&gt;3&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L86 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label&quot; x=&quot;78&quot; y=&quot;46&quot;&gt;Agent 编排器&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;green&quot; cx=&quot;118&quot; cy=&quot;88&quot; r=&quot;32&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle cx=&quot;98&quot; cy=&quot;78&quot; r=&quot;7&quot; fill=&quot;#fff&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L89 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle cx=&quot;138&quot; cy=&quot;78&quot; r=&quot;7&quot; fill=&quot;#fff&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle cx=&quot;118&quot; cy=&quot;102&quot; r=&quot;7&quot; fill=&quot;#fff&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L91 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M98 78 L118 102 L138 78&quot; stroke=&quot;#fff&quot; stroke-width=&quot;5&quot; fill=&quot;none&quot; stroke-linecap=&quot;round&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L92 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;170&quot; y=&quot;84&quot;&gt;领域打分&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L93 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;170&quot; y=&quot;108&quot;&gt;主辅 Agent&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L94 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L95 | （空行） | 空行/展示分隔。 |
| L96 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(1270,310)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L97 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card blue-card&quot; width=&quot;220&quot; height=&quot;126&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;blue&quot; cx=&quot;44&quot; cy=&quot;38&quot; r=&quot;19&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L99 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;39&quot; y=&quot;44&quot;&gt;4&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L100 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label&quot; x=&quot;78&quot; y=&quot;46&quot;&gt;模型回复&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L101 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;42&quot; y=&quot;86&quot;&gt;System Prompt&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L102 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;42&quot; y=&quot;112&quot;&gt;+ 动态 Skills&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L103 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L104 | （空行） | 空行/展示分隔。 |
| L105 | <code>&nbsp;&nbsp;&lt;path class=&quot;line&quot; d=&quot;M342 373 L452 373&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L106 | <code>&nbsp;&nbsp;&lt;path class=&quot;line&quot; d=&quot;M722 373 L832 373&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L107 | <code>&nbsp;&nbsp;&lt;path class=&quot;line&quot; d=&quot;M1118 373 L1270 373&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L108 | （空行） | 空行/展示分隔。 |
| L109 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(1190,210)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L110 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;soft-card&quot; width=&quot;316&quot; height=&quot;46&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L111 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;green&quot; cx=&quot;28&quot; cy=&quot;23&quot; r=&quot;12&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L112 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M22 23 L27 29 L36 17&quot; stroke=&quot;#fff&quot; stroke-width=&quot;4&quot; fill=&quot;none&quot; stroke-linecap=&quot;round&quot; stroke-linejoin=&quot;round&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;52&quot; y=&quot;29&quot;&gt;控制台提示当前加载的 Skill&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L114 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L115 | （空行） | 空行/展示分隔。 |
| L116 | <code>&nbsp;&nbsp;&lt;path class=&quot;green-line&quot; d=&quot;M975 436 C905 478 345 478 300 540&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L117 | <code>&nbsp;&nbsp;&lt;path class=&quot;green-line&quot; d=&quot;M975 436 C912 480 825 480 800 540&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L118 | <code>&nbsp;&nbsp;&lt;path class=&quot;green-line&quot; d=&quot;M975 436 C1048 478 1282 478 1300 540&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L119 | （空行） | 空行/展示分隔。 |
| L120 | <code>&nbsp;&nbsp;&lt;!-- Agent layer --&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |

### L121 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L121 | <code>&nbsp;&nbsp;&lt;text class=&quot;section-title&quot; x=&quot;92&quot; y=&quot;505&quot;&gt;Agent 层：拆分职责边界，避免通用提示词互相污染&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L122 | （空行） | 空行/展示分隔。 |
| L123 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(90,540)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L124 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card green-card&quot; width=&quot;420&quot; height=&quot;160&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L125 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;green&quot; cx=&quot;62&quot; cy=&quot;60&quot; r=&quot;34&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L126 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path class=&quot;green&quot; d=&quot;M16 132 C24 94 43 80 62 80 C81 80 100 94 108 132 Z&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L127 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label green-text&quot; x=&quot;138&quot; y=&quot;52&quot;&gt;通用客服 Agent&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L128 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;138&quot; y=&quot;80&quot;&gt;GeneralAgent&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L129 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;138&quot; y=&quot;112&quot;&gt;接待、澄清、订单、售后&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L130 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;138&quot; y=&quot;140&quot;&gt;必要时转人工或分流&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L131 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L132 | （空行） | 空行/展示分隔。 |
| L133 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(590,540)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L134 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card orange-card&quot; width=&quot;420&quot; height=&quot;160&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L135 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;orange&quot; cx=&quot;62&quot; cy=&quot;60&quot; r=&quot;34&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L136 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text x=&quot;45&quot; y=&quot;72&quot; font-family=&quot;Arial&quot; font-size=&quot;34&quot; font-weight=&quot;800&quot; fill=&quot;#ffffff&quot;&gt;&amp;lt;/&amp;gt;&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L137 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label orange-text&quot; x=&quot;138&quot; y=&quot;52&quot;&gt;技术支持 Agent&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L138 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;138&quot; y=&quot;80&quot;&gt;TechnicalAgent&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L139 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;138&quot; y=&quot;112&quot;&gt;报错、接口、部署、日志&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L140 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;138&quot; y=&quot;140&quot;&gt;定位问题并给出排查步骤&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L141 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L142 | （空行） | 空行/展示分隔。 |
| L143 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(1090,540)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L144 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card purple-card&quot; width=&quot;420&quot; height=&quot;160&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;purple&quot; cx=&quot;62&quot; cy=&quot;60&quot; r=&quot;34&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L146 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M46 52 h34 M46 68 h34 M56 38 v46 M70 38 v46&quot; stroke=&quot;#fff&quot; stroke-width=&quot;5&quot; stroke-linecap=&quot;round&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L147 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label purple-text&quot; x=&quot;138&quot; y=&quot;52&quot;&gt;账单退款 Agent&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L148 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;138&quot; y=&quot;80&quot;&gt;BillingAgent&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L149 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;138&quot; y=&quot;112&quot;&gt;扣款、退款、发票、订阅&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L150 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;138&quot; y=&quot;140&quot;&gt;按账务规范处理敏感问题&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L151 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L152 | （空行） | 空行/展示分隔。 |
| L153 | <code>&nbsp;&nbsp;&lt;!-- Skills layer --&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L154 | <code>&nbsp;&nbsp;&lt;rect class=&quot;panel shadow&quot; x=&quot;32&quot; y=&quot;790&quot; width=&quot;1536&quot; height=&quot;174&quot; rx=&quot;18&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L155 | <code>&nbsp;&nbsp;&lt;text class=&quot;section-title&quot; x=&quot;62&quot; y=&quot;836&quot;&gt;Skills 注入：按顶部配置匹配文档，拼入本轮 system prompt&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L156 | （空行） | 空行/展示分隔。 |
| L157 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(92,866)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L158 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card green-card&quot; width=&quot;420&quot; height=&quot;70&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L159 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect x=&quot;28&quot; y=&quot;18&quot; width=&quot;52&quot; height=&quot;38&quot; rx=&quot;7&quot; fill=&quot;#ffffff&quot; stroke=&quot;#14945b&quot; stroke-width=&quot;5&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L160 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label green-text&quot; x=&quot;102&quot; y=&quot;30&quot;&gt;通用客服规范&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |

### L161 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L161 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;102&quot; y=&quot;56&quot;&gt;agents: general / keywords: 咨询、订单、售后&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L162 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L163 | （空行） | 空行/展示分隔。 |
| L164 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(590,866)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L165 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card orange-card&quot; width=&quot;420&quot; height=&quot;70&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L166 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect x=&quot;28&quot; y=&quot;18&quot; width=&quot;52&quot; height=&quot;38&quot; rx=&quot;7&quot; fill=&quot;#ffffff&quot; stroke=&quot;#f47d22&quot; stroke-width=&quot;5&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L167 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label orange-text&quot; x=&quot;102&quot; y=&quot;30&quot;&gt;技术支持规范&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L168 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;102&quot; y=&quot;56&quot;&gt;agents: technical / keywords: 报错、接口、500&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L169 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L170 | （空行） | 空行/展示分隔。 |
| L171 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(1088,866)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L172 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card purple-card&quot; width=&quot;420&quot; height=&quot;70&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L173 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect x=&quot;28&quot; y=&quot;18&quot; width=&quot;52&quot; height=&quot;38&quot; rx=&quot;7&quot; fill=&quot;#ffffff&quot; stroke=&quot;#6045a9&quot; stroke-width=&quot;5&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L174 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label purple-text&quot; x=&quot;102&quot; y=&quot;30&quot;&gt;账单退款规范&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L175 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;102&quot; y=&quot;56&quot;&gt;agents: billing / keywords: 退款、扣款、发票&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L176 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L177 | （空行） | 空行/展示分隔。 |
| L178 | <code>&nbsp;&nbsp;&lt;path class=&quot;green-line dashed&quot; d=&quot;M300 866 L300 700&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L179 | <code>&nbsp;&nbsp;&lt;path class=&quot;green-line dashed&quot; d=&quot;M800 866 L800 700&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L180 | <code>&nbsp;&nbsp;&lt;path class=&quot;green-line dashed&quot; d=&quot;M1300 866 L1300 700&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L181 | <code>&lt;/svg&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |

## 结合全项目：设计缺口与增强方向

- 需要与代码版本一起更新；图中的主辅协作、监控、部署语义不能代替对应函数证据。
- 本解读对重复坐标和配色简略，保留逐行位置；重点读可见标签和它连接的实际模块。

**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。
