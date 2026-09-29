import httpx
import pytest

from supportflow.api import create_app
from supportflow.contracts import Principal, Settings
from supportflow.refunds import resolve_refund_status
from tests.test_supportflow import ScriptedModel


@pytest.mark.parametrize('question', ['退款完成了吗', '看一下退款完成了吗', '帮我查一下退款进度', '审核通过了吗', '钱到账了吗', '查下退款'])
def test_progress_uses_user_order_not_stale_assistant(question):
    history = [{'role': 'user', 'content': '我要退款 ORD123'}, {'role': 'assistant', 'content': 'ORD999 已提交，待审核'}]
    result = resolve_refund_status(question, {}, history)
    assert result['active'] and result['order_ids'] == ['ORD123']


@pytest.mark.parametrize('question', ['退款规则是什么', '如何申请退款', '我要退款 ORD123 20元', '请查询订单 ORD123 并退款20元', '全退给我', '订单完成了吗'])
def test_policy_new_request_and_order_status_are_separate(question):
    assert not resolve_refund_status(question, {'last_refund': {'order_id': 'ORD123'}}, [])['active']


@pytest.mark.asyncio
async def test_live_refund_progress_after_merchant_changes(tmp_path):
    settings = Settings(db_path=str(tmp_path / 'db'), model_backend='fixture')
    app = create_app(settings, ScriptedModel(settings))
    store = app.state.store
    alice = Principal('t', 'alice')
    admin = Principal('t', 'merchant', frozenset({'staff', 'finance', 'admin'}))
    store.seed_order(admin, 'ORD123', 5000, 'alice')
    customer = {'Authorization': 'Bearer ' + store.issue_token(alice)}
    merchant = {'Authorization': 'Bearer ' + store.issue_token(admin)}
    async with app.router.lifespan_context(app), httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://localhost') as c:
        initial = (await c.post('/chat', headers=customer, json={'message': '我要退款 ORD123 50元', 'request_id': 'create-refund'})).json()
        conv = initial['conv_id']
        rid = store.refund_status(alice, 'ORD123')['items'][0]['id']
        for index, (action, expected, label) in enumerate([(None, 'pending', '待审核'), ('approval', 'approved', '审核已通过，等待执行退款，尚未完成'), ('settle', 'settled', '退款已完成')]):
            if action:
                mutation = await c.post(f'/refunds/{rid}/{action}', headers=merchant, json={'approve': True} if action == 'approval' else None)
                assert mutation.status_code == 200
            response = await c.post('/chat', headers=customer, json={'message': '看一下退款完成了吗', 'conv_id': conv, 'request_id': f'progress-{index}'})
            assert response.status_code == 200
            result = response.json()
            assert label in result['response'] and rid in result['response']
            assert result['tools_used'] == ['refund_status']
            call = result['trace']['tools'][0]
            assert not call['cached'] and call['result']['items'][0]['status'] == expected
            assert result['execution']['tools'][0]['title'] == '退款进度查询'
            assert store.order(alice, 'ORD123')['refunds'][0]['status'] == expected
        assert len(store.refund_status(alice, 'ORD123')['items']) == 1
        # Both direct lookup identifiers obey ownership and tenant isolation.
        for stranger in [Principal('t', 'bob'), Principal('other', 'alice')]:
            for args in [{'refund_id': rid}, {'order_id': 'ORD123'}]:
                with pytest.raises(PermissionError):
                    store.refund_status(stranger, **args)
        direct = (await c.post('/chat', headers=customer, json={'message': f'查退款 {rid} 状态', 'request_id': 'direct-refund-id'})).json()
        assert '退款已完成' in direct['response']
        missing = (await c.post('/chat', headers=customer, json={'message': '退款完成了吗', 'request_id': 'missing-identifier'})).json()
        assert missing['status'] == 'awaiting_input' and 'refund_request' not in missing['tools_used']
        supplied = (await c.post('/chat', headers=customer, json={'message': 'ORD123', 'conv_id': missing['conv_id'], 'request_id': 'supply-identifier'})).json()
        assert supplied['tools_used'] == ['refund_status'] and '退款已完成' in supplied['response']


@pytest.mark.asyncio
@pytest.mark.parametrize('status,label', [('rejected', '审核未通过'), ('processing', '退款处理中'), ('failed', '退款执行失败')])
async def test_other_refund_outcomes_are_not_reported_as_completed(tmp_path, status, label):
    settings = Settings(db_path=str(tmp_path / 'db'), model_backend='fixture')
    app = create_app(settings, ScriptedModel(settings))
    store = app.state.store
    alice, admin = Principal('t', 'alice'), Principal('t', 'admin', frozenset({'admin'}))
    store.seed_order(admin, 'ORD123', 5000, 'alice')
    r = store.refund_request(alice, 'ORD123', 2000, 'test', 'refund-one')
    with store.tx() as db:
        db.execute('UPDATE refunds SET status=? WHERE id=?', (status, r['id']))
    async with app.router.lifespan_context(app), httpx.AsyncClient(transport=httpx.ASGITransport(app=app), base_url='http://localhost') as c:
        result = (await c.post('/chat', headers={'Authorization': 'Bearer ' + store.issue_token(alice)}, json={'message': '订单 ORD123 退款完成了吗', 'request_id': 'check-outcome'})).json()
        assert label in result['response'] and '退款已完成' not in result['response']
        assert 'refund_request' not in result['tools_used']
