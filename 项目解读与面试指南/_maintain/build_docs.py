"""仅生成解读文档：输入当前项目文本与人工导读，输出逐文件页、配置消费表和覆盖清单。

运行：python 项目解读与面试指南/_maintain/build_docs.py
不导入业务模块，不执行 shell 示例，不联网；.env 的值永不输出。
"""
import ast
import hashlib
import html
import json
import os
import re
from pathlib import Path
from urllib.parse import quote
import sys
sys.dont_write_bytecode = True
from content import FILES
import support  # 注册其余人工导读

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / '项目解读与面试指南'
PAGES = OUT / '逐文件'
PAGES.mkdir(exist_ok=True)

def link(path, label=None):
    return '[' + (label or path) + '](' + quote(path.replace('\\', '/'), safe='/.:#-') + ')'

def code(value):
    escaped=html.escape(str(value)).replace('|', '&#124;')
    escaped=re.sub(r'^ +',lambda m:'&nbsp;'*len(m.group()),escaped)
    return '<code>' + escaped + '</code>'

def shorten(text, n=135):
    return text if len(text) <= n else text[:n] + '…'

def text_of(node):
    return shorten(ast.unparse(node).replace('\n', ' '))

NAMES = {
 'req':'当前请求', 'message':'本轮用户消息', 'history':'历史消息', 'context':'背景上下文',
 'intent':'意图标签', 'intent_group':'粗意图组', 'urgency':'紧急程度', 'confidence':'置信度分数',
 'entities':'结构化实体', 'conv_id':'会话标识', 'user_id':'用户标识', 'max_tokens':'模型最多输出 token 数',
 'temperature':'生成采样温度', 'model':'模型名称', 'messages':'模型消息序列/当前函数的消息列表',
 'system':'模型系统指令', 'api_key':'模型服务凭据', 'base_url':'模型服务地址',
 'success':'执行成功标记', 'latency_ms':'当前计时范围的毫秒耗时', 'primary_agent':'计划主 Agent',
 'supporting_agents':'计划辅助 Agent 列表', 'agent_type':'Agent 类别', 'routing_reason':'可解释路由文字',
 'routing_confidence':'裁剪后的领域分数', 'reranked':'重排标记', 'cached':'缓存命中标记',
 'top_k':'最终返回条数', 'query':'本次检索文本', 'score':'展示分数', 'content':'文本正文',
 'title':'展示标题', 'metadata':'附加元信息', 'metadatas':'每个文档的元信息列表',
 'documents':'送入存储的文本列表', 'query_texts':'要向量化检索的文本列表', 'where':'存储查询过滤条件',
 'ids':'文档标识列表', 'n_results':'请求召回数量', 'enabled':'是否启用', 'keywords':'子串触发词',
 'agents':'允许匹配的 Agent 类型', 'timeout':'等待超时上限', 'return_exceptions':'是否把异常作为结果保留',
}

CALLS = {
 'str':'转换为字符串表示', 'float':'转换为浮点数；无效输入会抛出异常',
 'int':'转换为整数', 'bool':'求真值', 'list':'将迭代内容物化成列表',
 'dict':'构造字典', 'set':'构造去重集合', 'sum':'累加各项数值/布尔命中值',
 'any':'至少一项为真就返回True，并可提前结束迭代',
 'getattr':'读取对象指定属性，不存在时返回这里给出的默认值',
 'print':'向终端输出文本', 'logging.getLogger':'获得当前模块的日志记录器',
 'logging.basicConfig':'设置日志等级和显示格式',
 'load_dotenv':'加载.env配置到进程环境；已有环境变量通常保持优先',
 'sys.path.insert':'在模块搜索路径前方插入项目根目录，使内部模块可被找到',
 'uuid.uuid4':'生成随机UUID作为请求/会话标识来源',
 'datetime.now':'记录当前进程本地时间',
 'asyncio.create_task':'将协程安排为后台任务，当前行不等待业务完成',
 'asyncio.gather':'并发等待这批任务，结果顺序与输入任务顺序一致',
 'asyncio.to_thread':'把同步函数交给线程池，避免同步 I/O 占住事件循环',
 'asyncio.wait_for':'为被包装协程设置等待时间上限',
 'time.monotonic':'读取单调时钟，用来算耗时/过期，不作为日历时间',
 'json.loads':'将模型/存储返回的 JSON 文本解析成 Python 值，格式不合法会抛异常',
 'json.dumps':'把对象序列化为 JSON 文本供存储、提示词或缓存 key 使用',
 'extract_text_content':'进入共享响应适配器，只保留模型文本块',
 'hashlib.md5':'产生稳定摘要用于查找/去重/标识，不是密码安全保证',
 'os.getenv':'读取进程环境配置，缺失时采用这里写的默认值',
 'isinstance':'判断运行时类型，决定兼容/过滤分支',
 'len':'计算当前容器或字符串长度', 'range':'生成循环索引',
 'enumerate':'遍历时同时获得序号和值', 'zip':'按位置配对多份列表，长度不同以最短者结束',
 'max':'取当前候选中的最大值', 'min':'取上界/限制后的较小值',
 'sorted':'按指定规则排序，不直接改变原列表', 'round':'四舍五入用于返回/展示',
 're.findall':'按正则寻找所有匹配，抽取对应字段',
 'statistics.mean':'计算算术平均', 'statistics.stdev':'计算样本标准差',
}

