# 记忆与Skills

[返回总索引](00_使用说明与重点题.md)

<a id="d01"></a>

## D01 · 会话记忆分几层，各自存什么？

**P0 · 代码已核对** | 对应简历：知识与记忆 | 检索词：Memory、会话、SQL、Redis、Chroma

**主回答：** SQL存权威消息、会话状态和画像；Redis是带轮次信息的历史缓存；Chroma保存摘要情景记忆和画像投影。模型上下文由summary、recent、profile、recall组合。

**实现细节 / 展开：** 当前recent取最近8条消息，Store.history默认最多取20条；Chroma跨会话召回按tenant和user过滤，最多3条。订单与退款当前状态仍需查业务工具。

**深入追问：** 为什么不把所有历史直接塞进prompt？

**追问回答：** 上下文会变长、成本增加且旧状态容易误导。近期原文保留细节，摘要压缩较早内容，结构化业务槽位保存订单等关键字段，但这些压缩都可能失真。

**边界 / 易错点：** 这不是无限记忆，也没有证据说明长期召回准确率已达某个数值。

**依据：** [supportflow/service.py:569 · ChatService._run](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/service.py:569>)；[supportflow/service.py:466 · ChatService.chat](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/service.py:466>)；[supportflow/knowledge.py:261 · Knowledge.recall](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/knowledge.py:261>)

