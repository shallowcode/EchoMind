"""离线核对文档与关键行为。不调用 LLM/Redis/Chroma，不运行部署脚本。

从原文件 AST 去掉顶层 import，用标准库环境执行类定义；仅调用选定的纯逻辑方法。
压缩复现使用内存 Redis/LLM 替身，执行的是源码原方法。通过表示解释被支持，不表示 bug 已修复。
"""
import ast
import asyncio
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import hashlib
import html
import json
import logging
from pathlib import Path
import re
import statistics
import sys
import time
import types
import typing
import uuid
from urllib.parse import unquote

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'项目解读与面试指南'
checks=[]
def check(name, condition, detail):
    assert condition, name+': '+detail
    checks.append((name,detail))

def load(relative, injected=None):
    tree=ast.parse((ROOT/relative).read_text(encoding='utf-8'))
    tree.body=[x for x in tree.body if not isinstance(x,(ast.Import,ast.ImportFrom))]
    tree.body.insert(0,ast.ImportFrom(module='__future__',names=[ast.alias(name='annotations')],level=0))
    ast.fix_missing_locations(tree)
    mod=types.ModuleType('isolated_'+relative.replace('/','_').replace('.','_'))
    sys.modules[mod.__name__]=mod
    env=mod.__dict__
    env.update(vars(typing))
    env.update(dict(asyncio=asyncio,hashlib=hashlib,json=json,logging=logging,re=re,time=time,
                    dataclass=dataclass,field=field,asdict=asdict,Enum=Enum,datetime=datetime,
                    timedelta=timedelta,Path=Path,defaultdict=defaultdict,deque=deque,statistics=statistics,uuid=uuid))
    env.update(injected or {})
    exec(compile(tree,str(ROOT/relative),'exec'),env)
    return env