def explain_expr(n):
    if isinstance(n, ast.Await):
        return '等待完成后继续；' + explain_expr(n.value)
    if isinstance(n, ast.Call):
        func = ast.unparse(n.func)
        if func in CALLS:
            return CALLS[func]
        if func.endswith('.messages.create'):
            return '调用外部 LLM 的 messages.create，参数规定模型、提示词与输出预算'
        if func.endswith(('.warning','.error','.info','.debug')):
            return '输出诊断日志，供排障观察；日志不等于已完成提示中描述的改进'
        if '._redis.' in func:
            method = func.rsplit('.',1)[1]
            return {'lpush':'向 Redis 列表头写消息', 'lrange':'读取 Redis 指定索引范围',
                    'get':'读取 Redis 字符串', 'expire':'刷新 Redis 键过期时间',
                    'setex':'写 Redis 字符串并设置 TTL', 'llen':'读取 Redis 列表长度',
                    'delete':'删除 Redis 键', 'aclose':'释放 Redis 异步连接'}.get(method, '调用 Redis '+method)
        for suffix, desc in [('.append','追加一个元素到当前列表'),('.extend','追加一批元素到列表'),
                             ('.pop','移除并取出键/元素'),('.get','按键取值，缺失用给定默认值'),
                             ('.items','遍历字典键值对'),('.values','遍历字典的值'),
                             ('.join','把字符串片段按分隔符合并'),('.split','按分隔符切分字符串'),
                             ('.strip','去除两端指定字符或空白'),('.lower','转小写进行大小写无关比较'),
                             ('.add','向集合/存储添加数据，具体目标见左侧接收者'),
                             ('.write_text','把文本写入文件，覆盖已有内容'),('.read_text','从文件读取文本')]:
            if func.endswith(suffix): return desc
        tail=func.rsplit('.',1)[-1]
        meanings=[]
        for meta in FILES.values():
            for key,meaning in meta['methods'].items():
                if key.rsplit('.',1)[-1]==tail and meaning not in meanings:meanings.append(meaning)
        if len(meanings)==1:
            return '进入 '+code(func)+'：'+shorten(meanings[0].split('。')[0],160)
        return '调用 ' + code(func) + '；实参见源码，函数职责见本页导读或对应模块'
    if isinstance(n, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
        return '按 for/in 与 if 条件遍历、转换或过滤输入，构造新集合/迭代器'
    if isinstance(n, ast.IfExp):
        return '条件 ' + code(text_of(n.test)) + ' 成立选前值，否则选 else 后值'
    if isinstance(n, ast.Constant):
        return '使用这里写明的固定值' if not isinstance(n.value,str) else '使用固定文本/配置值'
    if isinstance(n, ast.JoinedStr): return '将变量插入模板，构造提示词、标识或可读说明'
    if isinstance(n, ast.Dict): return '组装字段字典，下列各键决定输出/模型请求/存储结构'
    if isinstance(n, (ast.List,ast.Tuple,ast.Set)): return '组装有序值或集合，元素在后续逻辑中消费'
    if isinstance(n, ast.BinOp): return '按此表达式计算 '+code(text_of(n))
    if isinstance(n, ast.Subscript): return '按索引/切片取 '+code(text_of(n))+'，注意是否截掉旧历史或长文本'
    return '读取 '+code(text_of(n))

def analyze(src):
    tree = ast.parse(src)
    starts, owners, strings, docstrings, kwargs, entries = {}, {}, set(), set(), {}, {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value,str):
            if getattr(node,'end_lineno',0)>node.lineno:
                strings.update(range(node.lineno,node.end_lineno+1))
        if isinstance(node,(ast.Module,ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef)) and node.body:
            first=node.body[0]
            if isinstance(first,ast.Expr) and isinstance(first.value,ast.Constant) and isinstance(first.value.value,str):
                docstrings.update(range(first.lineno,first.end_lineno+1))
        if isinstance(node, ast.stmt):
            starts.setdefault(node.lineno,[]).append(node)
            for i in range(node.lineno,node.end_lineno+1):
                old=owners.get(i)
                if old is None or (node.end_lineno-node.lineno)<(old.end_lineno-old.lineno): owners[i]=node
        if isinstance(node,ast.keyword) and node.arg:
            kwargs[node.lineno]=node
        if isinstance(node,ast.Dict):
            for key,val in zip(node.keys,node.values):
                if key is not None and getattr(key,'lineno',None): entries[key.lineno]=(key,val)
    return tree, starts, owners, strings, docstrings, kwargs, entries

def py_note(i, line, info, overrides):
    if i in overrides: return '**关键：**'+overrides[i]
    tree, starts, owners, strings, docstrings, kwargs, entries=info
    s=line.strip()
    if not s:return '空行，分隔逻辑。'
    if i in docstrings:return '说明文字；描述设计意图，实际行为以可执行语句和本页末尾核对为准。'
    if s.startswith('#'):return '源码注释：'+s.lstrip('#').strip()
    if i in strings and i not in starts:return '多行文本的这一行，将作为提示词/帮助内容的一部分；不是 Python 控制流。'
    if s.startswith('@'):return '装饰器 '+code(s)+'；为函数添加路由、属性、静态/类方法或数据类行为。'
    nodes=starts.get(i,[])
    n=nodes[-1] if nodes else None
    if isinstance(n,(ast.Import,ast.ImportFrom)):
        return '导入 '+code(ast.unparse(n))+'；只建立名称依赖，真正业务调用见后文。'
    if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
        return ('定义异步' if isinstance(n,ast.AsyncFunctionDef) else '定义')+'函数 '+code(n.name)+'；输入参数见签名，下方导读解释调用目的。'
    if isinstance(n,ast.ClassDef): return '定义 '+code(n.name)+' 的数据契约/行为；继承与字段见本段。'
    if isinstance(n,(ast.Assign,ast.AnnAssign)):
        targets=n.targets if isinstance(n,ast.Assign) else [n.target]
        label=', '.join(ast.unparse(x) for x in targets)
        if n.value is None:return '声明字段 '+code(label)+' 的类型，赋值由构造方完成。'
        return '将结果保存到 '+code(label)+'：'+explain_expr(n.value)+'。'
    if isinstance(n,ast.AugAssign): return '更新 '+code(ast.unparse(n.target))+'：'+code(ast.unparse(n))+'；此处会改变累计状态。'
    if isinstance(n,ast.If): return '判断 '+code(text_of(n.test))+'；成立才执行下一层，else（若有）处理另一情况。'
    if isinstance(n,(ast.For,ast.AsyncFor)):return '遍历 '+code(text_of(n.iter))+'，本轮元素绑定 '+code(text_of(n.target))+'。'
    if isinstance(n,ast.While):return '条件 '+code(text_of(n.test))+' 保持成立时重复循环。'
    if isinstance(n,ast.Return):return '结束当前函数并返回；'+(explain_expr(n.value) if n.value is not None else '无返回值')+'。'
    if isinstance(n,ast.Raise):return '抛出 '+code(text_of(n.exc))+'；由外层异常处理或 HTTP 框架接收。'
    if isinstance(n,ast.Try):return '进入异常捕获范围，后面的 except 决定失败如何降级。'
    if isinstance(n,ast.Expr):return explain_expr(n.value)+'。'
    if isinstance(n,ast.Delete):return '删除 '+code(ast.unparse(n))+' 对应状态；淘汰/重建逻辑需看外层范围。'
    if isinstance(n,ast.Continue):return '跳过本轮剩余代码，处理下一元素。'
    if isinstance(n,ast.Break):return '结束当前循环，不再处理剩余候选。'
    if isinstance(n,ast.Pass):return '有意不处理；异常分支可能因此丢失错误信号。'
    if isinstance(n,ast.Global):return '后续赋值修改模块级组件引用，使 HTTP 路由能共享初始化结果。'
    if isinstance(n,(ast.With,ast.AsyncWith)):return '在上下文管理器生命周期内使用资源，退出时清理。'
    if i in kwargs:
        k=kwargs[i]; return '参数 '+code(k.arg)+'（'+NAMES.get(k.arg,k.arg)+'）：'+explain_expr(k.value)+'。'
    if i in entries:
        k,v=entries[i]; key=k.value if isinstance(k,ast.Constant) else ast.unparse(k)
        return '字段 '+code(key)+'（'+NAMES.get(str(key),'当前映射中的键')+'）：'+explain_expr(v)+'。'
    if s.startswith('except'):return '捕获此类异常并进入恢复/错误记录分支。'
    if s.startswith('else'):return '前一条件不成立时走这里。'
    if s.startswith('finally'):return '离开 try 时执行收尾，包括发生异常的情况。'
    if re.fullmatch(r'[\]\[(){},:]+',s):return '结束/连接多行结构；本行没有独立业务动作。'
    owner=owners.get(i)
    if isinstance(owner,(ast.FunctionDef,ast.AsyncFunctionDef)) and i < min([x.lineno for x in owner.body] or [i]):
        return '函数参数/返回类型签名续行；默认值决定调用方可省略什么。'
    return '续接 L'+str(owner.lineno if owner else i)+' 的表达式：'+('构造文本/参数值。' if s.startswith(('"',"'")) else '按前述语句组装参数、条件或集合。')

def nonpy_note(path, i, line, overrides, fenced=False):
    if i in overrides:return '**关键：**'+overrides[i]
    s=line.strip()
    if not s:return '空行/展示分隔。'
    if path.startswith('.env'):
        if s.startswith('#'):return '配置说明；不被运行时当作赋值。'
        if '=' in s:
            key=s.split('=',1)[0]
            hits=ENV.get(key,[])
            return ('实际消费位置：'+', '.join(x['path']+':'+str(x['line']) for x in hits)) if hits else '未发现 Python os.getenv 消费；另查 Compose 插值。不能因模板列出就认定生效。'
    if path.endswith('.svg'):
        if '<text' in s or '<tspan' in s:return '图上的可见标签；表示架构说明，不建立实际代码调用。'
        if '<path' in s or '<line' in s or '<polyline' in s:return '画连接线/箭头，坐标决定方向；业务调用关系需对照结构地图。'
        if '<rect' in s:return '绘制背景或模块框，几何坐标/圆角/颜色属于展示参数。'
        if '<svg' in s:return '定义 SVG 画布尺寸和坐标系。'
        return 'SVG 样式/分组/图形结构；重复显示细节可略读。'
    if path.endswith('.md'):
        if s.startswith('#'):return '阅读章节：'+s.lstrip('#').strip()+'；本文件为材料或 Skill 文本，不直接执行业务代码。'
        if s.startswith('```'):return '开始/结束示例代码块。'
        if '/SKILL.md' in path:
            if s.startswith(('name:','description:','agents:','keywords:','enabled:')):return 'Skill 配置字段，由 _load_text 解析后参与匹配或展示。'
            return '业务指令/例句：匹配后作为模型 prompt；实际动作是否可做取决于工具与编排实现。'
        if fenced:return '文档中的示例代码/命令；按示例意图阅读，不代表本次已执行或当前结果保证一致。'
        return '原有说明或示例数据；结合本页导读与结尾纠偏阅读。'
    if s.startswith('#'):return '注释/说明：'+s.lstrip('#').strip()
    if path.endswith('.sh'):
        if s.startswith('set '):return '设置 Bash 执行策略；失败退出行为影响后续控制流。'
        if re.match(r'\w+\(\)',s):return '定义 Bash 函数，只有被调用时才执行函数体。'
        if s.startswith(('if ','elif ')):return '判断文件、参数或命令结果，选择后续操作。'
        if s.startswith(('for ','while ')):return '按条件循环消费参数或数据。'
        if s.startswith(('fi','done','esac',';;','}')):return '结束条件/循环/分支/函数结构。'
        if s.startswith(('echo ','print_','cat ')):return '向终端输出帮助或状态，不代表依赖服务真实健康。'
        if s.startswith(('docker ','docker-compose ')):return '调用 Docker 操作：'+code(s)+'；具体副作用须看命令。'
        if s.startswith(('rm ','cp ','mkdir ')):return '文件系统操作：'+code(s)+'；仅解读，未执行。'
        if s.startswith('shift'):return '移动位置参数，决定下一次 $1/$2 代表什么。'
        if s.startswith('eval '):return '对拼接命令做二次 shell 解释，需特别处理空格与引用。'
        if '=' in s:return '设置脚本变量/命令字符串，为后续 Docker 参数构造输入。'
        return 'Bash 分支标签、函数调用或帮助文本；对照所在函数目的阅读。'
    if path=='Dockerfile':
        op=s.split()[0]
        return {'FROM':'开始构建阶段，选择基础镜像/前阶段。','WORKDIR':'设置后续命令工作目录。','ENV':'设置镜像内环境默认值。','RUN':'构建时执行命令，形成镜像层。','COPY':'将上下文或前阶段文件复制入镜像。','USER':'设置后续运行身份。','EXPOSE':'声明容器端口，发布端口仍由 run/Compose 决定。','CMD':'声明容器默认启动命令。','HEALTHCHECK':'配置容器健康探测。'}.get(op,'续接构建指令的参数/命令。')
    if path=='.gitignore':return 'Git 忽略模式；不影响已跟踪文件。'
    if path=='.dockerignore':return 'Docker 上下文过滤模式；! 表示重新包含例外。'
    if path=='requirements.txt':return '安装指定 Python 包版本；职责见本页文件导读。'
    if path.endswith('.json'):
        if re.fullmatch(r'[\[\]{},]+',s):return 'JSON 结构边界。'
        key=re.match(r'"([^\"]+)"\s*:',s)
        return '数据字段 '+code(key.group(1) if key else s)+'；它是材料/历史结果，不是本次运行事实。'
    if path.endswith('.conf'):
        token=s.split()[0].rstrip(';')
        nginx={
          'user':'工作进程身份，控制文件访问权限', 'worker_processes':'工作进程数，auto让Nginx按环境决定',
          'worker_connections':'每个工作进程连接数上限', 'events':'事件处理配置块', 'http':'HTTP配置范围',
          'use':'选择事件通知机制，此处epoll对应Linux', 'multi_accept':'一次事件尽量接受多条新连接',
          'error_log':'错误日志路径和等级', 'access_log':'访问日志位置或关闭此位置的访问日志',
          'pid':'主进程PID文件位置', 'include':'加载其他配置文件', 'default_type':'无匹配MIME类型时的默认响应类型',
          'log_format':'定义访问日志字段格式', 'sendfile':'使用内核文件发送能力',
          'tcp_nopush':'调整TCP发送，适配文件传输', 'tcp_nodelay':'减少小数据包等待',
          'keepalive_timeout':'客户端空闲长连接保留时间', 'types_hash_max_size':'MIME映射哈希表容量',
          'gzip':'响应压缩总开关', 'gzip_vary':'根据Accept-Encoding区分缓存表示',
          'gzip_proxied':'决定哪些被代理响应可以压缩', 'gzip_comp_level':'压缩等级与CPU成本取舍',
          'gzip_types':'启用压缩的内容类型列表', 'upstream':'命名一组后端服务供proxy_pass引用',
          'least_conn':'选择当前连接少的上游；现配置只有一个候选',
          'server':'上游块内为后端地址，http块内则开始虚拟主机配置',
          'keepalive':'上游连接池缓存的空闲连接数量', 'limit_req_zone':'声明按键统计的请求速率共享区',
          'limit_conn_zone':'声明并发连接统计共享区', 'listen':'监听端口', 'server_name':'虚拟主机名称匹配',
          'add_header':'给响应添加指定头；always使错误响应也可带该头',
          'location':'按URL路径匹配本配置块', 'limit_req':'对匹配请求应用速率区域及突发策略',
          'limit_conn':'对指定统计区域限制并发连接', 'proxy_pass':'把请求转发到命名后端或URL',
          'proxy_http_version':'访问上游时使用的HTTP版本', 'proxy_set_header':'向上游传递指定请求头',
          'proxy_connect_timeout':'建立上游连接的等待上限', 'proxy_send_timeout':'向上游发送请求的等待上限',
          'proxy_read_timeout':'等待上游读取响应数据的超时', 'proxy_buffering':'是否先缓冲上游响应',
          'proxy_buffer_size':'读取响应初始数据的缓冲大小', 'proxy_buffers':'响应缓冲数量与单块大小',
          'proxy_busy_buffers_size':'忙碌响应缓冲区大小限制', 'allow':'允许来源地址/网段', 'deny':'拒绝指定来源',
          'alias':'将URL前缀映射到文件系统目录', 'expires':'设置静态缓存过期时间', 'client_max_body_size':'请求体大小上限'}
        if token in nginx:return nginx[token]+'；具体取值见原行。'
        return 'Nginx多行参数或配置块边界，继承当前块的语义。'
    token=s.lstrip('- ').split(':',1)[0]
    yaml={
      'services':'开始定义Compose服务集合', 'image':'从镜像名与标签选择容器内容',
      'container_name':'固定容器名称，运维脚本也依赖此名字', 'ports':'发布宿主端口到容器端口',
      'command':'覆盖镜像默认启动命令', 'volumes':'定义挂载；根级同名键声明命名卷',
      'restart':'容器退出后的重启策略', 'networks':'指定服务所属网络；根级声明网络',
      'healthcheck':'定义依赖可用性探测', 'test':'健康检查执行的命令',
      'interval':'健康检查周期', 'timeout':'单次检查超时', 'retries':'连续失败次数阈值',
      'start_period':'启动宽限期', 'environment':'注入变量，应用同名值覆盖env_file',
      'build':'声明本地构建参数', 'context':'Docker构建上下文目录', 'dockerfile':'使用的构建文件',
      'target':'选择Dockerfile构建阶段', 'env_file':'将此环境文件载入容器',
      'depends_on':'声明启动依赖关系', 'condition':'等待依赖满足指定条件',
      'driver':'网络驱动', 'ipam':'容器地址分配配置', 'subnet':'网络地址范围',
      'global':'Prometheus全局抓取默认值', 'scrape_interval':'抓取指标的时间间隔',
      'evaluation_interval':'评估记录/告警规则的周期', 'external_labels':'发送指标时附带的外部标签',
      'rule_files':'待加载的规则文件路径模式', 'scrape_configs':'定义指标抓取任务列表',
      'job_name':'指标任务名称', 'static_configs':'静态配置抓取目标', 'targets':'主机和端口目标列表',
      'labels':'为抓取的时间序列附加标签', 'metrics_path':'HTTP指标路径'}
    return (yaml[token]+'；缩进决定该项属于哪个服务/抓取任务。') if token in yaml else '当前服务/网络/抓取任务的名称、参数值或列表项；向上查最近的配置键确定归属。'

# 只做 AST 检查，不导入业务模块；列出确实被 os.getenv 读取的变量。
ENV={}
for p in sorted(ROOT.glob('*/*.py')):
    for n in ast.walk(ast.parse(p.read_text(encoding='utf-8'))):
        if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute) and ast.unparse(n.func)=='os.getenv' and n.args and isinstance(n.args[0],ast.Constant):
            ENV.setdefault(n.args[0].value,[]).append(dict(path=p.relative_to(ROOT).as_posix(),line=n.lineno,default=ast.unparse(n.args[1]) if len(n.args)>1 else 'None'))

