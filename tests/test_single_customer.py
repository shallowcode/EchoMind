from fastapi.testclient import TestClient
from supportflow.api import create_app
from supportflow.contracts import Settings, Principal
from tests.test_supportflow import ScriptedModel


def test_single_customer_all_orders_delete_restore_and_refund(tmp_path):
    settings = Settings(db_path=str(tmp_path / 'db'), model_backend='fixture', local_demo_access=True)
    app = create_app(settings, ScriptedModel(settings))
    store = app.state.store
    admin = Principal('demo', 'merchant', frozenset({'admin'}))
    store.seed_order(admin, 'ORD1001', 5000, 'alice')
    store.seed_order(admin, 'ORD2002', 2000, 'bob')
    store.seed_order(Principal('other', 'admin', frozenset({'admin'})), 'ORD9999', 9000, 'alice')
    admin_headers = {'Authorization': 'Bearer ' + store.issue_token(admin)}
    normal_headers = {'Authorization': 'Bearer ' + store.issue_token(Principal('demo', 'alice'))}
    with TestClient(app, base_url='http://127.0.0.1:8002', client=('127.0.0.1', 50000)) as c:
        assert c.post('/auth/demo-customer').status_code == 403
        session = c.post('/auth/demo-customer', headers={'X-SupportFlow-Demo': 'customer'})
        assert session.status_code == 200
        headers = {'Authorization': 'Bearer ' + session.json()['token']}
        assert c.get('/orders', headers=headers).json()['total'] == 2
        assert c.get('/orders', headers=normal_headers).json()['total'] == 1
        assert c.get('/orders/ORD2002', headers=normal_headers).status_code == 403
        assert c.get('/orders/ORD2002', headers=headers).status_code == 200
        assert c.get('/orders/ORD9999', headers=headers).status_code == 403
        result = c.post('/chat', headers=headers, json={'message': '查询全部订单', 'request_id': 'all-demo-orders'}).json()
        assert result['tools_used'] == ['order_list']
        assert 'ORD2002' in result['response'] and 'ORD9999' not in result['response']
        assert c.delete('/merchant/orders/ORD2002?version=0', headers=headers).status_code == 403
        assert c.get('/merchant/orders', headers=headers).status_code == 403
        refund = c.post('/refunds', headers=headers, json={'order_id': 'ORD2002', 'amount_cents': 1000, 'reason': 'test', 'idempotency_key': 'single-user-refund'}).json()
        rid = refund['id']
        assert c.post(f'/refunds/{rid}/approval', headers=headers, json={'approve': True}).status_code == 403
        assert c.delete('/merchant/orders/ORD2002?version=0', headers=admin_headers).status_code == 409
        assert c.post(f'/refunds/{rid}/approval', headers=admin_headers, json={'approve': False}).status_code == 200
        assert c.delete('/merchant/orders/ORD2002?version=0', headers=admin_headers).status_code == 200
        assert c.get('/orders', headers=headers).json()['total'] == 1
        assert c.get('/orders/ORD2002', headers=headers).status_code == 403
        assert c.get('/merchant/orders?status=deleted', headers=admin_headers).json()['total'] == 1
        after = c.post('/chat', headers=headers, json={'message': '查询全部订单', 'conv_id': result['conv_id'], 'request_id': 'after-demo-delete'}).json()
        assert 'ORD2002' not in after['response']
        assert c.post('/merchant/orders/ORD2002/restore', headers=admin_headers).status_code == 200
        assert c.get('/orders', headers=headers).json()['total'] == 2
        assert c.delete('/merchant/orders/ORD2002?version=0', headers=admin_headers).status_code == 409
        created = c.post('/merchant/orders', headers=admin_headers, json={'order_id': 'ORD3003', 'customer': 'bob', 'product': 'new', 'quantity': 1, 'total_cents': 600, 'status': 'paid'})
        assert created.status_code == 201
        assert c.get('/orders/ORD3003', headers=headers).json()['user'] == 'alice'


def test_customer_auto_access_is_local_sandbox_only(tmp_path):
    for enabled, mode in [(False, 'sandbox'), (True, 'external')]:
        app = create_app(Settings(db_path=str(tmp_path / mode), model_backend='fixture', local_demo_access=enabled, business_mode=mode))
        with TestClient(app, base_url='http://127.0.0.1', client=('127.0.0.1', 50000)) as c:
            assert c.post('/auth/demo-customer', headers={'X-SupportFlow-Demo': 'customer'}).status_code == 404
