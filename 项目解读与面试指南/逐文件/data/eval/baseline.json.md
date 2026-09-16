# data/eval/baseline.json 解读

## 输入、输出与流向

**定位：** 现存历史评测快照。

**输入：** EndToEndEvaluator._load_baseline 读取 JSON。

**输出 / 副作用：** 用于下次均分相对比较的 EvalReport；新运行会覆盖此文件。

**流向：** 磁盘 JSON→报告对象→与本轮均分对比→保存最新报告。

[返回阅读入口](../../../README.md) · [对照原文件](../../../../data/eval/baseline.json)

当前工作区快照：244 行。原始行号列对应原文件；空白和纯注释可略读。 SHA-256：`4527f73b73ed1d11392121c53b3c6bb7d27b746b4264a67f7fd897a0dbe30d7e`。

## 按原行号阅读

读法：先看每个函数前的因果解释，再看逐行表。多行参数、词表、提示文本续行从属于起始语句；关键行另加粗说明。


### L1 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L1 | <code>{</code> | JSON 结构边界。 |
| L2 | <code>&nbsp;&nbsp;&quot;timestamp&quot;: &quot;2026-05-31T07:06:07.150090&quot;,</code> | 数据字段 <code>timestamp</code>；它是材料/历史结果，不是本次运行事实。 |
| L3 | <code>&nbsp;&nbsp;&quot;total&quot;: 8,</code> | 数据字段 <code>total</code>；它是材料/历史结果，不是本次运行事实。 |
| L4 | <code>&nbsp;&nbsp;&quot;passed&quot;: 8,</code> | 数据字段 <code>passed</code>；它是材料/历史结果，不是本次运行事实。 |
| L5 | <code>&nbsp;&nbsp;&quot;pass_rate&quot;: 1.0,</code> | 数据字段 <code>pass_rate</code>；它是材料/历史结果，不是本次运行事实。 |
| L6 | <code>&nbsp;&nbsp;&quot;avg_scores&quot;: {</code> | 数据字段 <code>avg_scores</code>；它是材料/历史结果，不是本次运行事实。 |
| L7 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;relevance&quot;: 1.0,</code> | 数据字段 <code>relevance</code>；它是材料/历史结果，不是本次运行事实。 |
| L8 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;accuracy&quot;: 0.9786,</code> | 数据字段 <code>accuracy</code>；它是材料/历史结果，不是本次运行事实。 |
| L9 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;completeness&quot;: 0.8,</code> | 数据字段 <code>completeness</code>；它是材料/历史结果，不是本次运行事实。 |
| L10 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;helpfulness&quot;: 0.8857,</code> | 数据字段 <code>helpfulness</code>；它是材料/历史结果，不是本次运行事实。 |
| L11 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;intent_accuracy&quot;: 1.0</code> | 数据字段 <code>intent_accuracy</code>；它是材料/历史结果，不是本次运行事实。 |
| L12 | <code>&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L13 | <code>&nbsp;&nbsp;&quot;regressions&quot;: [],</code> | 数据字段 <code>regressions</code>；它是材料/历史结果，不是本次运行事实。 |
| L14 | <code>&nbsp;&nbsp;&quot;recommendations&quot;: [</code> | 数据字段 <code>recommendations</code>；它是材料/历史结果，不是本次运行事实。 |
| L15 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&quot;所有指标均达标，继续保持&quot;</code> | 数据字段 <code>&quot;所有指标均达标，继续保持&quot;</code>；它是材料/历史结果，不是本次运行事实。 |
| L16 | <code>&nbsp;&nbsp;],</code> | JSON 结构边界。 |
| L17 | <code>&nbsp;&nbsp;&quot;results&quot;: [</code> | 数据字段 <code>results</code>；它是材料/历史结果，不是本次运行事实。 |
| L18 | <code>&nbsp;&nbsp;&nbsp;&nbsp;{</code> | JSON 结构边界。 |
| L19 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;test_id&quot;: &quot;intent_recognition&quot;,</code> | 数据字段 <code>test_id</code>；它是材料/历史结果，不是本次运行事实。 |
| L20 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;passed&quot;: true,</code> | 数据字段 <code>passed</code>；它是材料/历史结果，不是本次运行事实。 |
| L21 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;scores&quot;: {</code> | 数据字段 <code>scores</code>；它是材料/历史结果，不是本次运行事实。 |
| L22 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;accuracy&quot;: 1.0,</code> | 数据字段 <code>accuracy</code>；它是材料/历史结果，不是本次运行事实。 |
| L23 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;macro_f1&quot;: 1.0</code> | 数据字段 <code>macro_f1</code>；它是材料/历史结果，不是本次运行事实。 |
| L24 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L25 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;detail&quot;: &quot;准确率 100.0%，Macro-F1 1.000&quot;,</code> | 数据字段 <code>detail</code>；它是材料/历史结果，不是本次运行事实。 |
| L26 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;metadata&quot;: {</code> | 数据字段 <code>metadata</code>；它是材料/历史结果，不是本次运行事实。 |
| L27 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;total&quot;: 8,</code> | 数据字段 <code>total</code>；它是材料/历史结果，不是本次运行事实。 |
| L28 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;correct&quot;: 8,</code> | 数据字段 <code>correct</code>；它是材料/历史结果，不是本次运行事实。 |
| L29 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;cases&quot;: [</code> | 数据字段 <code>cases</code>；它是材料/历史结果，不是本次运行事实。 |
| L30 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{</code> | JSON 结构边界。 |
| L31 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;message&quot;: &quot;我的订单什么时候到？&quot;,</code> | 数据字段 <code>message</code>；它是材料/历史结果，不是本次运行事实。 |
| L32 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;expected&quot;: &quot;query&quot;,</code> | 数据字段 <code>expected</code>；它是材料/历史结果，不是本次运行事实。 |
| L33 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;predicted&quot;: &quot;query&quot;,</code> | 数据字段 <code>predicted</code>；它是材料/历史结果，不是本次运行事实。 |
| L34 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;confidence&quot;: 0.95,</code> | 数据字段 <code>confidence</code>；它是材料/历史结果，不是本次运行事实。 |
| L35 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;reasoning&quot;: &quot;用户询问订单到达时间，属于查询类意图。&quot;</code> | 数据字段 <code>reasoning</code>；它是材料/历史结果，不是本次运行事实。 |
| L36 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L37 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{</code> | JSON 结构边界。 |
| L38 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;message&quot;: &quot;帮我取消订单&quot;,</code> | 数据字段 <code>message</code>；它是材料/历史结果，不是本次运行事实。 |
| L39 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;expected&quot;: &quot;request&quot;,</code> | 数据字段 <code>expected</code>；它是材料/历史结果，不是本次运行事实。 |
| L40 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;predicted&quot;: &quot;request&quot;,</code> | 数据字段 <code>predicted</code>；它是材料/历史结果，不是本次运行事实。 |

### L41 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L41 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;confidence&quot;: 1.0,</code> | 数据字段 <code>confidence</code>；它是材料/历史结果，不是本次运行事实。 |
| L42 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;reasoning&quot;: &quot;用户明确要求执行取消订单的操作，属于请求类意图。&quot;</code> | 数据字段 <code>reasoning</code>；它是材料/历史结果，不是本次运行事实。 |
| L43 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L44 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{</code> | JSON 结构边界。 |
| L45 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;message&quot;: &quot;你们服务太差了！&quot;,</code> | 数据字段 <code>message</code>；它是材料/历史结果，不是本次运行事实。 |
| L46 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;expected&quot;: &quot;complaint&quot;,</code> | 数据字段 <code>expected</code>；它是材料/历史结果，不是本次运行事实。 |
| L47 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;predicted&quot;: &quot;complaint&quot;,</code> | 数据字段 <code>predicted</code>；它是材料/历史结果，不是本次运行事实。 |
| L48 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;confidence&quot;: 0.95,</code> | 数据字段 <code>confidence</code>；它是材料/历史结果，不是本次运行事实。 |
| L49 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;reasoning&quot;: &quot;用户直接表达了对服务的不满，属于投诉类意图。&quot;</code> | 数据字段 <code>reasoning</code>；它是材料/历史结果，不是本次运行事实。 |
| L50 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L51 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{</code> | JSON 结构边界。 |
| L52 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;message&quot;: &quot;应用一直报500错误&quot;,</code> | 数据字段 <code>message</code>；它是材料/历史结果，不是本次运行事实。 |
| L53 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;expected&quot;: &quot;technical&quot;,</code> | 数据字段 <code>expected</code>；它是材料/历史结果，不是本次运行事实。 |
| L54 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;predicted&quot;: &quot;technical&quot;,</code> | 数据字段 <code>predicted</code>；它是材料/历史结果，不是本次运行事实。 |
| L55 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;confidence&quot;: 0.95,</code> | 数据字段 <code>confidence</code>；它是材料/历史结果，不是本次运行事实。 |
| L56 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;reasoning&quot;: &quot;用户报告应用持续出现500错误，属于技术问题&quot;</code> | 数据字段 <code>reasoning</code>；它是材料/历史结果，不是本次运行事实。 |
| L57 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L58 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{</code> | JSON 结构边界。 |
| L59 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;message&quot;: &quot;为什么扣了两次款？&quot;,</code> | 数据字段 <code>message</code>；它是材料/历史结果，不是本次运行事实。 |
| L60 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;expected&quot;: &quot;billing&quot;,</code> | 数据字段 <code>expected</code>；它是材料/历史结果，不是本次运行事实。 |
| L61 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;predicted&quot;: &quot;billing&quot;,</code> | 数据字段 <code>predicted</code>；它是材料/历史结果，不是本次运行事实。 |
| L62 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;confidence&quot;: 0.95,</code> | 数据字段 <code>confidence</code>；它是材料/历史结果，不是本次运行事实。 |
| L63 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;reasoning&quot;: &quot;用户询问扣款问题，明确涉及账单费用，符合billing意图&quot;</code> | 数据字段 <code>reasoning</code>；它是材料/历史结果，不是本次运行事实。 |
| L64 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L65 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{</code> | JSON 结构边界。 |
| L66 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;message&quot;: &quot;我要投诉，转人工！&quot;,</code> | 数据字段 <code>message</code>；它是材料/历史结果，不是本次运行事实。 |
| L67 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;expected&quot;: &quot;escalation&quot;,</code> | 数据字段 <code>expected</code>；它是材料/历史结果，不是本次运行事实。 |
| L68 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;predicted&quot;: &quot;escalation&quot;,</code> | 数据字段 <code>predicted</code>；它是材料/历史结果，不是本次运行事实。 |
| L69 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;confidence&quot;: 0.95,</code> | 数据字段 <code>confidence</code>；它是材料/历史结果，不是本次运行事实。 |
| L70 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;reasoning&quot;: &quot;用户明确要求投诉并转人工，符合升级处理意图&quot;</code> | 数据字段 <code>reasoning</code>；它是材料/历史结果，不是本次运行事实。 |
| L71 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L72 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{</code> | JSON 结构边界。 |
| L73 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;message&quot;: &quot;你好&quot;,</code> | 数据字段 <code>message</code>；它是材料/历史结果，不是本次运行事实。 |
| L74 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;expected&quot;: &quot;greeting&quot;,</code> | 数据字段 <code>expected</code>；它是材料/历史结果，不是本次运行事实。 |
| L75 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;predicted&quot;: &quot;greeting&quot;,</code> | 数据字段 <code>predicted</code>；它是材料/历史结果，不是本次运行事实。 |
| L76 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;confidence&quot;: 1.0,</code> | 数据字段 <code>confidence</code>；它是材料/历史结果，不是本次运行事实。 |
| L77 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;reasoning&quot;: &quot;用户消息为&#x27;你好&#x27;，与示例中问候意图完全一致。&quot;</code> | 数据字段 <code>reasoning</code>；它是材料/历史结果，不是本次运行事实。 |
| L78 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L79 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{</code> | JSON 结构边界。 |
| L80 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;message&quot;: &quot;修改我的邮箱地址&quot;,</code> | 数据字段 <code>message</code>；它是材料/历史结果，不是本次运行事实。 |

### L81 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L81 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;expected&quot;: &quot;account&quot;,</code> | 数据字段 <code>expected</code>；它是材料/历史结果，不是本次运行事实。 |
| L82 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;predicted&quot;: &quot;account&quot;,</code> | 数据字段 <code>predicted</code>；它是材料/历史结果，不是本次运行事实。 |
| L83 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;confidence&quot;: 0.95,</code> | 数据字段 <code>confidence</code>；它是材料/历史结果，不是本次运行事实。 |
| L84 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;reasoning&quot;: &quot;用户明确要求修改邮箱地址，属于账户信息变更操作。&quot;</code> | 数据字段 <code>reasoning</code>；它是材料/历史结果，不是本次运行事实。 |
| L85 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | JSON 结构边界。 |
| L86 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;]</code> | JSON 结构边界。 |
| L87 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | JSON 结构边界。 |
| L88 | <code>&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L89 | <code>&nbsp;&nbsp;&nbsp;&nbsp;{</code> | JSON 结构边界。 |
| L90 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;test_id&quot;: &quot;dialog_0&quot;,</code> | 数据字段 <code>test_id</code>；它是材料/历史结果，不是本次运行事实。 |
| L91 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;passed&quot;: true,</code> | 数据字段 <code>passed</code>；它是材料/历史结果，不是本次运行事实。 |
| L92 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;scores&quot;: {</code> | 数据字段 <code>scores</code>；它是材料/历史结果，不是本次运行事实。 |
| L93 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;relevance&quot;: 1.0,</code> | 数据字段 <code>relevance</code>；它是材料/历史结果，不是本次运行事实。 |
| L94 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;accuracy&quot;: 1.0,</code> | 数据字段 <code>accuracy</code>；它是材料/历史结果，不是本次运行事实。 |
| L95 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;completeness&quot;: 0.6,</code> | 数据字段 <code>completeness</code>；它是材料/历史结果，不是本次运行事实。 |
| L96 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;helpfulness&quot;: 0.7,</code> | 数据字段 <code>helpfulness</code>；它是材料/历史结果，不是本次运行事实。 |
| L97 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;overall&quot;: 0.825</code> | 数据字段 <code>overall</code>；它是材料/历史结果，不是本次运行事实。 |
| L98 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L99 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;detail&quot;: &quot;Q: 我的订单 #12345 还没到，已经超时了... → 综合评分 0.825&quot;,</code> | 数据字段 <code>detail</code>；它是材料/历史结果，不是本次运行事实。 |
| L100 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;metadata&quot;: {</code> | 数据字段 <code>metadata</code>；它是材料/历史结果，不是本次运行事实。 |
| L101 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;question&quot;: &quot;我的订单 #12345 还没到，已经超时了&quot;,</code> | 数据字段 <code>question</code>；它是材料/历史结果，不是本次运行事实。 |
| L102 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;response&quot;: &quot;您好，非常抱歉给您带来不便。我查一下您的订单 #12345 的物流情况。请稍等。请问您方便提供一下联系方式或收货地址吗？这样我可以更高效地核实问题。&quot;,</code> | 数据字段 <code>response</code>；它是材料/历史结果，不是本次运行事实。 |
| L103 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;agent_type&quot;: &quot;general&quot;,</code> | 数据字段 <code>agent_type</code>；它是材料/历史结果，不是本次运行事实。 |
| L104 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;intent&quot;: &quot;complaint&quot;,</code> | 数据字段 <code>intent</code>；它是材料/历史结果，不是本次运行事实。 |
| L105 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;turn&quot;: 0,</code> | 数据字段 <code>turn</code>；它是材料/历史结果，不是本次运行事实。 |
| L106 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;conv_id&quot;: &quot;eval_0&quot;,</code> | 数据字段 <code>conv_id</code>；它是材料/历史结果，不是本次运行事实。 |
| L107 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;judge_failed&quot;: false,</code> | 数据字段 <code>judge_failed</code>；它是材料/历史结果，不是本次运行事实。 |
| L108 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;judge_error&quot;: null</code> | 数据字段 <code>judge_error</code>；它是材料/历史结果，不是本次运行事实。 |
| L109 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | JSON 结构边界。 |
| L110 | <code>&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L111 | <code>&nbsp;&nbsp;&nbsp;&nbsp;{</code> | JSON 结构边界。 |
| L112 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;test_id&quot;: &quot;dialog_1&quot;,</code> | 数据字段 <code>test_id</code>；它是材料/历史结果，不是本次运行事实。 |
| L113 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;passed&quot;: true,</code> | 数据字段 <code>passed</code>；它是材料/历史结果，不是本次运行事实。 |
| L114 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;scores&quot;: {</code> | 数据字段 <code>scores</code>；它是材料/历史结果，不是本次运行事实。 |
| L115 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;relevance&quot;: 1.0,</code> | 数据字段 <code>relevance</code>；它是材料/历史结果，不是本次运行事实。 |
| L116 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;accuracy&quot;: 1.0,</code> | 数据字段 <code>accuracy</code>；它是材料/历史结果，不是本次运行事实。 |
| L117 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;completeness&quot;: 1.0,</code> | 数据字段 <code>completeness</code>；它是材料/历史结果，不是本次运行事实。 |
| L118 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;helpfulness&quot;: 1.0,</code> | 数据字段 <code>helpfulness</code>；它是材料/历史结果，不是本次运行事实。 |
| L119 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;overall&quot;: 1.0</code> | 数据字段 <code>overall</code>；它是材料/历史结果，不是本次运行事实。 |
| L120 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |

### L121 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L121 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;detail&quot;: &quot;Q: 应用登录一直报错 401... → 综合评分 1.000&quot;,</code> | 数据字段 <code>detail</code>；它是材料/历史结果，不是本次运行事实。 |
| L122 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;metadata&quot;: {</code> | 数据字段 <code>metadata</code>；它是材料/历史结果，不是本次运行事实。 |
| L123 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;question&quot;: &quot;应用登录一直报错 401&quot;,</code> | 数据字段 <code>question</code>；它是材料/历史结果，不是本次运行事实。 |
| L124 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;response&quot;: &quot;收到您关于应用登录报错 401 的问题。401 状态码通常表示**身份验证失败**，即用户身份未被系统认可或凭证无效。\n\n为了帮助您快速排查，请按以下步骤操作：\n\n### 第一步：基础排查（前端/用户侧）\n\n1.  **检查账号密码是否正确**\n    -   确认是否输入了正确的用户名/邮箱和密码。\n    -   注意是否开启了**大小写锁定键（Caps Lock）** 或使用了全角字符（例如 “Ａ” 而非 “A”）。\n    -   尝试在浏览器无痕/隐私窗口登录，排除缓存干扰。\n2.  **清除浏览器缓存和 Cookie**\n    -   401 也可能由过期的 Token 或 Session 引起。清除后重新尝试登录。\n3.  **确认网络环境**\n    -   如果使用公司内网或 VPN，请确认网络连接正常，且没有触发防火墙或代理拦截。\n\n### 第二步：进阶排查（若第一步无效）\n\n如果基础操作后问题依旧，需进一步判断：\n\n1.  **检查请求的 API 地址**\n    -   确认前端请求的登录接口 URL 与后端配置的完全一致（包括协议、域名、端口）。\n2.  **查看请求头与 Token**\n    -   使用浏览器开发者工具（F12 &gt; Network 标签），找到登录失败的请求。\n    -   查看 **Response Headers** 中的 `WWW-Authenticate` 字段，它会提示具体的认证方案（如 Bearer / Basic / Digest）。\n    -   查看是否携带了正确的 `Authorization` 头，或是否因 Token 过期/无效被后端拒绝。\n\n### 第三步：后台/服务器侧（需更高权限）\n\n&gt; **说明**：以下操作需要**系统管理员或后台运维权限**，如果您是普通用户，请将以下信息反馈给技术负责人。\n\n1.  **检查后端服务状态**\n    -   登录服务器，查看应用服务（如 Nginx、Tomcat、Node.js 等）是否正常运行。\n    -   检查认证服务（如 OAuth、LDAP、JWT 签发服务）是否能正常响应。\n2.  **查看应用日志**\n    -   搜索关键词 `401` 或 `Unauthorized`，确认具体报错信息。\n    -   常见原因：\n        -   认证密钥（Secret Key）在环境变量或配置文件中错误。\n        -   用户数据库连接异常或用户记录被锁定/禁用。\n        -   Token 黑名单机制误判了正常请求。\n3.  **检查白名单/IP 限制**\n    -   确认服务器是否对特定 IP 段或地区做了访问限制。\n\n---\n\n### 当前最推荐您尝试的操作：\n\n1.  **立即重置密码**（如果是个人账号问题）。\n2.  **联系管理员确认账号状态**（未激活、被锁定、已过期）。\n3.  **提供以下信息给技术支持**，以便快速定位：\n    -   报错时间的完整截图（含浏览器控制台 Network 面板）。\n    -   完整错误日志或响应体内容（例如：`{\&quot;error\&quot;:\&quot;invalid_token\&quot;}`）。\n\n若以上步骤仍无法解决，请提供**更详细的错误信息**（如其他用户是否正常、系统版本变动等），我会为您做更深层分析。&quot;,</code> | 数据字段 <code>response</code>；它是材料/历史结果，不是本次运行事实。 |
| L125 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;agent_type&quot;: &quot;technical&quot;,</code> | 数据字段 <code>agent_type</code>；它是材料/历史结果，不是本次运行事实。 |
| L126 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;intent&quot;: &quot;technical&quot;,</code> | 数据字段 <code>intent</code>；它是材料/历史结果，不是本次运行事实。 |
| L127 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;turn&quot;: 0,</code> | 数据字段 <code>turn</code>；它是材料/历史结果，不是本次运行事实。 |
| L128 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;conv_id&quot;: &quot;eval_1&quot;,</code> | 数据字段 <code>conv_id</code>；它是材料/历史结果，不是本次运行事实。 |
| L129 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;judge_failed&quot;: false,</code> | 数据字段 <code>judge_failed</code>；它是材料/历史结果，不是本次运行事实。 |
| L130 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;judge_error&quot;: null</code> | 数据字段 <code>judge_error</code>；它是材料/历史结果，不是本次运行事实。 |
| L131 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | JSON 结构边界。 |
| L132 | <code>&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L133 | <code>&nbsp;&nbsp;&nbsp;&nbsp;{</code> | JSON 结构边界。 |
| L134 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;test_id&quot;: &quot;dialog_2&quot;,</code> | 数据字段 <code>test_id</code>；它是材料/历史结果，不是本次运行事实。 |
| L135 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;passed&quot;: true,</code> | 数据字段 <code>passed</code>；它是材料/历史结果，不是本次运行事实。 |
| L136 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;scores&quot;: {</code> | 数据字段 <code>scores</code>；它是材料/历史结果，不是本次运行事实。 |
| L137 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;relevance&quot;: 1.0,</code> | 数据字段 <code>relevance</code>；它是材料/历史结果，不是本次运行事实。 |
| L138 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;accuracy&quot;: 0.95,</code> | 数据字段 <code>accuracy</code>；它是材料/历史结果，不是本次运行事实。 |
| L139 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;completeness&quot;: 0.8,</code> | 数据字段 <code>completeness</code>；它是材料/历史结果，不是本次运行事实。 |
| L140 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;helpfulness&quot;: 0.9,</code> | 数据字段 <code>helpfulness</code>；它是材料/历史结果，不是本次运行事实。 |
| L141 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;overall&quot;: 0.9125</code> | 数据字段 <code>overall</code>；它是材料/历史结果，不是本次运行事实。 |
| L142 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L143 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;detail&quot;: &quot;Q: 为什么这个月多扣了 50 块钱？... → 综合评分 0.912&quot;,</code> | 数据字段 <code>detail</code>；它是材料/历史结果，不是本次运行事实。 |
| L144 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;metadata&quot;: {</code> | 数据字段 <code>metadata</code>；它是材料/历史结果，不是本次运行事实。 |
| L145 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;question&quot;: &quot;为什么这个月多扣了 50 块钱？&quot;,</code> | 数据字段 <code>question</code>；它是材料/历史结果，不是本次运行事实。 |
| L146 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;response&quot;: &quot;您好，我理解您对账单金额变动的疑问。这50元可能来自以下原因：\n\n1. **订阅服务调整**：请检查是否有新增的会员服务（如云存储扩容、增值功能）或试用期结束转为付费。\n2. **基础费用变更**：部分套餐可能因促销到期或汇率波动产生临时调整。\n3. **一次性费用**：例如超量使用费、自动续费的代金券抵扣失效等。\n\n建议您提供以下信息以便进一步分析：\n- 账单上的具体项目名称\n- 扣款时间范围\n- 账户绑定的服务类型\n\n如果您需要正式核查或申请退款，需由人工客服调取后台记录。请点击“转人工”并提供账单截图，我会帮您转接处理。&quot;,</code> | 数据字段 <code>response</code>；它是材料/历史结果，不是本次运行事实。 |
| L147 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;agent_type&quot;: &quot;billing&quot;,</code> | 数据字段 <code>agent_type</code>；它是材料/历史结果，不是本次运行事实。 |
| L148 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;intent&quot;: &quot;billing&quot;,</code> | 数据字段 <code>intent</code>；它是材料/历史结果，不是本次运行事实。 |
| L149 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;turn&quot;: 0,</code> | 数据字段 <code>turn</code>；它是材料/历史结果，不是本次运行事实。 |
| L150 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;conv_id&quot;: &quot;eval_2&quot;,</code> | 数据字段 <code>conv_id</code>；它是材料/历史结果，不是本次运行事实。 |
| L151 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;judge_failed&quot;: false,</code> | 数据字段 <code>judge_failed</code>；它是材料/历史结果，不是本次运行事实。 |
| L152 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;judge_error&quot;: null</code> | 数据字段 <code>judge_error</code>；它是材料/历史结果，不是本次运行事实。 |
| L153 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | JSON 结构边界。 |
| L154 | <code>&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L155 | <code>&nbsp;&nbsp;&nbsp;&nbsp;{</code> | JSON 结构边界。 |
| L156 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;test_id&quot;: &quot;dialog_3&quot;,</code> | 数据字段 <code>test_id</code>；它是材料/历史结果，不是本次运行事实。 |
| L157 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;passed&quot;: true,</code> | 数据字段 <code>passed</code>；它是材料/历史结果，不是本次运行事实。 |
| L158 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;scores&quot;: {</code> | 数据字段 <code>scores</code>；它是材料/历史结果，不是本次运行事实。 |
| L159 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;relevance&quot;: 1.0,</code> | 数据字段 <code>relevance</code>；它是材料/历史结果，不是本次运行事实。 |
| L160 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;accuracy&quot;: 1.0,</code> | 数据字段 <code>accuracy</code>；它是材料/历史结果，不是本次运行事实。 |

### L161 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L161 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;completeness&quot;: 1.0,</code> | 数据字段 <code>completeness</code>；它是材料/历史结果，不是本次运行事实。 |
| L162 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;helpfulness&quot;: 1.0,</code> | 数据字段 <code>helpfulness</code>；它是材料/历史结果，不是本次运行事实。 |
| L163 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;overall&quot;: 1.0</code> | 数据字段 <code>overall</code>；它是材料/历史结果，不是本次运行事实。 |
| L164 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L165 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;detail&quot;: &quot;Q: 帮我把收货地址改成北京市朝阳区... → 综合评分 1.000&quot;,</code> | 数据字段 <code>detail</code>；它是材料/历史结果，不是本次运行事实。 |
| L166 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;metadata&quot;: {</code> | 数据字段 <code>metadata</code>；它是材料/历史结果，不是本次运行事实。 |
| L167 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;question&quot;: &quot;帮我把收货地址改成北京市朝阳区&quot;,</code> | 数据字段 <code>question</code>；它是材料/历史结果，不是本次运行事实。 |
| L168 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;response&quot;: &quot;好的，已为您更新收货地址为：北京市朝阳区。如需进一步修改，请随时告知。&quot;,</code> | 数据字段 <code>response</code>；它是材料/历史结果，不是本次运行事实。 |
| L169 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;agent_type&quot;: &quot;general&quot;,</code> | 数据字段 <code>agent_type</code>；它是材料/历史结果，不是本次运行事实。 |
| L170 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;intent&quot;: &quot;request&quot;,</code> | 数据字段 <code>intent</code>；它是材料/历史结果，不是本次运行事实。 |
| L171 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;turn&quot;: 0,</code> | 数据字段 <code>turn</code>；它是材料/历史结果，不是本次运行事实。 |
| L172 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;conv_id&quot;: &quot;eval_3&quot;,</code> | 数据字段 <code>conv_id</code>；它是材料/历史结果，不是本次运行事实。 |
| L173 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;judge_failed&quot;: false,</code> | 数据字段 <code>judge_failed</code>；它是材料/历史结果，不是本次运行事实。 |
| L174 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;judge_error&quot;: null</code> | 数据字段 <code>judge_error</code>；它是材料/历史结果，不是本次运行事实。 |
| L175 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | JSON 结构边界。 |
| L176 | <code>&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L177 | <code>&nbsp;&nbsp;&nbsp;&nbsp;{</code> | JSON 结构边界。 |
| L178 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;test_id&quot;: &quot;dialog_4_turn_0&quot;,</code> | 数据字段 <code>test_id</code>；它是材料/历史结果，不是本次运行事实。 |
| L179 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;passed&quot;: true,</code> | 数据字段 <code>passed</code>；它是材料/历史结果，不是本次运行事实。 |
| L180 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;scores&quot;: {</code> | 数据字段 <code>scores</code>；它是材料/历史结果，不是本次运行事实。 |
| L181 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;relevance&quot;: 1.0,</code> | 数据字段 <code>relevance</code>；它是材料/历史结果，不是本次运行事实。 |
| L182 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;accuracy&quot;: 1.0,</code> | 数据字段 <code>accuracy</code>；它是材料/历史结果，不是本次运行事实。 |
| L183 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;completeness&quot;: 0.6,</code> | 数据字段 <code>completeness</code>；它是材料/历史结果，不是本次运行事实。 |
| L184 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;helpfulness&quot;: 0.8,</code> | 数据字段 <code>helpfulness</code>；它是材料/历史结果，不是本次运行事实。 |
| L185 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;overall&quot;: 0.85</code> | 数据字段 <code>overall</code>；它是材料/历史结果，不是本次运行事实。 |
| L186 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L187 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;detail&quot;: &quot;Q: 你好，我想退款... → 综合评分 0.850&quot;,</code> | 数据字段 <code>detail</code>；它是材料/历史结果，不是本次运行事实。 |
| L188 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;metadata&quot;: {</code> | 数据字段 <code>metadata</code>；它是材料/历史结果，不是本次运行事实。 |
| L189 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;question&quot;: &quot;你好，我想退款&quot;,</code> | 数据字段 <code>question</code>；它是材料/历史结果，不是本次运行事实。 |
| L190 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;response&quot;: &quot;您好！请问您希望为哪一笔订单申请退款呢？我可以帮您查询和处理相关事宜。&quot;,</code> | 数据字段 <code>response</code>；它是材料/历史结果，不是本次运行事实。 |
| L191 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;agent_type&quot;: &quot;general&quot;,</code> | 数据字段 <code>agent_type</code>；它是材料/历史结果，不是本次运行事实。 |
| L192 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;intent&quot;: &quot;request&quot;,</code> | 数据字段 <code>intent</code>；它是材料/历史结果，不是本次运行事实。 |
| L193 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;turn&quot;: 0,</code> | 数据字段 <code>turn</code>；它是材料/历史结果，不是本次运行事实。 |
| L194 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;conv_id&quot;: &quot;eval_4&quot;,</code> | 数据字段 <code>conv_id</code>；它是材料/历史结果，不是本次运行事实。 |
| L195 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;judge_failed&quot;: false,</code> | 数据字段 <code>judge_failed</code>；它是材料/历史结果，不是本次运行事实。 |
| L196 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;judge_error&quot;: null</code> | 数据字段 <code>judge_error</code>；它是材料/历史结果，不是本次运行事实。 |
| L197 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | JSON 结构边界。 |
| L198 | <code>&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L199 | <code>&nbsp;&nbsp;&nbsp;&nbsp;{</code> | JSON 结构边界。 |
| L200 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;test_id&quot;: &quot;dialog_4_turn_1&quot;,</code> | 数据字段 <code>test_id</code>；它是材料/历史结果，不是本次运行事实。 |

### L201 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L201 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;passed&quot;: true,</code> | 数据字段 <code>passed</code>；它是材料/历史结果，不是本次运行事实。 |
| L202 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;scores&quot;: {</code> | 数据字段 <code>scores</code>；它是材料/历史结果，不是本次运行事实。 |
| L203 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;relevance&quot;: 1.0,</code> | 数据字段 <code>relevance</code>；它是材料/历史结果，不是本次运行事实。 |
| L204 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;accuracy&quot;: 1.0,</code> | 数据字段 <code>accuracy</code>；它是材料/历史结果，不是本次运行事实。 |
| L205 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;completeness&quot;: 0.8,</code> | 数据字段 <code>completeness</code>；它是材料/历史结果，不是本次运行事实。 |
| L206 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;helpfulness&quot;: 0.9,</code> | 数据字段 <code>helpfulness</code>；它是材料/历史结果，不是本次运行事实。 |
| L207 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;overall&quot;: 0.925</code> | 数据字段 <code>overall</code>；它是材料/历史结果，不是本次运行事实。 |
| L208 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L209 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;detail&quot;: &quot;Q: 订单号是 #12345... → 综合评分 0.925&quot;,</code> | 数据字段 <code>detail</code>；它是材料/历史结果，不是本次运行事实。 |
| L210 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;metadata&quot;: {</code> | 数据字段 <code>metadata</code>；它是材料/历史结果，不是本次运行事实。 |
| L211 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;question&quot;: &quot;订单号是 #12345&quot;,</code> | 数据字段 <code>question</code>；它是材料/历史结果，不是本次运行事实。 |
| L212 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;response&quot;: &quot;好的，我已找到订单 #12345。请问您希望申请退款的原因是什么呢？我可以先帮您确认退款政策。&quot;,</code> | 数据字段 <code>response</code>；它是材料/历史结果，不是本次运行事实。 |
| L213 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;agent_type&quot;: &quot;general&quot;,</code> | 数据字段 <code>agent_type</code>；它是材料/历史结果，不是本次运行事实。 |
| L214 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;intent&quot;: &quot;request&quot;,</code> | 数据字段 <code>intent</code>；它是材料/历史结果，不是本次运行事实。 |
| L215 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;turn&quot;: 1,</code> | 数据字段 <code>turn</code>；它是材料/历史结果，不是本次运行事实。 |
| L216 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;conv_id&quot;: &quot;eval_4&quot;,</code> | 数据字段 <code>conv_id</code>；它是材料/历史结果，不是本次运行事实。 |
| L217 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;judge_failed&quot;: false,</code> | 数据字段 <code>judge_failed</code>；它是材料/历史结果，不是本次运行事实。 |
| L218 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;judge_error&quot;: null</code> | 数据字段 <code>judge_error</code>；它是材料/历史结果，不是本次运行事实。 |
| L219 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | JSON 结构边界。 |
| L220 | <code>&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L221 | <code>&nbsp;&nbsp;&nbsp;&nbsp;{</code> | JSON 结构边界。 |
| L222 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;test_id&quot;: &quot;dialog_4_turn_2&quot;,</code> | 数据字段 <code>test_id</code>；它是材料/历史结果，不是本次运行事实。 |
| L223 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;passed&quot;: true,</code> | 数据字段 <code>passed</code>；它是材料/历史结果，不是本次运行事实。 |
| L224 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;scores&quot;: {</code> | 数据字段 <code>scores</code>；它是材料/历史结果，不是本次运行事实。 |
| L225 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;relevance&quot;: 1.0,</code> | 数据字段 <code>relevance</code>；它是材料/历史结果，不是本次运行事实。 |
| L226 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;accuracy&quot;: 0.9,</code> | 数据字段 <code>accuracy</code>；它是材料/历史结果，不是本次运行事实。 |
| L227 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;completeness&quot;: 0.8,</code> | 数据字段 <code>completeness</code>；它是材料/历史结果，不是本次运行事实。 |
| L228 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;helpfulness&quot;: 0.9,</code> | 数据字段 <code>helpfulness</code>；它是材料/历史结果，不是本次运行事实。 |
| L229 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;overall&quot;: 0.9</code> | 数据字段 <code>overall</code>；它是材料/历史结果，不是本次运行事实。 |
| L230 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;},</code> | JSON 结构边界。 |
| L231 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;detail&quot;: &quot;Q: 退款多久能到账？... → 综合评分 0.900&quot;,</code> | 数据字段 <code>detail</code>；它是材料/历史结果，不是本次运行事实。 |
| L232 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;metadata&quot;: {</code> | 数据字段 <code>metadata</code>；它是材料/历史结果，不是本次运行事实。 |
| L233 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;question&quot;: &quot;退款多久能到账？&quot;,</code> | 数据字段 <code>question</code>；它是材料/历史结果，不是本次运行事实。 |
| L234 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;response&quot;: &quot;通常退款会在您提交申请后的 **3-7个工作日** 内到账，具体时间取决于您的支付方式和银行处理速度。如果您有紧急情况，可以尝试联系支付平台加速处理。&quot;,</code> | 数据字段 <code>response</code>；它是材料/历史结果，不是本次运行事实。 |
| L235 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;agent_type&quot;: &quot;general&quot;,</code> | 数据字段 <code>agent_type</code>；它是材料/历史结果，不是本次运行事实。 |
| L236 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;intent&quot;: &quot;query&quot;,</code> | 数据字段 <code>intent</code>；它是材料/历史结果，不是本次运行事实。 |
| L237 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;turn&quot;: 2,</code> | 数据字段 <code>turn</code>；它是材料/历史结果，不是本次运行事实。 |
| L238 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;conv_id&quot;: &quot;eval_4&quot;,</code> | 数据字段 <code>conv_id</code>；它是材料/历史结果，不是本次运行事实。 |
| L239 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;judge_failed&quot;: false,</code> | 数据字段 <code>judge_failed</code>；它是材料/历史结果，不是本次运行事实。 |
| L240 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&quot;judge_error&quot;: null</code> | 数据字段 <code>judge_error</code>；它是材料/历史结果，不是本次运行事实。 |

### L241 起 · 文本/配置片段

| 原行 | 源码 / 原文 | 解释 |
|---:|---|---|
| L241 | <code>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;}</code> | JSON 结构边界。 |
| L242 | <code>&nbsp;&nbsp;&nbsp;&nbsp;}</code> | JSON 结构边界。 |
| L243 | <code>&nbsp;&nbsp;]</code> | JSON 结构边界。 |
| L244 | <code>}</code> | JSON 结构边界。 |

## 结合全项目：设计缺口与增强方向

- 文件记录 2026-05-31 的历史结果，非本次重新运行结果；该快照内意图样本为8条，当前 DEFAULT_INTENT_CASES 为11条且细化标签。
- pass_rate=1.0 是8个报告项通过，不能当成真实用户请求全量100%准确率。
- 缺少模型、prompt、数据集、代码版本等实验元数据，不足以支撑严格跨版本回归结论。

**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。