manifest=[]
for path,meta in FILES.items():
    source=ROOT/path
    raw=source.read_text(encoding='utf-8-sig')
    source_lines=raw.splitlines()
    is_secret=path=='.env'
    displayed=source_lines[:]
    if is_secret:
        displayed=[(line.split('=',1)[0]+'=<已脱敏>') if line.strip() and not line.lstrip().startswith('#') and '=' in line else ('# 配置注释（省略，避免复制本机信息）' if line.strip() else '') for line in displayed]
    relout='逐文件/'+path+'.md'
    dest=OUT/relout
    dest.parent.mkdir(parents=True,exist_ok=True)
    back=os.path.relpath(OUT/'README.md',dest.parent).replace('\\','/')
    src_link=os.path.relpath(source,dest.parent).replace('\\','/')
    digest=hashlib.sha256(source.read_bytes()).hexdigest() if not is_secret else None
    parts=[f'# {path} 解读', '', '## 输入、输出与流向', '',
           '**定位：** '+meta['role'], '', '**输入：** '+meta['inputs'], '', '**输出 / 副作用：** '+meta['outputs'], '',
           '**流向：** '+meta['flow'], '', link(back,'返回阅读入口')+' · '+link(src_link,'对照原文件'), '',
           f'当前工作区快照：{len(source_lines)} 行。原始行号列对应原文件；空白和纯注释可略读。'+('实际配置值均已脱敏。' if is_secret else f' SHA-256：`{digest}`。'), '']
    info=analyze(raw) if path.endswith('.py') else None
    symbols={}
    if info:
        def walk_defs(nodes,prefix=''):
            for n in nodes:
                if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)):
                    full=prefix+n.name
                    start=min([n.lineno]+[d.lineno for d in n.decorator_list])
                    meaning=meta['methods'].get(full,meta['methods'].get(n.name))
                    if meaning is None and isinstance(n,ast.ClassDef):
                        meaning=meta['role']+' 下方逐个方法说明该类如何实现职责。'
                    if meaning is None:
                        raise RuntimeError('缺少人工符号解读 '+path+':'+full)
                    symbols[start]=(full,n,meaning)
                    walk_defs(n.body,full+'.' if isinstance(n,ast.ClassDef) else '')
        walk_defs(info[0].body)
        # 文件内数据常量/词表也单独解释。
        parts+=['## 类与函数导航','',' → '.join(link('#symbol-'+str(i),full) for i,(full,n,meaning) in sorted(symbols.items())), '']
    parts+=['## 按原行号阅读', '', '读法：先看每个函数前的因果解释，再看逐行表。多行参数、词表、提示文本续行从属于起始语句；关键行另加粗说明。', '']
    table=False
    fenced=False
    for i,line in enumerate(displayed,1):
        if i in symbols:
            full,n,meaning=symbols[i]
            parts+=['',f'<a id="symbol-{i}"></a>', '',f'### L{i}–L{n.end_lineno} · {full}', '', meaning, '']
            if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):
                args=ast.unparse(n.args)
                returns=ast.unparse(n.returns) if n.returns else '源码未标注；参照 return 和本段解释'
                parts+=['**签名输入：** '+code(args)+'；**返回契约：** '+code(returns)+'。','']
            table=False
        if not info and (i==1 or (path.endswith('.md') and line.startswith('#') and not fenced) or (not path.endswith('.md') and i%40==1)):
            parts+=['',f'### L{i} 起 · '+(line.lstrip('#').strip() if path.endswith('.md') and line.startswith('#') else '文本/配置片段'), ''];table=False
        if not table:
            parts+=['| 原行 | 源码 / 原文 | 解释 |','|---:|---|---|']; table=True
        note=py_note(i,line,info,meta['lines']) if info else nonpy_note(path,i,line,meta['lines'],fenced)
        parts.append(f'| L{i} | {code(line) if line else "（空行）"} | {note.replace(chr(10)," ").replace("|","&#124;")} |')
        if path.endswith('.md') and line.lstrip().startswith('```'):fenced=not fenced
    if not displayed:parts+=['此文件为空，没有需要逐行解释的语句。']
    parts+=['','## 结合全项目：设计缺口与增强方向','']+['- '+g for g in meta['gaps']]
    parts+=['','**面试落点：** 先说本文件接收什么、产出什么，再解释它如何影响下一模块；将以上缺口说成观察到的问题或下一步方案，不说成已经完成的能力。','']
    dest.write_text('\n'.join(parts),encoding='utf-8')
    manifest.append(dict(path=path,doc=relout,lines=len(source_lines),sha256=digest,redacted=is_secret,kind='python' if info else 'text',symbols=len(symbols)))

