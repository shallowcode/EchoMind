import json
import pytest
from fastapi.testclient import TestClient

from supportflow.api import create_app
from supportflow.contracts import Settings, Principal
from supportflow.merchant import Merchant
from tests.test_supportflow import ScriptedModel


class ProductModel(ScriptedModel):
    async def complete(self, messages, system='', **kwargs):
        if '订单指代匹配器' in system:
            data = json.loads(messages[0]['content'])
            text = data['message']
            if '那件' in text or text == '全退给我':
                return json.dumps({'kind': 'reference', 'ids': data['previous_ids'], 'certain': True})
            if '耳机' in text:
                ids = [o['id'] for o in data['orders'] if '蓝牙耳机' in o['product']]
                return json.dumps({'kind': 'product', 'ids': ids, 'certain': True})
            if '胡编' in text:
                return json.dumps({'kind': 'product', 'ids': ['ORD9999'], 'certain': True})
            return json.dumps({'kind': 'product', 'ids': [], 'certain': True})
        return await super().complete(messages, system, **kwargs)


@pytest.fixture
def product_app(tmp_path):
    settings = Settings(db_path=str(tmp_path / 'db'), model_backend='fixture')
    app = create_app(settings, ProductModel(settings))
    store = app.state.store
    admin = Principal('t', 'admin', frozenset({'admin'}))
    merchant = Merchant(store)
    merchant.create_order(admin, 'ORD123', 'alice', '内裤', 1, 5000, 'paid')
    merchant.create_order(admin, 'ORD456', 'alice', '黑色无线蓝牙耳机', 1, 9900, 'shipped')
    merchant.create_order(admin, 'ORD789', 'bob', '另一副蓝牙耳机', 1, 10000, 'paid')
    headers = {'Authorization': 'Bearer ' + store.issue_token(Principal('t', 'alice'))}
    with TestClient(app) as client:
        yield client, headers, merchant, admin, store


def chat(c, h, text, rid, conv=None):
    r = c.post('/chat', headers=h, json={'message': text, 'request_id': rid, 'conv_id': conv})
    assert r.status_code == 200, r.text
    return r.json()


def test_product_alias_fresh_status_switch_and_missing(product_app):
    c, h, merchant, admin, _ = product_app
    first = chat(c, h, '我买的内裤怎么还不到', 'product-first')
    assert 'ORD123' in first['response'] and '尚未发货' in first['response']
    assert '请提供' not in first['response']
    merchant.update_order(admin, 'ORD123', 'shipped', 0)
    second = chat(c, h, '那件现在到哪里了', 'product-second', first['conv_id'])
    assert '已发货' in second['response'] and '没有物流轨迹' in second['response']
    third = chat(c, h, '我的耳机到哪里了', 'product-third', first['conv_id'])
    assert 'ORD456' in third['response'] and 'ORD123' not in third['response'] and 'ORD789' not in third['response']
    missing = chat(c, h, '我的冰箱发货了吗', 'product-missing', first['conv_id'])
    assert '没有找到匹配' in missing['response'] and 'ORD456' not in missing['response']
    invalid = chat(c, h, '胡编的订单', 'product-invalid')
    assert invalid['status'] == 'awaiting_input' and 'ORD9999' not in invalid['response']


def test_ambiguous_selection_refund_and_deleted_orders(product_app):
    c, h, merchant, admin, store = product_app
    merchant.create_order(admin, 'ORD124', 'alice', '内裤', 1, 3000, 'paid')
    ambiguous = chat(c, h, '内裤退款给我吧', 'ambiguous-request')
    assert ambiguous['status'] == 'awaiting_input'
    assert 'ORD123' in ambiguous['response'] and 'ORD124' in ambiguous['response']
    assert 'refund_request' not in ambiguous['tools_used']
    selected = chat(c, h, '第二笔', 'choose-second', ambiguous['conv_id'])
    assert 'ORD123' in selected['response'] and '请确认退款金额' in selected['response']
    refund = chat(c, h, '全退给我', 'product-refund', ambiguous['conv_id'])
    assert '50.00' in refund['response'] and '待财务审核' in refund['response']
    r = store.refund_status(Principal('t', 'alice'), 'ORD123')['items'][0]
    store.approve_refund(admin, r['id'])
    progress = chat(c, h, '退款完成了吗', 'product-progress', ambiguous['conv_id'])
    assert '审核已通过' in progress['response'] and r['id'] in progress['response']
    switched = chat(c, h, '我的耳机是什么状态', 'switch-after-refund', ambiguous['conv_id'])
    assert 'ORD456' in switched['response'] and '已发货' in switched['response']
    assert 'refund_status' not in switched['tools_used']
    merchant.delete_order(admin, 'ORD124', 0)
    direct = chat(c, h, '我买的内裤现在是什么状态', 'after-delete')
    assert 'ORD124' not in direct['response'] and direct['status'] == 'completed'


def test_product_query_does_not_authorize_refund(product_app):
    c, h, _, _, store = product_app
    result = chat(c, h, '内裤能退款吗？', 'product-question')
    assert 'refund_request' not in result['tools_used']
    assert store.refund_status(Principal('t', 'alice'), 'ORD123')['items'] == []
