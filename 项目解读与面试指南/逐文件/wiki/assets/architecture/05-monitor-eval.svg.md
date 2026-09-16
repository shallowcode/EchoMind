# wiki/assets/architecture/05-monitor-eval.svg 解读

## 输入、输出与流向

**定位：** 静态 SVG 展示资产：05-monitor-eval.svg

**输入：** XML 中的画布、样式、图形、文本和连接线。

**输出 / 副作用：** 浏览器/Markdown 渲染后的架构图或宣传海报；无业务数据存储副作用。

**流向：** svg 画布→defs 样式/箭头→rect/text/path 等元素→静态图片。图中连线是作者画出的表达，不会执行 Python 调用。

[返回阅读入口](../../../../README.md) · [对照原文件](../../../../../wiki/assets/architecture/05-monitor-eval.svg)

当前工作区快照：196 行。原始行号列对应原文件；空白和纯注释可略读。 SHA-256：`170f13402a40a4d6c2ef272406e4bc30964a9db511190554e17fc348eb868f63`。

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
| L7 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.blue-panel { fill: #f8fbff; stroke: #d4dfed; stroke-width: 1.5; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L8 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.band { fill: #f0faf4; stroke: #cfe3d7; stroke-width: 1.2; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L9 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.blue-band { fill: #eef6ff; stroke: #c9d7e9; stroke-width: 1.2; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L10 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.card { fill: #ffffff; stroke: #d7e1df; stroke-width: 1.4; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L11 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.blue-card { fill: #f3f9ff; stroke: #cad9e9; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L12 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.green-card { fill: #f7fcf9; stroke: #bfe2ce; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L13 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.orange-card { fill: #fff9ef; stroke: #efd7af; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L14 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.purple-card { fill: #f7f3ff; stroke: #d3c6ef; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L15 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.red-card { fill: #fff8f6; stroke: #e6cbc4; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L16 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.soft-card { fill: #fbfefd; stroke: #d6e6dc; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L17 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.title { font: 800 38px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #13213b; letter-spacing: 1px; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L18 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.subtitle { font: 500 18px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #657284; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L19 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.section-title { font: 800 27px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #08733d; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L20 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.blue-title { font: 800 27px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #245ca8; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L21 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.label { font: 800 23px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #17243d; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L22 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.small { font: 500 18px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #25324b; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L23 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.muted { font: 500 16px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #657284; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L24 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.tiny { font: 800 15px &quot;PingFang SC&quot;, &quot;Microsoft YaHei&quot;, Arial, sans-serif; fill: #ffffff; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L25 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.green-text { fill: #08733d; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L26 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.orange-text { fill: #a85b00; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L27 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.purple-text { fill: #573c9b; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L28 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.blue-text { fill: #245ca8; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L29 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.red-text { fill: #a91f1f; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L30 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.blue { fill: #3165b7; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L31 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.green { fill: #14945b; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L32 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.orange { fill: #f47d22; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L33 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.purple { fill: #6045a9; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L34 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.red { fill: #d34a42; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L35 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.line { stroke: #aeb8c4; stroke-width: 3; fill: none; marker-end: url(#arrow); }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L36 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.green-line { stroke: #14945b; stroke-width: 3; fill: none; marker-end: url(#arrow-green); }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L37 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.blue-line { stroke: #4a86db; stroke-width: 3; fill: none; marker-end: url(#arrow-blue); }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L38 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.red-line { stroke: #d34a42; stroke-width: 3; fill: none; marker-end: url(#arrow-red); }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L39 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.dashed { stroke-dasharray: 9 9; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L40 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.shadow { filter: url(#shadow); }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |

### L41 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L41 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;/style&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L42 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;filter id=&quot;shadow&quot; x=&quot;-20%&quot; y=&quot;-20%&quot; width=&quot;140%&quot; height=&quot;140%&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L43 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;feDropShadow dx=&quot;0&quot; dy=&quot;6&quot; stdDeviation=&quot;8&quot; flood-color=&quot;#d8e1df&quot; flood-opacity=&quot;0.42&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L44 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;/filter&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L45 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;marker id=&quot;arrow&quot; viewBox=&quot;0 0 10 10&quot; refX=&quot;9&quot; refY=&quot;5&quot; markerWidth=&quot;8&quot; markerHeight=&quot;8&quot; orient=&quot;auto&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L46 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M 0 0 L 10 5 L 0 10 z&quot; fill=&quot;#aeb8c4&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L47 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;/marker&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L48 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;marker id=&quot;arrow-green&quot; viewBox=&quot;0 0 10 10&quot; refX=&quot;9&quot; refY=&quot;5&quot; markerWidth=&quot;8&quot; markerHeight=&quot;8&quot; orient=&quot;auto&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L49 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M 0 0 L 10 5 L 0 10 z&quot; fill=&quot;#14945b&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L50 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;/marker&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L51 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;marker id=&quot;arrow-blue&quot; viewBox=&quot;0 0 10 10&quot; refX=&quot;9&quot; refY=&quot;5&quot; markerWidth=&quot;8&quot; markerHeight=&quot;8&quot; orient=&quot;auto&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M 0 0 L 10 5 L 0 10 z&quot; fill=&quot;#4a86db&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L53 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;/marker&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;marker id=&quot;arrow-red&quot; viewBox=&quot;0 0 10 10&quot; refX=&quot;9&quot; refY=&quot;5&quot; markerWidth=&quot;8&quot; markerHeight=&quot;8&quot; orient=&quot;auto&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M 0 0 L 10 5 L 0 10 z&quot; fill=&quot;#d34a42&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;/marker&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L57 | <code>&nbsp;&nbsp;&lt;/defs&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L58 | （空行） | 空行/展示分隔。 |
| L59 | <code>&nbsp;&nbsp;&lt;rect class=&quot;bg&quot; width=&quot;1600&quot; height=&quot;1000&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L60 | （空行） | 空行/展示分隔。 |
| L61 | <code>&nbsp;&nbsp;&lt;!-- Header --&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L62 | <code>&nbsp;&nbsp;&lt;rect class=&quot;header shadow&quot; x=&quot;32&quot; y=&quot;28&quot; width=&quot;1536&quot; height=&quot;112&quot; rx=&quot;18&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L63 | <code>&nbsp;&nbsp;&lt;text class=&quot;title&quot; x=&quot;66&quot; y=&quot;78&quot;&gt;监控与评测闭环&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L64 | <code>&nbsp;&nbsp;&lt;text class=&quot;subtitle&quot; x=&quot;66&quot; y=&quot;110&quot;&gt;在线监控影响后续路由，端到端评测发现回复质量退化并输出优化建议&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L65 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(1278,58)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L66 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;soft-card&quot; width=&quot;240&quot; height=&quot;48&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L67 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;green&quot; cx=&quot;28&quot; cy=&quot;24&quot; r=&quot;14&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L68 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M20 24 L26 31 L38 17&quot; stroke=&quot;#fff&quot; stroke-width=&quot;5&quot; fill=&quot;none&quot; stroke-linecap=&quot;round&quot; stroke-linejoin=&quot;round&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L69 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;52&quot; y=&quot;30&quot;&gt;监控 + 评测双闭环&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L70 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L71 | （空行） | 空行/展示分隔。 |
| L72 | <code>&nbsp;&nbsp;&lt;!-- Online monitoring --&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L73 | <code>&nbsp;&nbsp;&lt;rect class=&quot;panel shadow&quot; x=&quot;32&quot; y=&quot;170&quot; width=&quot;1536&quot; height=&quot;360&quot; rx=&quot;18&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L74 | <code>&nbsp;&nbsp;&lt;rect class=&quot;band&quot; x=&quot;62&quot; y=&quot;198&quot; width=&quot;1476&quot; height=&quot;66&quot; rx=&quot;14&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L75 | <code>&nbsp;&nbsp;&lt;text class=&quot;section-title&quot; x=&quot;92&quot; y=&quot;240&quot;&gt;在线监控链路：采集运行指标，写回路由惩罚&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L76 | （空行） | 空行/展示分隔。 |
| L77 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(92,310)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L78 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card blue-card&quot; width=&quot;240&quot; height=&quot;116&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L79 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;blue&quot; cx=&quot;42&quot; cy=&quot;38&quot; r=&quot;19&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L80 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;37&quot; y=&quot;44&quot;&gt;1&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |

### L81 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L81 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label blue-text&quot; x=&quot;78&quot; y=&quot;46&quot;&gt;对话请求&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L82 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;78&quot; y=&quot;82&quot;&gt;POST /chat&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L83 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L84 | （空行） | 空行/展示分隔。 |
| L85 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(430,310)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L86 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card purple-card&quot; width=&quot;280&quot; height=&quot;116&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;purple&quot; cx=&quot;42&quot; cy=&quot;38&quot; r=&quot;19&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;37&quot; y=&quot;44&quot;&gt;2&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L89 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label purple-text&quot; x=&quot;78&quot; y=&quot;46&quot;&gt;Agent 编排器&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;78&quot; y=&quot;78&quot;&gt;成功率 / 延迟 / 路由评分&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L91 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L92 | （空行） | 空行/展示分隔。 |
| L93 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(808,310)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L94 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card orange-card&quot; width=&quot;280&quot; height=&quot;116&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L95 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;orange&quot; cx=&quot;42&quot; cy=&quot;38&quot; r=&quot;19&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L96 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;37&quot; y=&quot;44&quot;&gt;3&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L97 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label orange-text&quot; x=&quot;78&quot; y=&quot;46&quot;&gt;工具管理器&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;78&quot; y=&quot;78&quot;&gt;缓存 / 熔断 / fallback&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L99 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L100 | （空行） | 空行/展示分隔。 |
| L101 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(1186,310)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L102 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card green-card&quot; width=&quot;280&quot; height=&quot;116&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L103 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;green&quot; cx=&quot;42&quot; cy=&quot;38&quot; r=&quot;19&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L104 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;37&quot; y=&quot;44&quot;&gt;4&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label green-text&quot; x=&quot;78&quot; y=&quot;46&quot;&gt;在线监控&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L106 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;78&quot; y=&quot;78&quot;&gt;采集 Agent / Tool 指标&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L107 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L108 | （空行） | 空行/展示分隔。 |
| L109 | <code>&nbsp;&nbsp;&lt;path class=&quot;line&quot; d=&quot;M332 368 L430 368&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L110 | <code>&nbsp;&nbsp;&lt;path class=&quot;line&quot; d=&quot;M710 368 L808 368&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L111 | <code>&nbsp;&nbsp;&lt;path class=&quot;line&quot; d=&quot;M1088 368 L1186 368&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L112 | （空行） | 空行/展示分隔。 |
| L113 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(952,462)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L114 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card green-card&quot; width=&quot;280&quot; height=&quot;48&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;green&quot; cx=&quot;30&quot; cy=&quot;24&quot; r=&quot;14&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;25&quot; y=&quot;29&quot;&gt;5&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L117 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label green-text&quot; x=&quot;62&quot; y=&quot;31&quot;&gt;/monitor 与 /metrics&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L118 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L119 | <code>&nbsp;&nbsp;&lt;path class=&quot;green-line&quot; d=&quot;M1326 426 C1300 478 1240 486 1232 486&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L120 | （空行） | 空行/展示分隔。 |

### L121 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L121 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(1294,462)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L122 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card red-card&quot; width=&quot;212&quot; height=&quot;48&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L123 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;red&quot; cx=&quot;30&quot; cy=&quot;24&quot; r=&quot;14&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L124 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;25&quot; y=&quot;29&quot;&gt;6&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L125 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label red-text&quot; x=&quot;62&quot; y=&quot;31&quot;&gt;动态降权&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L126 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L127 | <code>&nbsp;&nbsp;&lt;path class=&quot;red-line dashed&quot; d=&quot;M1400 462 C1450 244 574 244 570 310&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L128 | （空行） | 空行/展示分隔。 |
| L129 | <code>&nbsp;&nbsp;&lt;!-- Evaluation --&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L130 | <code>&nbsp;&nbsp;&lt;rect class=&quot;blue-panel shadow&quot; x=&quot;32&quot; y=&quot;570&quot; width=&quot;1536&quot; height=&quot;394&quot; rx=&quot;18&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L131 | <code>&nbsp;&nbsp;&lt;rect class=&quot;blue-band&quot; x=&quot;62&quot; y=&quot;598&quot; width=&quot;1476&quot; height=&quot;66&quot; rx=&quot;14&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L132 | <code>&nbsp;&nbsp;&lt;text class=&quot;blue-title&quot; x=&quot;92&quot; y=&quot;640&quot;&gt;端到端评测链路：真实调用生成回复，再由 LLM-as-Judge 评分和定位回归&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L133 | （空行） | 空行/展示分隔。 |
| L134 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(92,712)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L135 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card blue-card&quot; width=&quot;240&quot; height=&quot;116&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L136 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;blue&quot; cx=&quot;42&quot; cy=&quot;38&quot; r=&quot;19&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L137 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;37&quot; y=&quot;44&quot;&gt;1&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L138 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label blue-text&quot; x=&quot;78&quot; y=&quot;46&quot;&gt;评测请求&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L139 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;78&quot; y=&quot;82&quot;&gt;POST /eval/run&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L140 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L141 | （空行） | 空行/展示分隔。 |
| L142 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(430,712)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L143 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card purple-card&quot; width=&quot;280&quot; height=&quot;116&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L144 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;purple&quot; cx=&quot;42&quot; cy=&quot;38&quot; r=&quot;19&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;37&quot; y=&quot;44&quot;&gt;2&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L146 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label purple-text&quot; x=&quot;78&quot; y=&quot;46&quot;&gt;真实调用链路&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L147 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;78&quot; y=&quot;78&quot;&gt;Orchestrator 生成回复&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L148 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L149 | （空行） | 空行/展示分隔。 |
| L150 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(808,712)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L151 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card orange-card&quot; width=&quot;280&quot; height=&quot;116&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L152 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;orange&quot; cx=&quot;42&quot; cy=&quot;38&quot; r=&quot;19&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L153 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;37&quot; y=&quot;44&quot;&gt;3&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L154 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label orange-text&quot; x=&quot;78&quot; y=&quot;46&quot;&gt;LLM 评审&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L155 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;78&quot; y=&quot;78&quot;&gt;相关性 / 准确性 / 完整性&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L156 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L157 | （空行） | 空行/展示分隔。 |
| L158 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(1186,712)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L159 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card green-card&quot; width=&quot;280&quot; height=&quot;116&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L160 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;green&quot; cx=&quot;42&quot; cy=&quot;38&quot; r=&quot;19&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |

### L161 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L161 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;37&quot; y=&quot;44&quot;&gt;4&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L162 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label green-text&quot; x=&quot;78&quot; y=&quot;46&quot;&gt;评测报告&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L163 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;78&quot; y=&quot;78&quot;&gt;通过率 / 回归 / 建议&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L164 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L165 | （空行） | 空行/展示分隔。 |
| L166 | <code>&nbsp;&nbsp;&lt;path class=&quot;line&quot; d=&quot;M332 770 L430 770&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L167 | <code>&nbsp;&nbsp;&lt;path class=&quot;line&quot; d=&quot;M710 770 L808 770&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L168 | <code>&nbsp;&nbsp;&lt;path class=&quot;line&quot; d=&quot;M1088 770 L1186 770&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L169 | （空行） | 空行/展示分隔。 |
| L170 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(238,874)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L171 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;soft-card&quot; width=&quot;350&quot; height=&quot;56&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L172 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;blue&quot; cx=&quot;32&quot; cy=&quot;28&quot; r=&quot;15&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L173 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M22 28 h20 M32 18 v20&quot; stroke=&quot;#fff&quot; stroke-width=&quot;5&quot; stroke-linecap=&quot;round&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L174 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label blue-text&quot; x=&quot;64&quot; y=&quot;24&quot;&gt;基线对比&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L175 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;64&quot; y=&quot;44&quot;&gt;data/eval/baseline.json&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L176 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L177 | （空行） | 空行/展示分隔。 |
| L178 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(676,874)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L179 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;soft-card&quot; width=&quot;350&quot; height=&quot;56&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L180 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;orange&quot; cx=&quot;32&quot; cy=&quot;28&quot; r=&quot;15&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L181 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;27&quot; y=&quot;33&quot;&gt;分&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L182 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label orange-text&quot; x=&quot;64&quot; y=&quot;24&quot;&gt;质量评分&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L183 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;64&quot; y=&quot;44&quot;&gt;相关性、准确性、完整性&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L184 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L185 | （空行） | 空行/展示分隔。 |
| L186 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(1114,874)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L187 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;soft-card&quot; width=&quot;350&quot; height=&quot;56&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L188 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;green&quot; cx=&quot;32&quot; cy=&quot;28&quot; r=&quot;15&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L189 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M23 28 L30 36 L43 19&quot; stroke=&quot;#fff&quot; stroke-width=&quot;5&quot; fill=&quot;none&quot; stroke-linecap=&quot;round&quot; stroke-linejoin=&quot;round&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L190 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label green-text&quot; x=&quot;64&quot; y=&quot;24&quot;&gt;优化建议&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L191 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;64&quot; y=&quot;44&quot;&gt;定位退化并反哺规则和知识库&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L192 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L193 | （空行） | 空行/展示分隔。 |
| L194 | <code>&nbsp;&nbsp;&lt;path class=&quot;blue-line dashed&quot; d=&quot;M520 874 C520 842 534 828 570 828&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L195 | <code>&nbsp;&nbsp;&lt;path class=&quot;green-line dashed&quot; d=&quot;M1288 874 C1288 846 1308 836 1326 828&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L196 | <code>&lt;/svg&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |

## 结合全项目：设计缺口与增强方向

- 需要与代码版本一起更新；图中的主辅协作、监控、部署语义不能代替对应函数证据。
- 本解读对重复坐标和配色简略，保留逐行位置；重点读可见标签和它连接的实际模块。

**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。
