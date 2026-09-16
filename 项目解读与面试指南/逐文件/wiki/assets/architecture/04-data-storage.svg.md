# wiki/assets/architecture/04-data-storage.svg 解读

## 输入、输出与流向

**定位：** 静态 SVG 展示资产：04-data-storage.svg

**输入：** XML 中的画布、样式、图形、文本和连接线。

**输出 / 副作用：** 浏览器/Markdown 渲染后的架构图或宣传海报；无业务数据存储副作用。

**流向：** svg 画布→defs 样式/箭头→rect/text/path 等元素→静态图片。图中连线是作者画出的表达，不会执行 Python 调用。

[返回阅读入口](../../../../README.md) · [对照原文件](../../../../../wiki/assets/architecture/04-data-storage.svg)

当前工作区快照：148 行。原始行号列对应原文件；空白和纯注释可略读。 SHA-256：`b7db491493c4962bb142f67eb8c30126c1353cf79320240bb8be0f97691495bf`。

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
| L24 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.blue-text { fill: #245ca8; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L25 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.blue { fill: #3165b7; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L26 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.green { fill: #14945b; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L27 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.orange { fill: #f47d22; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L28 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.purple { fill: #6045a9; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L29 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.line { stroke: #aeb8c4; stroke-width: 3; fill: none; marker-end: url(#arrow); }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L30 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.green-line { stroke: #14945b; stroke-width: 3; fill: none; marker-end: url(#arrow-green); }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L31 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.dashed { stroke-dasharray: 9 9; }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L32 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;.shadow { filter: url(#shadow); }</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L33 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;/style&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L34 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;filter id=&quot;shadow&quot; x=&quot;-20%&quot; y=&quot;-20%&quot; width=&quot;140%&quot; height=&quot;140%&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L35 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;feDropShadow dx=&quot;0&quot; dy=&quot;6&quot; stdDeviation=&quot;8&quot; flood-color=&quot;#d8e1df&quot; flood-opacity=&quot;0.42&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L36 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;/filter&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L37 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;marker id=&quot;arrow&quot; viewBox=&quot;0 0 10 10&quot; refX=&quot;9&quot; refY=&quot;5&quot; markerWidth=&quot;8&quot; markerHeight=&quot;8&quot; orient=&quot;auto&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L38 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M 0 0 L 10 5 L 0 10 z&quot; fill=&quot;#aeb8c4&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L39 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;/marker&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L40 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;marker id=&quot;arrow-green&quot; viewBox=&quot;0 0 10 10&quot; refX=&quot;9&quot; refY=&quot;5&quot; markerWidth=&quot;8&quot; markerHeight=&quot;8&quot; orient=&quot;auto&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |

### L41 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L41 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M 0 0 L 10 5 L 0 10 z&quot; fill=&quot;#14945b&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L42 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;/marker&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L43 | <code>&nbsp;&nbsp;&lt;/defs&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L44 | （空行） | 空行/展示分隔。 |
| L45 | <code>&nbsp;&nbsp;&lt;rect class=&quot;bg&quot; width=&quot;1600&quot; height=&quot;1000&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L46 | （空行） | 空行/展示分隔。 |
| L47 | <code>&nbsp;&nbsp;&lt;!-- Header --&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L48 | <code>&nbsp;&nbsp;&lt;rect class=&quot;header shadow&quot; x=&quot;32&quot; y=&quot;28&quot; width=&quot;1536&quot; height=&quot;112&quot; rx=&quot;18&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L49 | <code>&nbsp;&nbsp;&lt;text class=&quot;title&quot; x=&quot;66&quot; y=&quot;78&quot;&gt;数据与存储架构&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L50 | <code>&nbsp;&nbsp;&lt;text class=&quot;subtitle&quot; x=&quot;66&quot; y=&quot;110&quot;&gt;Redis 管短期工作记忆，ChromaDB 管知识库、情景记忆和用户画像，文件目录管理可热加载规则&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L51 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(1292,58)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;soft-card&quot; width=&quot;226&quot; height=&quot;48&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L53 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;green&quot; cx=&quot;28&quot; cy=&quot;24&quot; r=&quot;14&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;23&quot; y=&quot;29&quot;&gt;分&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;small&quot; x=&quot;52&quot; y=&quot;30&quot;&gt;短期 / 长期 / 配置分层&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L56 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L57 | （空行） | 空行/展示分隔。 |
| L58 | <code>&nbsp;&nbsp;&lt;!-- Storage columns --&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L59 | <code>&nbsp;&nbsp;&lt;rect class=&quot;panel shadow&quot; x=&quot;32&quot; y=&quot;170&quot; width=&quot;1536&quot; height=&quot;650&quot; rx=&quot;18&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L60 | <code>&nbsp;&nbsp;&lt;rect class=&quot;band&quot; x=&quot;62&quot; y=&quot;198&quot; width=&quot;1476&quot; height=&quot;72&quot; rx=&quot;14&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L61 | <code>&nbsp;&nbsp;&lt;text class=&quot;section-title&quot; x=&quot;92&quot; y=&quot;244&quot;&gt;存储分层：把会话状态、向量知识和文件规则拆开管理&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L62 | （空行） | 空行/展示分隔。 |
| L63 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(90,318)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L64 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card green-card&quot; width=&quot;420&quot; height=&quot;430&quot; rx=&quot;14&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L65 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;green&quot; cx=&quot;54&quot; cy=&quot;52&quot; r=&quot;25&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L66 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;49&quot; y=&quot;58&quot;&gt;1&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L67 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label green-text&quot; x=&quot;96&quot; y=&quot;58&quot;&gt;Redis 工作记忆&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L68 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;96&quot; y=&quot;86&quot;&gt;短期会话状态，强调速度和过期控制&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L69 | （空行） | 空行/展示分隔。 |
| L70 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card&quot; x=&quot;44&quot; y=&quot;122&quot; width=&quot;332&quot; height=&quot;74&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L71 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label&quot; x=&quot;76&quot; y=&quot;152&quot;&gt;最近消息&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;76&quot; y=&quot;178&quot;&gt;保存当前会话上下文&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L73 | （空行） | 空行/展示分隔。 |
| L74 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card&quot; x=&quot;44&quot; y=&quot;224&quot; width=&quot;332&quot; height=&quot;74&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L75 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label&quot; x=&quot;76&quot; y=&quot;254&quot;&gt;TTL 过期&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L76 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;76&quot; y=&quot;280&quot;&gt;短期记忆自动清理&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L77 | （空行） | 空行/展示分隔。 |
| L78 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card&quot; x=&quot;44&quot; y=&quot;326&quot; width=&quot;332&quot; height=&quot;74&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L79 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label&quot; x=&quot;76&quot; y=&quot;356&quot;&gt;压缩摘要入口&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L80 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;76&quot; y=&quot;382&quot;&gt;长对话达到阈值后触发&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |

### L81 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L81 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L82 | （空行） | 空行/展示分隔。 |
| L83 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(590,318)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card blue-card&quot; width=&quot;420&quot; height=&quot;430&quot; rx=&quot;14&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;blue&quot; cx=&quot;54&quot; cy=&quot;52&quot; r=&quot;25&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L86 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;49&quot; y=&quot;58&quot;&gt;2&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label blue-text&quot; x=&quot;96&quot; y=&quot;58&quot;&gt;ChromaDB 向量存储&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;96&quot; y=&quot;86&quot;&gt;长期语义检索，支撑 RAG 和个性化&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L89 | （空行） | 空行/展示分隔。 |
| L90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card&quot; x=&quot;44&quot; y=&quot;122&quot; width=&quot;332&quot; height=&quot;74&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L91 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label&quot; x=&quot;76&quot; y=&quot;152&quot;&gt;知识库&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L92 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;76&quot; y=&quot;178&quot;&gt;knowledge_base / RAG 召回&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L93 | （空行） | 空行/展示分隔。 |
| L94 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card&quot; x=&quot;44&quot; y=&quot;224&quot; width=&quot;332&quot; height=&quot;74&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L95 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label&quot; x=&quot;76&quot; y=&quot;254&quot;&gt;情景记忆&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L96 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;76&quot; y=&quot;280&quot;&gt;episodic 历史摘要&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L97 | （空行） | 空行/展示分隔。 |
| L98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card&quot; x=&quot;44&quot; y=&quot;326&quot; width=&quot;332&quot; height=&quot;74&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L99 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label&quot; x=&quot;76&quot; y=&quot;356&quot;&gt;用户画像&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L100 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;76&quot; y=&quot;382&quot;&gt;user_profile 偏好与事实&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L101 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L102 | （空行） | 空行/展示分隔。 |
| L103 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(1090,318)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L104 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card orange-card&quot; width=&quot;420&quot; height=&quot;430&quot; rx=&quot;14&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;orange&quot; cx=&quot;54&quot; cy=&quot;52&quot; r=&quot;25&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L106 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;49&quot; y=&quot;58&quot;&gt;3&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L107 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label orange-text&quot; x=&quot;96&quot; y=&quot;58&quot;&gt;文件型配置&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L108 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;96&quot; y=&quot;86&quot;&gt;便于挂载、热加载和版本化维护&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L109 | （空行） | 空行/展示分隔。 |
| L110 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card&quot; x=&quot;44&quot; y=&quot;122&quot; width=&quot;332&quot; height=&quot;74&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L111 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label&quot; x=&quot;76&quot; y=&quot;152&quot;&gt;演示知识库&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L112 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;76&quot; y=&quot;178&quot;&gt;data/demo_docs&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L113 | （空行） | 空行/展示分隔。 |
| L114 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card purple-card&quot; x=&quot;44&quot; y=&quot;224&quot; width=&quot;332&quot; height=&quot;74&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label purple-text&quot; x=&quot;76&quot; y=&quot;254&quot;&gt;动态 Skills&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;76&quot; y=&quot;280&quot;&gt;skills/*/SKILL.md&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L117 | （空行） | 空行/展示分隔。 |
| L118 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;rect class=&quot;card&quot; x=&quot;44&quot; y=&quot;326&quot; width=&quot;332&quot; height=&quot;74&quot; rx=&quot;12&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L119 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label&quot; x=&quot;76&quot; y=&quot;356&quot;&gt;评测基线&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L120 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;76&quot; y=&quot;382&quot;&gt;data/eval/baseline.json&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |

### L121 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L121 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L122 | （空行） | 空行/展示分隔。 |
| L123 | <code>&nbsp;&nbsp;&lt;path class=&quot;line&quot; d=&quot;M510 676 C548 686 552 676 590 662&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L124 | <code>&nbsp;&nbsp;&lt;path class=&quot;line&quot; d=&quot;M1090 476 C1048 476 1038 476 1010 476&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L125 | <code>&nbsp;&nbsp;&lt;path class=&quot;line&quot; d=&quot;M1090 578 C1042 596 1034 632 1010 662&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L126 | <code>&nbsp;&nbsp;&lt;path class=&quot;line&quot; d=&quot;M1090 680 C1048 716 1008 746 948 748&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L127 | （空行） | 空行/展示分隔。 |
| L128 | <code>&nbsp;&nbsp;&lt;!-- Bottom notes --&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L129 | <code>&nbsp;&nbsp;&lt;rect class=&quot;panel shadow&quot; x=&quot;32&quot; y=&quot;850&quot; width=&quot;1536&quot; height=&quot;114&quot; rx=&quot;18&quot;/&gt;</code> | 绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。 |
| L130 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(92,878)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L131 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;green&quot; cx=&quot;30&quot; cy=&quot;30&quot; r=&quot;18&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L132 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M21 30 L28 38 L41 21&quot; stroke=&quot;#fff&quot; stroke-width=&quot;5&quot; fill=&quot;none&quot; stroke-linecap=&quot;round&quot; stroke-linejoin=&quot;round&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L133 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label green-text&quot; x=&quot;64&quot; y=&quot;24&quot;&gt;会话优先读 Redis&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L134 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;64&quot; y=&quot;52&quot;&gt;保证多轮对话响应速度，过期后通过摘要回补长期记忆&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L135 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L136 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(600,878)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L137 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;blue&quot; cx=&quot;30&quot; cy=&quot;30&quot; r=&quot;18&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L138 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;path d=&quot;M18 30 h24 M30 18 v24&quot; stroke=&quot;#fff&quot; stroke-width=&quot;5&quot; stroke-linecap=&quot;round&quot;/&gt;</code> | 画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。 |
| L139 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label blue-text&quot; x=&quot;64&quot; y=&quot;24&quot;&gt;长期语义统一进 ChromaDB&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L140 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;64&quot; y=&quot;52&quot;&gt;知识、历史摘要和画像都可参与检索增强&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L141 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L142 | <code>&nbsp;&nbsp;&lt;g transform=&quot;translate(1110,878)&quot;&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L143 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;circle class=&quot;orange&quot; cx=&quot;30&quot; cy=&quot;30&quot; r=&quot;18&quot;/&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L144 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;tiny&quot; x=&quot;24&quot; y=&quot;35&quot;&gt;热&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;label orange-text&quot; x=&quot;64&quot; y=&quot;24&quot;&gt;文件配置便于热加载&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L146 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&lt;text class=&quot;muted&quot; x=&quot;64&quot; y=&quot;52&quot;&gt;Skills 和评测基线可随部署目录挂载&lt;/text&gt;</code> | 图上的可见标签；表示架构说明，不建立实际代码调用。 |
| L147 | <code>&nbsp;&nbsp;&lt;/g&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |
| L148 | <code>&lt;/svg&gt;</code> | SVG 样式/分组/图形结构；重复显示细节可略读。 |

## 结合全项目：设计缺口与增强方向

- 需要与代码版本一起更新；图中的主辅协作、监控、部署语义不能代替对应函数证据。
- 本解读对重复坐标和配色简略，保留逐行位置；重点读可见标签和它连接的实际模块。

**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。
