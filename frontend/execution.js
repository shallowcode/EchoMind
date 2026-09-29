function renderExecution(execution) {
  const panel=node('details','execution');
  const summary=node('summary');
  const label=node('span','execution-label','执行过程');
  const duration=Number.isFinite(execution.duration_ms)?`${(execution.duration_ms/1000).toFixed(1)} 秒`:'';
  summary.append(icon('spark'),label,node('span','execution-meta',duration),node('span','execution-chevron','⌄'));
  panel.append(summary);
  const content=node('div','execution-content');
  const agents={billing:'账单助手',technical:'技术助手',general:'通用助手',escalation:'人工接管'};
  const intents={refund:'退款',order_status:'订单查询',technical:'技术支持',billing:'账单',general:'一般咨询',human_handoff:'转人工',invoice:'发票'};
  const states={awaiting_input:'待补充信息',completed:'完成',denied:'业务拒绝',blocked:'未完成',pending:'待执行',failed:'失败',partial:'部分完成',degraded:'降级'};
  function step(title,detail,status='completed') {
    const row=node('div','execution-step '+status);
    row.append(node('span','step-dot',status==='failed'||status==='blocked'?'!':'✓'));
    const text=node('div','step-text');text.append(node('strong','',title));
    if(detail)text.append(node('p','',detail));row.append(text);content.append(row);return text;
  }
  for(const event of execution.steps||[]) {
    if(event.title==='生成答复') {
      const tools=execution.tools||[];
      const toolSection=step('执行工具',tools.length?`${tools.length} 次调用`:'本轮未调用工具',tools.some(tool=>!tool.success)?'failed':'completed');
      for(const tool of tools) {
        const item=node('details','tool-detail');const heading=node('summary');
        heading.append(node('span','',tool.title),node('span',tool.success?'tool-ok':'tool-failed',tool.success?(tool.cached?'复用结果':'成功'):'失败'));
        item.append(heading,node('p','',tool.detail));
        item.append(node('small','',`${tool.name} · ${tool.agent} · ${tool.duration_ms} ms`));
        if(tool.shared)item.append(node('p','','本请求内共享结果'));
        for(const [title,value] of [['工具输入',tool.arguments],['工具结果',tool.result],['执行约束',tool.controls],['错误',tool.error]])if(value){const raw=node('details','context-detail');raw.append(node('summary','',title),node('pre','context-value',typeof value==='string'?value:JSON.stringify(value,null,2)));item.append(raw);}
        if(tool.queries?.length){item.append(node('p','tool-subtitle','检索词'));for(const query of tool.queries)item.append(node('p','tool-query',query));}
        if(tool.backend)item.append(node('p','',`${tool.backend==='chroma'?'向量检索':'词法检索'} · ${tool.reranked?'已重排':'未重排'}`));
        if(tool.degraded?.length)item.append(node('p','tool-failed','部分检索环节已降级'));
        toolSection.append(item);
      }
    }
    let detail=event.detail;
    if(event.title==='识别意图')detail=intents[detail]||detail;
    if(event.title==='分派任务')detail=(execution.tasks||[]).map(task=>`${task.title} → ${task.agent}`).join('；');
    const entry=step(event.title,detail,event.status);
    if(event.title==='分派任务')for(const task of execution.tasks||[])entry.append(node('small','task-state',`${task.title} · ${states[task.status]||task.status} · ${task.attempts} 轮`));
  }
  if(execution.schema_version>=2) {
    const inspect=node('div','context-inspector');
    function section(parent,title,value){const item=node('details','context-detail');item.append(node('summary','',title));if(value!==undefined)item.append(node('pre','context-value',typeof value==='string'?value:JSON.stringify(value,null,2)));parent.append(item);return item;}
    if(execution.tasks?.some(task=>task.input)){
      const tasks=section(inspect,`任务编排 · ${execution.tasks.length} 项`);
      const end=Math.max(...execution.tasks.map(t=>(t.started_ms||0)+(t.duration_ms||0)),1);
      for(const task of execution.tasks){
        const item=section(tasks,`${task.title} · ${task.agent} · ${states[task.status]||task.status}`);
        const line=node('div','task-timeline');const bar=node('span');bar.style.marginLeft=`${task.started_ms/end*100}%`;bar.style.width=`${Math.max(1,task.duration_ms/end*100)}%`;line.append(bar);item.append(line,node('small','task-time',`开始 ${(task.started_ms/1000).toFixed(2)} s · 耗时 ${(task.duration_ms/1000).toFixed(2)} s · ${task.attempts} 轮`));
        section(item,'隔离后的输入',task.input);section(item,'职责与工具要求',{instruction:task.instruction,required_tools:task.required_tools});
        section(item,'工具证据',task.observations);section(item,`重试与补做 · ${(task.repairs||[]).length} 次`,task.repairs?.length?task.repairs:'本项未触发重试或补做');
        section(item,'处理结果',{answer:task.answer,missing:task.missing});
      }
      section(tasks,'执行预算',execution.limits);
    }
    const memory=section(inspect,'记忆');
    const snapshot=execution.memory||{};
    if(!Object.keys(snapshot).length)memory.append(node('p','context-empty','本轮没有记忆记录'));
    else {
      section(memory,`历史消息 · ${(snapshot.history||[]).length} 条`,snapshot.history||[]);
      section(memory,`最近上下文 · ${(snapshot.recent||[]).length} 条`,snapshot.recent||[]);
      section(memory,'会话摘要',snapshot.summary||'无');
      section(memory,'用户偏好',snapshot.profile||{});
      section(memory,`召回记忆 · ${(snapshot.recall||[]).length} 条`,snapshot.recall||[]);
      section(memory,'识别的实体',snapshot.entities||{});
      section(memory,'订单与退款上下文',{order_reference:snapshot.order_reference||{},refund_context:snapshot.refund_context||{}});
    }
    const knowledge=section(inspect,`知识库 · ${(execution.knowledge||[]).length} 次检索`);
    if(!execution.knowledge?.length)knowledge.append(node('p','context-empty','本轮未检索知识库'));
    for(const [index,lookup] of (execution.knowledge||[]).entries()){
      const retrieval=section(knowledge,`${index+1}. ${lookup.query}${lookup.cached?' · 复用结果':''}`);
      section(retrieval,'检索信息',{queries:lookup.result?.queries||[],backend:lookup.result?.backend,reranked:lookup.result?.rerank_applied,success:lookup.success,error:lookup.error});
      if(lookup.result?.branches){const branches=section(retrieval,`并行召回 · ${lookup.result.branches.length} 路`);for(const b of lookup.result.branches)section(branches,`${b.query} · ${b.duration_ms} ms`,b);section(retrieval,'重排前候选',lookup.result.candidates);}
      for(const source of lookup.result?.items||[]){const doc=section(retrieval,source.title||source.id,source.content||'');section(doc,'资料信息',{id:source.id,version:source.version,distance:source.distance,lexical_score:source.lexical_score});}
    }
    if(execution.skills){const skills=section(inspect,`Skills 注入 · ${execution.skills.length} 次`);for(const skill of execution.skills){const s=section(skills,`${agents[skill.agent]||skill.agent} · ${skill.task_id||''}`,skill.prompt||'未命中 Skill');section(s,'内容版本',skill.version);}}
    const calls=execution.model_inputs||[];
    const inputs=section(inspect,`最终送给模型的输入 · ${calls.length} 次`);
    if(!calls.length)inputs.append(node('p','context-empty','本轮未记录模型请求'));
    const purposes={billing:'账单助手',general:'通用助手',technical:'技术助手'};
    for(const call of calls){
      const purpose=(call.purpose||'模型调用').replace(/^(billing|general|technical)/,key=>purposes[key]);
      const item=section(inputs,`${call.index}. ${purpose}${call.status==='failed'?' · 失败':''}`);
      const request=call.request||{};
      if(request.system)section(item,'system',request.system);
      for(const [index,message] of (request.messages||[]).entries())section(item,`${index+1}. ${message.role}`,typeof message.content==='string'?message.content:message);
      const parameters={...request};delete parameters.messages;delete parameters.system;
      section(item,'调用参数',parameters);
      section(item,'完整请求 JSON',request);
    }
    content.append(inspect);
  } else if(execution.sources?.length) {
    const sources=node('div','execution-sources');sources.append(node('strong','','检索资料'));
    for(const source of execution.sources){const item=node('details','source-item');item.append(node('summary','',source.title),node('p','',source.content),node('code','',source.id));sources.append(item);}
    content.append(sources);
  }
  if(execution.failures?.length)content.append(node('p','execution-warning','存在失败或降级环节，详见任务与调用状态。'));
  content.append(node('div','execution-footer',`${execution.model} · ${execution.model_calls} 次模型调用 · ${states[execution.status]||execution.status}`));
  panel.append(content);return panel;
}