coverage=json.loads((OUT/'_maintain/coverage.json').read_text(encoding='utf-8'))
total=0
for item in coverage['files']:
    path=ROOT/item['path']
    if not item['redacted']:
        check('快照 '+item['path'],hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256'],'生成时与验证时源文件哈希一致。')
    page=(OUT/item['doc']).read_text(encoding='utf-8')
    nums=[int(x) for x in re.findall(r'^\| L(\d+) \|',page,re.M)]
    check('行覆盖 '+item['path'],nums==list(range(1,item['lines']+1)),f'{item["lines"]} 行按原序号完整覆盖，无跳号/重号。')
    total+=item['lines']
    check('首尾结构 '+item['path'],'## 输入、输出与流向' in page and '## 结合全项目：设计缺口与增强方向' in page,'具备输入输出与跨文件缺口说明。')

utils=load('core/llm_utils.py')
intent=load('core/intent_recognizer.py',dict(extract_text_content=utils['extract_text_content']))
I=intent['IntentCategory']; U=intent['UrgencyLevel']
orc=load('agents/agent_orchestrator.py',dict(IntentCategory=I,UrgencyLevel=U,extract_text_content=utils['extract_text_content']))
manager=load('mcp/tool_manager.py',dict(extract_text_content=utils['extract_text_content']))
kb=load('mcp/knowledge_base.py')
skill=load('core/skill_loader.py')
memory=load('memory/conversation_memory.py',dict(extract_text_content=utils['extract_text_content']))
monitor=load('monitor/performance_monitor.py')

IR=intent['IntentRecognizer']; ir=IR.__new__(IR); ir._embedding_enabled=True; ir.threshold=.5
O=orc['AgentOrchestrator']; A=orc['AgentType']; R=orc['Request']; o=O.__new__(O)
o._pool={A.GENERAL:[object()], A.TECHNICAL:[object()], A.BILLING:[object()]}

msg='登录一直 401，而且刚才还重复扣款了'
req=R(message=msg,user_id='demo',conv_id='c1',intent=I.TECHNICAL_LOGIN,urgency=U.LOW,entities=ir._extract_entities(msg))
scores=o._domain_scores(req); decision=o._route_decision(req)
check('复合问题不必然并行',not decision.multi_agent and scores[A.TECHNICAL]==1.13 and scores[A.BILLING]==.18,
      f'固定 intent=technical_login：technical={scores[A.TECHNICAL]}，billing={scores[A.BILLING]}，辅助门槛={scores[A.TECHNICAL]*.55:.4f}，仅技术 Agent。')
msg2='无法登录，报错401；重复扣款50元，申请退款并核对支付发票'
req2=R(message=msg2,user_id='demo',conv_id='c1',intent=I.PAYMENT_ISSUE,urgency=U.LOW,entities=ir._extract_entities(msg2))
s2=o._domain_scores(req2); d2=o._route_decision(req2)
# 构造确实满足辅助条件的输入：固定主意图 technical_login，账单关键词与金额使 .6，技术主 1.13 时要求 .6215，仍不够。
# 固定 technical_login 但只一个技术关键词且不提错误码，主 .93，账单 .6 可通过 .5115。
msg3='无法登录，重复扣款50元，申请退款并核对支付发票'
req3=R(message=msg3,user_id='demo',conv_id='c1',intent=I.TECHNICAL_LOGIN,urgency=U.LOW,entities=ir._extract_entities(msg3))
s3=o._domain_scores(req3);d3=o._route_decision(req3)
check('可并行正例',d3.primary_agent==A.TECHNICAL and d3.supporting_agents==[A.BILLING],
      f'固定 technical_login：technical={s3[A.TECHNICAL]}，billing={s3[A.BILLING]}；账单满足 .45 与主分*.55。')
critical=R(message='请立刻协助处理',user_id='demo',conv_id='c1',intent=I.OTHER,urgency=U.CRITICAL,intent_confidence=.2)
check('澄清优先于紧急分支',o._needs_clarification(critical),'OTHER/.2/长度>2 满足澄清，而 run 中该检查在 CRITICAL 决策之前。')

breaker=manager['CircuitBreaker'](failure_threshold=1,recovery_s=0)
breaker.record_failure()
check('半开并发无单探测限制',breaker.allow() and breaker.allow() and breaker.state==manager['CircuitState'].HALF_OPEN,'连续两次 allow 均为 True，尚未 record_success/failure。')
items=[{'title':'退款政策','content':'同一个片段','score':.8},{'title':'退款政策','content':'同一个片段','score':.7}]
check('去重包含分数',len({hashlib.md5(str(i).encode()).hexdigest() for i in items})==2,'同正文仅 score 不同，MD5(str(item)) 仍保留两条。')
chunks=kb['KnowledgeBase'].__new__(kb['KnowledgeBase'])._chunk_text('甲'*1200,500)
check('切片上限不严格',len(chunks)==1 and len(chunks[0])==1200,'无句号的1200字符文本仍是单片，超过500。')
check('中文逗号解析',skill['SkillManager']._as_list('退款，发票')==['退款，发票'],'中文逗号没有拆成两个关键词。')
irkey1=ir._cache_key('甲'*200+'退款');irkey2=ir._cache_key('甲'*200+'登录')
check('截断缓存冲突',irkey1==irkey2,'前200字符相同、末尾意图不同的消息拥有同一缓存key。')
vote=ir._vote({'intent':I.TECHNICAL,'confidence':.9},{'intent':I.OTHER,'confidence':0},{'intent':I.REFUND,'confidence':.5})
check('跨意图组细化',vote[0]==I.REFUND,'技术粗类得分.63，被退款细类词表改成refund；无组一致性判断。')
es=ir._extract_entities('订单号 AB12345')
check('实体交叉误匹配',es['order_id']==['AB12345'] and es['error_code']==['AB12345'],'AB12345 同时当作订单号和错误码。')
try:
    json.dumps(asdict(monitor['Alert'](monitor['Severity'].ERROR,'m','test',1.,.9)))
except TypeError:
    enum_failure=True
else:enum_failure=False
check('Webhook枚举不可直接JSON编码',enum_failure,'asdict保留普通Enum，json.dumps抛TypeError；没有实际发网络请求。')
check('模型文本块适配',utils['extract_text_content'](['a',{'type':'text','text':'b'},{'type':'tool_use','text':'hidden'}])=='a\nb','字符串和字典文本保留，tool_use不作为文字或工具执行。')

class FakeRedis:
    def __init__(self):self.lists={};self.strings={}
    async def lpush(self,key,value):self.lists.setdefault(key,[]).insert(0,value)
    async def lrange(self,key,start,end):return self.lists.get(key,[])[start:end+1]
    async def expire(self,*a):return True
    async def get(self,key):return self.strings.get(key)
    async def setex(self,key,ttl,value):self.strings[key]=value
    async def delete(self,key):self.lists.pop(key,None)
class FakeMessages:
    async def create(self,**kw):return types.SimpleNamespace(content=['模拟摘要'])

async def reproduce_compression():
    M=memory['MemoryManager']; m=M.__new__(M)
    m._redis=FakeRedis();m._client=types.SimpleNamespace(messages=FakeMessages());m._model='offline'
    async def store(*a):return None
    m._store_episodic=store
    key=m._wm_key('demo','c')
    for i in range(1,16):
        await m._redis.lpush(key,json.dumps(dict(role='user',content=str(i),ts=datetime(2026,1,1).isoformat(),metadata={})))
    before=[x.content for x in await m._get_working_memory('demo','c')]
    await m._compress('demo','c')
    after=[x.content for x in await m._get_working_memory('demo','c')]
    check('原方法压缩顺序复现',before==[str(x) for x in range(1,16)] and after==['15','14','13','12','11'],
          '执行原 _compress/_get_working_memory，内存Redis替身：压缩前1..15，保留区读取成15,14,13,12,11，预期应11..15。')
asyncio.run(reproduce_compression())

# 所有本地 Markdown 链接必须可解析；忽略示例 source code 内的 URL。
broken=[]
for p in OUT.rglob('*.md'):
    text=p.read_text(encoding='utf-8')
    for match in re.finditer(r'(?<!!)\[[^\]\n]*\]\(([^)\n]+)\)',text):
        target=unquote(match.group(1).strip('<>'))
        if target.startswith(('http:','https:','#','codex:')):continue
        if '<code>' in text[max(0,match.start()-60):match.start()]:continue
        local=target.split('#',1)[0]
        resolved=(p.parent/local).resolve()
        if resolved==OUT/'06_验证记录.md':continue  # 本次检查完成后在下方生成
        if not resolved.exists():broken.append(str(p.relative_to(OUT))+': '+target)
check('文档链接有效',not broken,str(broken[:5]) if broken else '所有实际 Markdown 本地导航链接都存在。')

behavior=[c for c in checks if not c[0].startswith(('快照 ','行覆盖 ','首尾结构 '))]
report=['# 验证记录','','输入：当前源码与生成文档；输出：静态覆盖检查和隔离行为复现。没有发模型请求、连接数据库、启动容器或覆盖原评测基线。','',
        f'本次结果：**{len(coverage["files"])} 个原文件、{total} 行完整覆盖，{len(checks)} 项检查通过**。其中源码快照/行覆盖/页首尾属于文档一致性检查，下面是关键行为验证。','',
        '| 验证点 | 观察结果 |','|---|---|']
for name,detail in behavior:report.append('| '+name+' | '+detail.replace('|','\\|')+' |')
report+=['','## 如何复验','','```powershell','python 项目解读与面试指南/_maintain/build_docs.py','python 项目解读与面试指南/_maintain/verify.py','```','',
         '维护脚本在本文件夹内；build_docs 根据人工导读与 AST 生成逐行页，verify 根据 coverage.json 检查哈希/行号并复现选定函数。修改源码后应先更新人工分析，再重新生成。','',
         '## 能证明和不能证明什么','','这些检查支持所写的分支、阈值和边界问题，**通过不是修复了原项目，也不是整套服务测试通过**。未验证真实模型输出、凭据有效性、Redis/Chroma 连接、实际镜像构建、生产性能、费用或公开认证。',
         '复现固定了输入意图以隔离路由公式；真实 LLM 可能返回不同意图，应另用完整 HTTP 链路验证。数据库协议与模型 SDK 在隔离环境中未加载。','']
(OUT/'06_验证记录.md').write_text('\n'.join(report),encoding='utf-8')
print(json.dumps(dict(checks=len(checks),behavior_checks=len(behavior),source_files=len(coverage['files']),source_lines=total),ensure_ascii=False))