rows=['# 逐文件覆盖索引','','每个条目都有独立解读页。所有业务 Python、部署脚本、配置、Skills、现存数据样例和展示材料均列入；不依赖 Git 跟踪状态。','',
      '| 原文件 | 行数 | 解读 |','|---|---:|---|']
for m in sorted(manifest,key=lambda x:x['path']):rows.append('| '+code(m['path'])+' | '+str(m['lines'])+' | '+link(m['doc'],'打开')+' |')
rows+=['','## 非源码与明确排除范围','','以下仍列入清单，按用途解释；没有把二进制或第三方依赖伪装成可逐行阅读的业务代码。','',
       '| 路径 | 处理原因 |','|---|---|']
excluded=[]
for p in sorted(ROOT.rglob('*')):
    r=p.relative_to(ROOT).as_posix()
    if r.split('/')[0] in {OUT.name,'.git','.venv'}:continue
    if p.is_file() and r not in FILES:
        if r.startswith('.idea/'):why='IDE 的项目/编辑器/工作区配置，不参与应用请求链路；不复制本机编辑历史。'
        elif '.DS_Store' in r:why='操作系统目录展示元数据。'
        elif r.startswith('data/chroma/'):why='Chroma 持久化 SQLite/HNSW 文件，由存储库管理；不是 Python 源码，未读取用户历史内容。'
        elif '__pycache__' in r or r.endswith('.pyc'):why='Python 生成缓存。'
        else:raise RuntimeError('发现未纳入覆盖的文件：'+r)
        rows.append('| '+code(r)+' | '+why+' |');excluded.append(dict(path=r,reason=why))
