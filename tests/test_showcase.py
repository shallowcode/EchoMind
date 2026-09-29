import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

from supportflow.api import create_app
from supportflow.contracts import Settings, Principal
from supportflow.planning import plan_tasks
from supportflow.showcase import evaluation_report
from tests.test_supportflow import ScriptedModel


def test_product_match_keeps_other_compound_tasks():
    tasks = plan_tasks('登录报错401，我买的耳机发货了吗，转人工', {'order_id': ['ORD123']}, 'billing', False,
                       order_reference={'active': True, 'ids': ['ORD123']})
    assert [t.kind for t in tasks] == ['product_order', 'technical', 'handoff']
    ambiguous = plan_tasks('登录报错401，耳机退款10元，转人工', {}, 'billing', True,
                           order_reference={'active': True, 'ids': ['ORD123', 'ORD456']})
    assert [t.kind for t in ambiguous] == ['product_order', 'technical', 'handoff']


def test_workbench_local_access_hot_edit_and_ticket_closure(tmp_path):
    skills = tmp_path / 'skills'
    skills.mkdir()
    skill = skills / 'SKILL.md'
    skill.write_text('---\nname: 技术规范\nagents: technical\nkeywords: 登录\n---\n检查登录状态。', encoding='utf-8')
    settings = Settings(db_path=str(tmp_path / 'db'), skills_dir=str(skills), model_backend='fixture', local_demo_access=True)
    app = create_app(settings)
    with TestClient(app, base_url='http://127.0.0.1', client=('127.0.0.1', 50000)) as c:
        token = c.post('/auth/demo-merchant', headers={'X-SupportFlow-Demo': 'merchant'}).json()['token']
        h = {'Authorization': 'Bearer '+token, 'X-SupportFlow-Demo': 'merchant'}
        assert c.get('/lab/runtime').status_code == 401
        assert c.get('/lab/runtime', headers={'Authorization': 'Bearer '+token}).status_code == 403
        assert c.get('/lab/runtime', headers={**h, 'Origin': 'https://other.example'}).status_code == 403
        customer = app.state.store.issue_token(Principal('demo', 'alice'))
        assert c.get('/lab/runtime', headers={**h, 'Authorization': 'Bearer '+customer}).status_code == 403
        row = c.get('/lab/runtime', headers=h).json()['skills'][0]
        change = {'content': '检查登录状态，然后重新登录。', 'version': row['version']}
        edited = c.patch('/lab/skills/'+row['id'], headers=h, json=change)
        assert edited.status_code == 200
        assert '重新登录' in app.state.service.skills.prompt_for('登录', 'technical')
        assert not app.state.service.skills.prompt_for('登录', 'billing')
        assert c.patch('/lab/skills/'+row['id'], headers=h, json=change).status_code == 409
        p = Principal('demo', 'alice')
        app.state.store.acquire_conversation(p, 'demo-conv', 'lease', 60)
        t = app.state.store.create_ticket(p, 'demo-conv', '需要技术人员检查', 'ticket-demo')
        tid = t['id']
        assert any(x['id'] == tid for x in c.get('/tickets', headers=h).json())
        assert c.patch('/tickets/'+tid, headers=h, json={'status': 'assigned', 'assignee': 'merchant', 'version': 0}).status_code == 200
        assert c.patch('/tickets/'+tid, headers=h, json={'status': 'resolved', 'resolution': '已修复登录配置', 'version': 1}).status_code == 200
        assert '已修复登录配置' in app.state.store.history(p, 'demo-conv')[-1]['content']


def test_archived_evaluation_is_recomputed():
    r = evaluation_report(str(Path(__file__).resolve().parents[1]))
    assert r['evaluated'] == 1200 and r['source_classes'] == 20
    assert len(r['records']) == sum(x['n'] for x in r['confusion']) == 1200
    assert r['report_verified']
    assert r['accuracy'] == pytest.approx(766 / 1200)
    assert r['macro_f1'] == pytest.approx(.6786013430639989)


def test_compound_trace_records_parallelism_and_isolated_inputs(tmp_path):
    class Model(ScriptedModel):
        async def complete(self, messages, system='', *args, **kwargs):
            if '检索改写' in system:
                return '{"queries":["登录认证故障"]}'
            if '相关文档索引' in system:
                return '{"order":[0]}'
            if '订单指代匹配器' in system:
                return '{"kind":"none","ids":[],"certain":true}'
            await asyncio.sleep(.02)
            if 'technical' in system:
                if '工具执行结果' in messages[-1]['content']:
                    return json.dumps({'answer': '请检查登录状态并重新登录后再尝试。', 'tool_calls': []})
                return json.dumps({'answer': '', 'tool_calls': [{'name': 'knowledge_search', 'arguments': {'query': '登录401'}}]})
            return await super().complete(messages, system, **kwargs)
    s = Settings(db_path=str(tmp_path / 'trace.db'), model_backend='fixture')
    app = create_app(s, Model(s))
    store = app.state.store
    p = Principal('demo', 'alice')
    store.seed_order(Principal('demo', 'admin', frozenset({'admin'})), 'ORD1001', 5000, 'alice')
    app.state.service.knowledge.seed('demo')
    with TestClient(app) as c:
        r = c.post('/chat', headers={'Authorization': 'Bearer '+store.issue_token(p)}, json={'message': '登录报错401，同时查询订单ORD1001状态，并申请退款10元', 'request_id': 'compound-observe'}).json()
    tasks = r['execution']['tasks']
    assert {t['kind'] for t in tasks} == {'technical', 'order', 'refund'}
    tech = next(t for t in tasks if t['kind'] == 'technical')
    assert 'ORD1001' not in json.dumps(tech['input'])
    assert '10元' not in tech['input']['message']
    assert min(t['started_ms'] + t['duration_ms'] for t in tasks) > max(t['started_ms'] for t in tasks)
    assert r['execution']['skills']
    assert any(t['shared'] for t in r['execution']['tools'])
    assert r['execution']['knowledge'][0]['result']['branches']
    order_task = next(t for t in tasks if t['kind'] == 'order')
    assert '退款申请' not in order_task['answer'] and 'rf_' not in order_task['answer']