**关联：** [D02](04_记忆与Skills.md#d02) · [D05](04_记忆与Skills.md#d05)

---

<a id="d02"></a>

## D02 · Redis 挂了能不能继续聊天？为什么？

**P0 · 代码已核对** | 对应简历：知识与记忆 | 检索词：Redis、权威源、降级、缓存一致性

**主回答：** 能尝试继续，因为SQL是权威会话存储；Redis读写失败被记录到trace，主链路仍可用SQL历史处理，结果可能标为degraded。写缓存发生在SQL提交后。

**实现细节 / 展开：** 读取时当前实现先取SQL历史，再比较Redis的turn和history内容，只有一致才采用缓存。因此此处缓存并没有完全消除SQL读取，更像可核验投影。

**深入追问：** 既然先读SQL，Redis到底带来多大性能收益？

**追问回答：** 需要实测，不能凭“用了Redis”声称显著加速。改进时可设计轻量版本校验和缓存读取路径，同时处理人工工单写回绕过普通聊天轮次的问题。

**边界 / 易错点：** 不要把当前Redis描述成唯一工作记忆，或宣称命中即可完全绕过数据库。

**依据：** [supportflow/service.py:569 · ChatService._run](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/service.py:569>)；[supportflow/service.py:466 · ChatService.chat](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/service.py:466>)

**关联：** [D03](04_记忆与Skills.md#d03) · [I03](09_性能可靠性与部署.md#i03)

---

<a id="d03"></a>

## D03 · 为什么 Redis 不只比较 turn，还比较 history 内容？

**P1 · 代码已核对** | 对应简历：知识与记忆 | 检索词：人工回写、缓存失效、版本

**主回答：** 人工工单解决时会往原会话写入system消息，但这未必同步增加聊天轮次。只比较turn可能接受旧缓存，丢掉客服已经解决问题的说明。

**实现细节 / 展开：** 当前同时比较历史内容，让SQL新增的人工消息优先。更清晰的长期设计是统一会话变更版本，让所有写入路径都推进同一版本。

**深入追问：** 比较内容是不是成本太大？

**追问回答：** 是一个权衡：当前历史窗口小，比较简单，但仍需SQL读。规模变大后应改为轻量版本与可靠失效机制，再验证回写一致性。

**边界 / 易错点：** 统一版本方案是建议；不能把现有多个版本字段说成天然一致。

**依据：** [supportflow/service.py:569 · ChatService._run](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/service.py:569>)；[supportflow/store.py:308 · Store.update_ticket](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/store.py:308>)

**关联：** [D02](04_记忆与Skills.md#d02) · [E14](05_业务工具与权限.md#e14)

---

<a id="d04"></a>

## D04 · 历史摘要什么时候生成，摘要失败怎么办？

**P1 · 代码已核对** | 对应简历：知识与记忆 | 检索词：摘要、触发条件、上下文窗口

**主回答：** 当前条件是历史至少14条且本轮turn模6等于2。摘要输入为旧摘要和history去掉最后6条，模型输出上限256 tokens，最终截到1000字符；失败记录summary并继续。

**实现细节 / 展开：** 这保留最近对话原文、压缩较早信息，但窗口、轮次和字符阈值都是工程设置。history本身有读取上限，不能理解为每次把全部历史重新完整总结。

**深入追问：** 怎么避免摘要把“申请待审核”写成“已到账”？

**追问回答：** 摘要提示要求只总结事实，但高风险状态还必须从当前工具重查。可以保存来源轮次、对结构化状态单独校验，并用跨轮反例测摘要漂移。

**边界 / 易错点：** 摘要不是账本，不能成为支付或退款完成的事实来源。

**依据：** [supportflow/service.py:569 · ChatService._run](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/service.py:569>)；[supportflow/knowledge.py:242 · Knowledge.archive](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/knowledge.py:242>)

**关联：** [D05](04_记忆与Skills.md#d05) · [J03](10_场景推演与个人表达.md#j03)

---

<a id="d05"></a>

## D05 · 用户画像是模型自动理解所有偏好吗？

**P1 · 代码已核对** | 对应简历：知识与记忆 | 检索词：长期记忆、召回、用户画像

**主回答：** 当前画像更新很克制：例如用户明确说“用中文”“简短”时写language和verbosity，SQL按tenant和user保存；Chroma画像是投影，不是完整用户画像建模系统。

**实现细节 / 展开：** 情景记忆召回是按当前用户和租户查询摘要集合，可跨会话找相关历史。近期事实和召回摘要冲突时，应核对原文和当前业务状态。

**深入追问：** 为什么不自动推断用户收入或敏感属性？

**追问回答：** 这些信息并非客服任务必需，推断还可能不准。画像应限定为明确授权、可解释、可纠正且与业务相关的字段。

**边界 / 易错点：** 不能说系统已经实现自动画像抽取、冲突合并和隐私删除全流程。

**依据：** [supportflow/knowledge.py:261 · Knowledge.recall](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/knowledge.py:261>)；[supportflow/knowledge.py:242 · Knowledge.archive](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/knowledge.py:242>)；[supportflow/knowledge.py:272 · Knowledge.project_profile](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/knowledge.py:272>)；[supportflow/service.py:569 · ChatService._run](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/service.py:569>)

**关联：** [D06](04_记忆与Skills.md#d06) · [D07](04_记忆与Skills.md#d07)

---

<a id="d06"></a>

## D06 · 用户依次说“我要退款”“ORD1001”“全退给我”，怎么承接？

**P0 · 代码已核对** | 对应简历：知识与记忆 | 检索词：多轮退款、槽位、授权、承接

**主回答：** 退款解析器维护待补充上下文，保存用户明确提供的订单与退款意图；缺字段时返回awaiting_input。“全退”不让模型计算金额，而是传full_refund，由账本事务计算可退余额。

**实现细节 / 展开：** 切换订单要清除旧金额，取消或切换话题要结束待补充流程。订单来源需追溯用户消息或确定匹配结果，不能拿助手随口生成的订单号作授权。

**深入追问：** 如果上一轮问“可以退款吗”，下一轮只说订单号呢？

**追问回答：** 咨询不应自动变成提交授权。应区分政策咨询、明确申请和待补充申请状态；只有授权和必要字段都满足时才执行写入。

**边界 / 易错点：** 这是当前增强实现；不能把新增多轮能力直接归因到9月9日旧评测成绩。

**依据：** [supportflow/refunds.py:46 · resolve_refund](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/refunds.py:46>)；[supportflow/refunds.py:93 · validate_refund_call](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/refunds.py:93>)；[supportflow/service.py:569 · ChatService._run](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/service.py:569>)

**关联：** [E06](05_业务工具与权限.md#e06) · [J02](10_场景推演与个人表达.md#j02)

---

<a id="d07"></a>

## D07 · 用户说“上次那笔退了吗”，查记忆还是查数据库？

**P1 · 代码已核对** | 对应简历：知识与记忆 | 检索词：退款进度、记忆过期、业务事实

**主回答：** 记忆只用来定位订单或申请，真实进度调用refund_status查当前账本。approved表示批准待执行，settled才表示沙箱退款完成；不能把上次答复作为最新状态。

**实现细节 / 展开：** 如果无法唯一定位订单，应追问或展示候选。询问进度不得顺便再次提交申请，否则把读操作误变成写操作。

**深入追问：** 模型记得已经到账，而账本说待审核，听谁的？

**追问回答：** 以当前经过权限校验的业务记录为准，说明现在查到的状态；必要时标记历史答复错误并提供人工核查路径。

**边界 / 易错点：** 沙箱settled只表示测试账本完成，不代表真实银行资金到账。

**依据：** [supportflow/store.py:143 · Store.refund_status](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/store.py:143>)；[supportflow/service.py:569 · ChatService._run](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/service.py:569>)

**关联：** [D04](04_记忆与Skills.md#d04) · [J05](10_场景推演与个人表达.md#j05)

---

<a id="d08"></a>

## D08 · Skills、RAG 和 Memory 为什么要分开？

**P0 · 代码已核对** | 对应简历：知识与记忆 | 检索词：Skill、RAG、Memory、SOP

**主回答：** RAG回答“规则和知识是什么”，Memory回答“这位用户之前说过什么”，Skill回答“当前角色按什么步骤处理”。例如退款政策、上一轮订单号、先核验再提交的SOP分别属于三者。

**实现细节 / 展开：** 三者在模型上下文中会组合，但业务硬约束由代码实现。更新SOP不应改变数据库可退余额，也不能赋予角色原本没有的支付权限。

**深入追问：** Skill是不是把工具定义换个名字？

**追问回答：** 不是。这里Skill是从文件加载的说明文本；工具是有参数schema、执行代码和权限检查的动作。写出“可以退款”不会自动生成退款实现。

**边界 / 易错点：** 这个Skill加载器是项目内SOP机制，不等于所有Agent平台中的Skills标准。

**依据：** [core/skill_loader.py:122 · SkillManager.prompt_for](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/core/skill_loader.py:122>)；[supportflow/service.py:569 · ChatService._run](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/service.py:569>)；[supportflow/knowledge.py:166 · Knowledge.retrieve](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/knowledge.py:166>)

**关联：** [D09](04_记忆与Skills.md#d09) · [D11](04_记忆与Skills.md#d11)

---

<a id="d09"></a>

## D09 · Skill 如何匹配当前请求，注入有多大预算？

**P1 · 代码已核对** | 对应简历：知识与记忆 | 检索词：Skill匹配、关键词、角色、预算

**主回答：** Skill按enabled、agents和keywords筛选；关键词为空可作为全局Skill。Manager默认总字符预算5000，单块默认3200，当前ToolAgent还把最终Skill文本截到2200字符。

**实现细节 / 展开：** 这些是字符限制，不是token限制。不同角色和关键词命中会得到不同SOP；加载顺序影响预算不足时后面规则能否进入prompt。

**深入追问：** 截断会不会把关键禁止事项截掉？

**追问回答：** 会，因此强制权限必须在代码。可把不可截断的短约束固定在系统层，给SOP设置优先级、token预算和完整块截断，再检查实际注入trace。

**边界 / 易错点：** 不能只报SkillManager的5000而忽略Agent侧2200的实际限制。

**依据：** [core/skill_loader.py:27 · Skill.matches](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/core/skill_loader.py:27>)；[core/skill_loader.py:122 · SkillManager.prompt_for](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/core/skill_loader.py:122>)；[supportflow/service.py:36 · ToolAgent._call_llm](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/service.py:36>)

**关联：** [D10](04_记忆与Skills.md#d10) · [D12](04_记忆与Skills.md#d12)

---

<a id="d10"></a>

## D10 · Skills 热更新具体怎么做，改文件就一定立即生效吗？

**P1 · 代码已核对** | 对应简历：知识与记忆 | 检索词：热更新、Skill加载、错误文件

**主回答：** SkillManager.reload重新扫描受管目录并解析文件；每个文件的错误被收集，其他有效Skill仍可加载。API有受权限约束的重载入口，当前工作台保存也会触发重载。

**实现细节 / 展开：** 单纯编辑文件不等于所有进程自动同步；是否立即生效取决于是否调用重载以及实例范围。已有请求是否读到新内容也与读取时点有关。

**深入追问：** 如果一个关键Skill写坏了，系统会怎样？

**追问回答：** 当前可以跳过坏文件继续加载，这保证部分可用但可能缺关键SOP。更严格的方案是验证整批候选后原子替换，并保留上个可用版本及回滚操作。

**边界 / 易错点：** 完整跨实例发布、回滚和请求快照隔离是改进建议，不应声称已有。

**依据：** [core/skill_loader.py:92 · SkillManager.load](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/core/skill_loader.py:92>)；[supportflow/api.py:89 · create_app](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/api.py:89>)；[tests/test_supportflow_skills.py:1](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/tests/test_supportflow_skills.py:1>)

**关联：** [D11](04_记忆与Skills.md#d11) · [F09](06_事务与一致性.md#f09)

---

<a id="d11"></a>

## D11 · 如何证明一次回答到底用了哪个版本的 Skill？

**P1 · 设计推演** | 对应简历：知识与记忆 | 检索词：热更新一致性、版本、审计

**主回答：** 当前trace记录实际注入的Skill文本及其哈希，服务也能计算Skills目录摘要。相比只记录“当前版本”，保存实际输入更有助于复现该请求。

**实现细节 / 展开：** 但目录哈希与任务实际读取文本不是天然原子快照；热更新与多任务交错时可能看到不同版本。更稳妥是请求开始捕获不可变Skill集合并传给所有任务。

**深入追问：** 有哈希为什么还不能复现？

**追问回答：** 哈希只能核对内容是否一致，不能还原内容；还要保留对应文本、模型和知识版本、请求参数及输出。模型服务本身也可能有非确定性。

**边界 / 易错点：** 不可变请求快照是建议，不应将目录版本号当作完整可复现证明。

**依据：** [core/skill_loader.py:92 · SkillManager.load](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/core/skill_loader.py:92>)；[supportflow/service.py:459 · ChatService.versions](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/service.py:459>)；[supportflow/service.py:36 · ToolAgent._call_llm](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/service.py:36>)

**关联：** [F09](06_事务与一致性.md#f09) · [I06](09_性能可靠性与部署.md#i06)

---

<a id="d12"></a>

## D12 · 长期记忆越来越多，怎么避免旧偏好和错误摘要污染？

**P1 · 设计推演** | 对应简历：知识与记忆 | 检索词：记忆冲突、遗忘、删除、长会话

**主回答：** 先给记忆标来源、时间和版本，结构化业务事实以当前账本为准；对于用户偏好允许明确覆盖，对不确定摘要降低权重，并制定过期和删除策略。

**实现细节 / 展开：** 当前系统有租户和用户过滤、摘要版本与SQL权威状态，但没有完整记忆质量评分、冲突消解、遗忘调度及跨存储删除编排。

**深入追问：** 面试官让你优先做一个改进，你选什么？

**追问回答：** 先补记忆来源和纠错机制，尤其防止把助手旧答复当用户授权；用跨轮换订单、取消退款、偏好改口的用例检验，再考虑更复杂召回算法。

**边界 / 易错点：** 这里是扩展设计，不是现有长对话准确率或隐私治理的成绩。

**依据：** [supportflow/service.py:569 · ChatService._run](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/service.py:569>)；[supportflow/knowledge.py:261 · Knowledge.recall](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/knowledge.py:261>)；[supportflow/store.py:406 · Store.commit_turn](<C:/Users/A0005232/Downloads/EchoMind所有代码+简历1（人已满，不可申请）_____ (1)/EchoMind所有代码+简历/EchoMind/supportflow/store.py:406>)

**关联：** [J03](10_场景推演与个人表达.md#j03) · [I08](09_性能可靠性与部署.md#i08)

---