for r,why in [('.git/','版本控制对象和日志；原有工作区改动未恢复。'),('.venv/','第三方依赖和虚拟环境，不属于项目自研源码。'),('logs/','当前无业务文本文件；运行日志不是设计保证。'),('tools/','当前空目录，实际工具实现位于 mcp/。'),(OUT.name+'/','本次新建学习资料与维护脚本，不计入原项目覆盖分母。')]:rows.append('| '+code(r)+' | '+why+' |')
(OUT/'00_逐文件索引.md').write_text('\n'.join(rows)+'\n',encoding='utf-8')
(OUT/'_maintain'/'coverage.json').write_text(json.dumps(dict(files=manifest,excluded=excluded),ensure_ascii=False,indent=2),encoding='utf-8')

cfg=['# 配置消费核对','','此表从业务 Python AST 提取真实 os.getenv 调用；只有这里和 Compose/启动器显式消费的键才会生效。未读取真实 .env 的值。','',
     '| 键 | Python 消费位置 | 代码缺省值 |','|---|---|---|']
for key,hits in sorted(ENV.items()):
    cfg.append('| '+code(key)+' | '+'; '.join(code(h['path']+':'+str(h['line'])) for h in hits)+' | '+'; '.join(code(h['default']) for h in hits)+' |')
