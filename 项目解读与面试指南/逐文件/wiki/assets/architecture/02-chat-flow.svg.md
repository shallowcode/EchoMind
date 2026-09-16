# wiki/assets/architecture/02-chat-flow.svg 解读

## 输入、输出与流向

**定位：** 静态 SVG 展示资产：02-chat-flow.svg

**输入：** XML 中的画布、样式、图形、文本和连接线。

**输出 / 副作用：** 浏览器/Markdown 渲染后的架构图或宣传海报；无业务数据存储副作用。

**流向：** svg 画布→defs 样式/箭头→rect/text/path 等元素→静态图片。图中连线是作者画出的表达，不会执行 Python 调用。

[返回阅读入口](../../../../README.md) · [对照原文件](../../../../../wiki/assets/architecture/02-chat-flow.svg)

当前工作区快照：195 行。原始行号列对应原文件；空白和纯注释可略读。 SHA-256：`d0e10b7103b1aac9c1bdd26db8d45e65aae896f416f39858e5f9aff5ff19a4df`。

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
| L8 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.async-band { fill: #f8fbff; stroke: #d4dfed; stroke-width: 1.2; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L9 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.card { fill: #ffffff; stroke: #d7e1df; stroke-width: 1.4; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L10 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.blue-card { fill: #f3f9ff; stroke: #cad9e9; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L11 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.green-card { fill: #f7fcf9; stroke: #bfe2ce; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L12 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.orange-card { fill: #fff9ef; stroke: #efd7af; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L13 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.purple-card { fill: #f7f3ff; stroke: #d3c6ef; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L14 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.soft-card { fill: #fbfefd; stroke: #d6e6dc; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L15 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.title { font: 800 38px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #13213b; letter-spacing: 1px; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L16 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.subtitle { font: 500 18px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #657284; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L17 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.section-title { font: 800 27px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #08733d; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L18 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.label { font: 800 23px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #17243d; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L19 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.small { font: 500 18px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #25324b; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L20 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.muted { font: 500 16px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #657284; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L21 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.tiny { font: 800 15px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #ffffff; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L22 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.green-text { fill: #08733d; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L23 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.orange-text { fill: #a85b00; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L24 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.purple-text { fill: #573c9b; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L25 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.blue-text { fill: #245ca8; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L26 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.blue { fill: #3165b7; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L27 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.green { fill: #14945b; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L28 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.orange { fill: #f47d22; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L29 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.purple { fill: #6045a9; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L30 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.line { stroke: #aeb8c4; stroke-width: 3; fill: none; marker-end: url(#arrow); }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L31 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.green-line { stroke: #14945b; stroke-width: 3; fill: none; marker-end: url(#arrow-green); }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L32 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.blue-line { stroke: #4a86db; stroke-width: 3; fill: none; marker-end: url(#arrow-blue); }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L33 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.dashed { stroke-dasharray: 9 9; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L34 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.shadow { filter: url(#shadow); }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L35 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;/style&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L36 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;filter id=&quot;shadow&quot; x=&quot;-20%&quot; y=&quot;-20%&quot; width=&quot;140%&quot; height=&quot;140%&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L37 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;feDropShadow dx=&quot;0&quot; dy=&quot;6&quot; stdDeviation=&quot;8&quot; flood-color=&quot;#d8e1df&quot; flood-opacity=&quot;0.42&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L38 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;/filter&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L39 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;marker id=&quot;arrow&quot; viewBox=&quot;0 0 10 10&quot; refX=&quot;9&quot; refY=&quot;5&quot; markerWidth=&quot;8&quot; markerHeight=&quot;8&quot; orient=&quot;auto&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L40 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M 0 0 L 10 5 L 0 10 z&quot; fill=&quot;#aeb8c4&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |

### L41 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L41 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;/marker&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L42 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;marker id=&quot;arrow-green&quot; viewBox=&quot;0 0 10 10&quot; refX=&quot;9&quot; refY=&quot;5&quot; markerWidth=&quot;8&quot; markerHeight=&quot;8&quot; orient=&quot;auto&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L43 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M 0 0 L 10 5 L 0 10 z&quot; fill=&quot;#14945b&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L44 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;/marker&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L45 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;marker id=&quot;arrow-blue&quot; viewBox=&quot;0 0 10 10&quot; refX=&quot;9&quot; refY=&quot;5&quot; markerWidth=&quot;8&quot; markerHeight=&quot;8&quot; orient=&quot;auto&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L46 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M 0 0 L 10 5 L 0 10 z&quot; fill=&quot;#4a86db&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L47 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;/marker&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L48 | <code>&nbsp;&nbsp;&lt;/defs&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L49 | （空行） | 空行/展示分隔。 |
| L50 | <code>&nbsp;&nbsp;&lt;rect class=&quot;bg&quot; width=&quot;1600&quot; height=&quot;1000&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L51 | （空行） | 空行/展示分隔。 |
| L52 | <code>&nbsp;&nbsp;&lt;!-- Header --&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L53 | <code>&nbsp;&nbsp;&lt;rect class=&quot;header shadow&quot; x=&quot;32&quot; y=&quot;28&quot; width=&quot;1536&quot; height=&quot;112&quot; rx=&quot;18&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L54 | <code>&nbsp;&nbsp;&lt;text class=&quot;title&quot; x=&quot;66&quot; y=&quot;78&quot;&gt;/chat 主链路架构&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L55 | <code>&nbsp;&nbsp;&lt;text class=&quot;subtitle&quot; x=&quot;66&quot; y=&quot;110&quot;&gt;从用户请求到记忆读取、意图识别、按需知识库检索、Agent 回复和画像更新&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L56 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(1272,58)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L57 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;soft-card&quot; width=&quot;246&quot; height=&quot;48&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L58 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;green&quot; cx=&quot;28&quot; cy=&quot;24&quot; r=&quot;14&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L59 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;23&quot; y=&quot;29&quot;&gt;查&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L60 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;52&quot; y=&quot;30&quot;&gt;上下文 + 知识联合增强&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L61 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L62 | （空行） | 空行/展示分隔。 |
| L63 | <code>&nbsp;&nbsp;&lt;!-- Main chain --&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L64 | <code>&nbsp;&nbsp;&lt;rect class=&quot;panel shadow&quot; x=&quot;32&quot; y=&quot;170&quot; width=&quot;1536&quot; height=&quot;610&quot; rx=&quot;18&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L65 | <code>&nbsp;&nbsp;&lt;rect class=&quot;band&quot; x=&quot;62&quot; y=&quot;198&quot; width=&quot;1476&quot; height=&quot;72&quot; rx=&quot;14&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L66 | <code>&nbsp;&nbsp;&lt;text class=&quot;section-title&quot; x=&quot;92&quot; y=&quot;244&quot;&gt;同步主链路：一次请求内完成上下文增强、路由、Skills 注入与模型回复&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L67 | （空行） | 空行/展示分隔。 |
| L68 | <code>&nbsp;&nbsp;&lt;!-- Row 1 --&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L69 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(92,320)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L70 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card blue-card&quot; width=&quot;280&quot; height=&quot;132&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L71 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;blue&quot; cx=&quot;44&quot; cy=&quot;40&quot; r=&quot;20&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;39&quot; y=&quot;45&quot;&gt;1&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L73 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label blue-text&quot; x=&quot;82&quot; y=&quot;48&quot;&gt;用户请求&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L74 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M72 78 h118 a15 15 0 0 1 15 15 v26 a15 15 0 0 1 -15 15 h-55 l-28 22 v-22 h-35 a15 15 0 0 1 -15 -15 v-26 a15 15 0 0 1 15 -15z&quot; fill=&quot;#ffffff&quot; stroke=&quot;#3165b7&quot; stroke-width=&quot;5&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L75 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;82&quot; y=&quot;112&quot;&gt;POST /chat&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L76 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L77 | （空行） | 空行/展示分隔。 |
| L78 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(452,320)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L79 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card green-card&quot; width=&quot;300&quot; height=&quot;132&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L80 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;green&quot; cx=&quot;44&quot; cy=&quot;40&quot; r=&quot;20&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |

### L81 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L81 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;39&quot; y=&quot;45&quot;&gt;2&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L82 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label green-text&quot; x=&quot;82&quot; y=&quot;48&quot;&gt;读取记忆上下文&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L83 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect x=&quot;76&quot; y=&quot;78&quot; width=&quot;76&quot; height=&quot;46&quot; rx=&quot;8&quot; fill=&quot;#ffffff&quot; stroke=&quot;#14945b&quot; stroke-width=&quot;5&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle cx=&quot;192&quot; cy=&quot;101&quot; r=&quot;25&quot; fill=&quot;#ffffff&quot; stroke=&quot;#14945b&quot; stroke-width=&quot;5&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M210 119 L232 141&quot; stroke=&quot;#14945b&quot; stroke-width=&quot;5&quot; fill=&quot;none&quot; stroke-linecap=&quot;round&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L86 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;78&quot; y=&quot;152&quot;&gt;Redis 工作记忆 + 用户画像&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L87 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L88 | （空行） | 空行/展示分隔。 |
| L89 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(832,320)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card orange-card&quot; width=&quot;300&quot; height=&quot;132&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L91 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;orange&quot; cx=&quot;44&quot; cy=&quot;40&quot; r=&quot;20&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L92 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;39&quot; y=&quot;45&quot;&gt;3&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L93 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label orange-text&quot; x=&quot;82&quot; y=&quot;48&quot;&gt;RAG 知识库检索&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L94 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M80 78 h70 v46 h-70z&quot; fill=&quot;#ffffff&quot; stroke=&quot;#f47d22&quot; stroke-width=&quot;5&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L95 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M160 86 h72 M160 104 h62 M160 122 h50&quot; stroke=&quot;#f47d22&quot; stroke-width=&quot;5&quot; stroke-linecap=&quot;round&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L96 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;80&quot; y=&quot;152&quot;&gt;查询改写 / 召回 / 重排&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L97 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L98 | （空行） | 空行/展示分隔。 |
| L99 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(1212,320)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L100 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card purple-card&quot; width=&quot;280&quot; height=&quot;132&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L101 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;purple&quot; cx=&quot;44&quot; cy=&quot;40&quot; r=&quot;20&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L102 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;39&quot; y=&quot;45&quot;&gt;4&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L103 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label purple-text&quot; x=&quot;82&quot; y=&quot;48&quot;&gt;意图识别&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L104 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle cx=&quot;118&quot; cy=&quot;100&quot; r=&quot;31&quot; fill=&quot;#ffffff&quot; stroke=&quot;#6045a9&quot; stroke-width=&quot;5&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M92 100 h52 M118 74 v52 M98 80 c13 13 26 26 39 39 M138 80 c-13 13 -26 26 -39 39&quot; stroke=&quot;#6045a9&quot; stroke-width=&quot;3&quot; fill=&quot;none&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L106 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;168&quot; y=&quot;99&quot;&gt;LLM&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L107 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;168&quot; y=&quot;121&quot;&gt;语义 + 规则&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L108 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L109 | （空行） | 空行/展示分隔。 |
| L110 | <code>&nbsp;&nbsp;&lt;path class=&quot;line&quot; d=&quot;M372 386 L452 386&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L111 | <code>&nbsp;&nbsp;&lt;path class=&quot;line&quot; d=&quot;M752 386 L832 386&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L112 | <code>&nbsp;&nbsp;&lt;path class=&quot;line&quot; d=&quot;M1132 386 L1212 386&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L113 | （空行） | 空行/展示分隔。 |
| L114 | <code>&nbsp;&nbsp;&lt;!-- Row 2, snake direction --&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L115 | <code>&nbsp;&nbsp;&lt;path class=&quot;line&quot; d=&quot;M1352 452 L1352 526&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L116 | （空行） | 空行/展示分隔。 |
| L117 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(1212,526)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L118 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card purple-card&quot; width=&quot;280&quot; height=&quot;132&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L119 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;purple&quot; cx=&quot;44&quot; cy=&quot;40&quot; r=&quot;20&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L120 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;39&quot; y=&quot;45&quot;&gt;5&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |

### L121 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L121 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label purple-text&quot; x=&quot;82&quot; y=&quot;48&quot;&gt;Agent 路由&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L122 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;purple&quot; cx=&quot;112&quot; cy=&quot;98&quot; r=&quot;32&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L123 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle cx=&quot;94&quot; cy=&quot;90&quot; r=&quot;6&quot; fill=&quot;#fff&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L124 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle cx=&quot;130&quot; cy=&quot;90&quot; r=&quot;6&quot; fill=&quot;#fff&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L125 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle cx=&quot;112&quot; cy=&quot;112&quot; r=&quot;6&quot; fill=&quot;#fff&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L126 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M94 90 L112 112 L130 90&quot; stroke=&quot;#fff&quot; stroke-width=&quot;5&quot; fill=&quot;none&quot; stroke-linecap=&quot;round&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L127 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;164&quot; y=&quot;96&quot;&gt;通用 / 技术&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L128 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;164&quot; y=&quot;118&quot;&gt;账单 / 降级&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L129 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L130 | （空行） | 空行/展示分隔。 |
| L131 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(832,526)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L132 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card green-card&quot; width=&quot;300&quot; height=&quot;132&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L133 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;green&quot; cx=&quot;44&quot; cy=&quot;40&quot; r=&quot;20&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L134 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;39&quot; y=&quot;45&quot;&gt;6&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L135 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label green-text&quot; x=&quot;82&quot; y=&quot;48&quot;&gt;动态 Skills 注入&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L136 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect x=&quot;82&quot; y=&quot;76&quot; width=&quot;62&quot; height=&quot;54&quot; rx=&quot;8&quot; fill=&quot;#ffffff&quot; stroke=&quot;#14945b&quot; stroke-width=&quot;5&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L137 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M144 76 L168 100 L144 100 Z&quot; fill=&quot;#dff4e8&quot; stroke=&quot;#14945b&quot; stroke-width=&quot;4&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L138 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;184&quot; y=&quot;96&quot;&gt;按 Agent&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L139 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;184&quot; y=&quot;118&quot;&gt;和关键词匹配&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L140 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L141 | （空行） | 空行/展示分隔。 |
| L142 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(452,526)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L143 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card blue-card&quot; width=&quot;300&quot; height=&quot;132&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L144 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;blue&quot; cx=&quot;44&quot; cy=&quot;40&quot; r=&quot;20&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;39&quot; y=&quot;45&quot;&gt;7&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L146 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label blue-text&quot; x=&quot;82&quot; y=&quot;48&quot;&gt;调用大模型&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L147 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M84 84 C100 60 142 60 158 84 C174 108 154 130 122 130 C90 130 68 108 84 84 Z&quot; fill=&quot;#ffffff&quot; stroke=&quot;#3165b7&quot; stroke-width=&quot;5&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L148 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;176&quot; y=&quot;96&quot;&gt;Prompt&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L149 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;176&quot; y=&quot;118&quot;&gt;Memory + RAG + Skills&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L150 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L151 | （空行） | 空行/展示分隔。 |
| L152 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(92,526)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L153 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card green-card&quot; width=&quot;280&quot; height=&quot;132&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L154 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;green&quot; cx=&quot;44&quot; cy=&quot;40&quot; r=&quot;20&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L155 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;39&quot; y=&quot;45&quot;&gt;8&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L156 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label green-text&quot; x=&quot;82&quot; y=&quot;48&quot;&gt;返回回复&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L157 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M72 78 h118 a15 15 0 0 1 15 15 v24 a15 15 0 0 1 -15 15 h-32 l-28 22 v-22 h-58 a15 15 0 0 1 -15 -15 v-24 a15 15 0 0 1 15 -15z&quot; fill=&quot;#ffffff&quot; stroke=&quot;#14945b&quot; stroke-width=&quot;5&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L158 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;82&quot; y=&quot;112&quot;&gt;ChatResponse&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L159 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L160 | （空行） | 空行/展示分隔。 |

### L161 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L161 | <code>&nbsp;&nbsp;&lt;path class=&quot;line&quot; d=&quot;M1212 592 L1132 592&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L162 | <code>&nbsp;&nbsp;&lt;path class=&quot;line&quot; d=&quot;M832 592 L752 592&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L163 | <code>&nbsp;&nbsp;&lt;path class=&quot;line&quot; d=&quot;M452 592 L372 592&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L164 | （空行） | 空行/展示分隔。 |
| L165 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(1018,706)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L166 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;soft-card&quot; width=&quot;442&quot; height=&quot;44&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L167 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;green&quot; cx=&quot;28&quot; cy=&quot;22&quot; r=&quot;12&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L168 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M22 22 L27 28 L36 16&quot; stroke=&quot;#fff&quot; stroke-width=&quot;4&quot; fill=&quot;none&quot; stroke-linecap=&quot;round&quot; stroke-linejoin=&quot;round&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L169 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;52&quot; y=&quot;28&quot;&gt;控制台可打印：本轮加载 general / technical / billing skill&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L170 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L171 | （空行） | 空行/展示分隔。 |
| L172 | <code>&nbsp;&nbsp;&lt;!-- Async post-processing --&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L173 | <code>&nbsp;&nbsp;&lt;rect class=&quot;panel shadow&quot; x=&quot;32&quot; y=&quot;810&quot; width=&quot;1536&quot; height=&quot;154&quot; rx=&quot;18&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L174 | <code>&nbsp;&nbsp;&lt;rect class=&quot;async-band&quot; x=&quot;62&quot; y=&quot;838&quot; width=&quot;1476&quot; height=&quot;48&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L175 | <code>&nbsp;&nbsp;&lt;text class=&quot;section-title&quot; x=&quot;92&quot; y=&quot;872&quot;&gt;异步后处理：回复完成后补齐记忆与用户画像&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L176 | （空行） | 空行/展示分隔。 |
| L177 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(282,908)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L178 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card green-card&quot; width=&quot;360&quot; height=&quot;52&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L179 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;green&quot; cx=&quot;32&quot; cy=&quot;26&quot; r=&quot;15&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L180 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;23&quot; y=&quot;31&quot;&gt;9&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L181 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label green-text&quot; x=&quot;62&quot; y=&quot;23&quot;&gt;写入工作记忆&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L182 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;62&quot; y=&quot;43&quot;&gt;用户消息 + 助手回复&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L183 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L184 | （空行） | 空行/展示分隔。 |
| L185 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(812,908)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L186 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card green-card&quot; width=&quot;430&quot; height=&quot;52&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L187 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;green&quot; cx=&quot;34&quot; cy=&quot;26&quot; r=&quot;15&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L188 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;21&quot; y=&quot;31&quot;&gt;10&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L189 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label green-text&quot; x=&quot;66&quot; y=&quot;23&quot;&gt;异步更新用户画像&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L190 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;66&quot; y=&quot;43&quot;&gt;写入 ChromaDB user_profile&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L191 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L192 | （空行） | 空行/展示分隔。 |
| L193 | <code>&nbsp;&nbsp;&lt;path class=&quot;blue-line dashed&quot; d=&quot;M232 658 C232 758 430 780 462 908&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L194 | <code>&nbsp;&nbsp;&lt;path class=&quot;green-line&quot; d=&quot;M642 934 L812 934&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L195 | <code>&lt;/svg&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |

## 结合全项目：设计缺口与增强方向

- 需要与代码版本一起更新；图中的主辅协作、监控、部署语义不能代替对应函数证据。
- 本解读对重复坐标和配色简略，保留逐行位置；重点读可见标签和它连接的实际模块。

**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。