cfg+=['','## 模板中未见 Python 消费的活跃键','','下列键不一定全部无效：例如 REDIS_PASSWORD 被 Compose 消费；但 JWT、限流、缓存配置等不能因为列在模板中就称已接入。','']
for name in ['.env.example','.env.example.env']:
    keys=[]
    for ln in (ROOT/name).read_text(encoding='utf-8').splitlines():
        if ln and not ln.lstrip().startswith('#') and '=' in ln:
            key=ln.split('=',1)[0].strip()
            if key not in ENV:keys.append(key)
    cfg+=['- '+code(name)+'：'+', '.join(code(k) for k in keys)]
cfg+=['','## 必须能解释的配置冲突','',
 '- Compose 应用覆盖 REDIS_URL，但未覆盖 CHROMA_HOST/CHROMA_PORT；模板 localhost:8001 是宿主访问方式，容器间应显式配置 chromadb:8000。',
 '- 实际监控周期变量是 MONITOR_INTERVAL，长模板写 MONITORING_INTERVAL，二者不同。',
 '- ENABLE_SWAGGER_UI、ENABLE_MONITORING、ENABLE_EVALUATION 未控制对应路由/装配。',
 '- Python API_HOST/API_PORT/APP_ENV 仅在直接启动 api/main.py 的 __main__ 分支使用；Docker CMD 另有固定参数。',
 '- Memory 的 20/15/5 消息限制、24h TTL、意图 .5 阈值、工具30秒与5次熔断等写在代码中，不能靠模板同名配置自动改变。','']
(OUT/'05_配置消费核对.md').write_text('\n'.join(cfg),encoding='utf-8')
print(json.dumps(dict(pages=len(manifest),python_files=sum(m['kind']=='python' for m in manifest),source_lines=sum(m['lines'] for m in manifest),symbols=sum(m['symbols'] for m in manifest)),ensure_ascii=False))
