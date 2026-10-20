"""Exercise real Go HTTP + Python RPC boundaries using a uniquely named sandbox order."""
import argparse
import json
import time
import uuid
import httpx


def verify(url):
    suffix = uuid.uuid4().hex[:12]
    order_id = 'ORDVERIFY' + suffix
    client = httpx.Client(base_url=url, timeout=240, trust_env=False)
    def call(method, path, actor=None, body=None, expected=200, headers=None):
        response = client.request(method, path, json=body, headers={**({'Authorization': 'Bearer ' + actor} if actor else {}), **(headers or {})})
        assert response.status_code == expected, (path, response.status_code, response.text[:1200])
        return response.json()
    def session(audience):
        return call('POST', '/auth/demo-' + audience, headers={'X-SupportFlow-Demo': audience})['token']
    customer, merchant, operator = (session(a) for a in ('customer', 'merchant', 'operator'))
    assert call('GET', '/ready')['runtime']['backend'] == 'Go'
    call('POST', '/merchant/orders', merchant, {'order_id': order_id, 'customer': 'alice', 'product': '架构验收棉袜', 'quantity': 1, 'total_cents': 3900, 'status': 'paid'}, 201)
    conv = None
    def chat(message, request_id=None):
        nonlocal conv
        body = {'message': message, 'conv_id': conv, 'request_id': request_id or str(uuid.uuid4())}
        result = call('POST', '/chat', customer, body)
        conv = result['conv_id']
        return result, body
    def evidence(result, tool):
        rows = [row for row in result['trace']['tools'] if row['name'] == tool and row['success']]
        assert rows, (tool, result['response'])
        return rows[-1]['result']
    result, body = chat('查询订单 ' + order_id)
    assert evidence(result, 'order_lookup')['status'] == 'paid'
    replay = call('POST', '/chat', customer, body)
    assert replay['replayed'] and replay['response'] == result['response']
    call('POST', '/chat', customer, {**body, 'message': '不同消息'}, 409)
    call('PATCH', '/merchant/orders/' + order_id, merchant, {'status': 'shipped', 'version': 0})
    result, _ = chat('查询订单 ' + order_id)
    assert evidence(result, 'order_lookup')['status'] == 'shipped'
    result, _ = chat('我要为订单 ' + order_id + ' 申请退款10元')
    refund_id = evidence(result, 'refund_request')['id']
    call('POST', f'/refunds/{refund_id}/approval', merchant, {'approve': True})
    result, _ = chat('查询订单 ' + order_id + ' 的退款进度')
    assert any(x['status'] == 'approved' for x in evidence(result, 'refund_status')['items'])
    call('POST', f'/refunds/{refund_id}/settle', merchant)
    call('POST', f'/refunds/{refund_id}/settle', merchant)
    result, _ = chat('查询订单 ' + order_id + ' 的退款进度')
    assert any(x['status'] == 'settled' for x in evidence(result, 'refund_status')['items'])
    assert call('GET', '/orders/' + order_id, customer)['refunded'] == 1000
    ticket = call('POST', '/tickets', customer, {'conv_id': conv, 'summary': '架构验收人工接管', 'idempotency_key': 'verify-' + suffix})
    result, human_body = chat('我需要补充说明')
    assert result['status'] == 'awaiting_human' and 'trace' not in result
    detail = call('GET', '/conversations/' + conv, operator)
    call('POST', '/conversations/' + conv + '/takeover', operator, {'version': detail['version']})
    reply = {'message': '已核实退款结果，人工客服为您跟进。', 'request_id': 'reply-' + suffix}
    call('POST', '/conversations/' + conv + '/messages', operator, reply)
    call('POST', '/conversations/' + conv + '/messages', operator, reply)
    detail = call('GET', '/conversations/' + conv, customer)
    assert sum(m['content'] == reply['message'] for m in detail['messages']) == 1
    assert any(m.get('execution', {}).get('steps') for m in detail['messages'])
    for version, state in enumerate(('assigned', 'resolved', 'closed')):
        call('PATCH', '/tickets/' + ticket['id'], operator, {'status': state, 'version': version, 'resolution': '验收通过' if state == 'resolved' else ''})
    call('POST', '/conversations/' + conv + '/resume-ai', operator, {'version': detail['version']})
    assert call('POST', '/chat', customer, human_body)['replayed']
    result, _ = chat('查询订单 ' + order_id)
    assert evidence(result, 'order_lookup')['refunded'] == 1000
    with client.stream('GET', '/events', headers={'Authorization': 'Bearer ' + customer}) as stream:
        assert stream.status_code == 200
        event = next(json.loads(line[6:]) for line in stream.iter_lines() if line.startswith('data: '))
        assert event['conv']
    runtime = call('GET', '/lab/runtime', merchant, headers={'X-SupportFlow-Demo': 'merchant'})
    assert runtime['knowledge'] and runtime['audit']
    headers = {'Accept': 'application/json, text/event-stream', 'MCP-Protocol-Version': '2025-03-26'}
    rpc = call('POST', '/mcp/', merchant, {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call', 'params': {'name': 'order_list', 'arguments': {}}}, headers=headers)
    assert not rpc['result'].get('isError'), rpc
    with client.stream('POST', f'/copilot/conversations/{conv}/suggest', headers={'Authorization': 'Bearer ' + operator}) as stream:
        assert stream.status_code == 200 and stream.headers['content-type'].startswith('text/event-stream')
        names = [line[7:] for line in stream.iter_lines() if line.startswith('event: ')]
    assert names.count('delta') >= 1 and names[-1] == 'done', names
    summary = call('POST', f'/copilot/conversations/{conv}/summary', operator)
    assert summary['summary']['intent'] and summary['meta']['prompt_version'].startswith('summary@')
    call('POST', f'/copilot/conversations/{conv}/suggest', customer, expected=403)
    job = call('POST', '/knowledge/jobs', operator, {'doc_id': 'verify-' + suffix, 'title': '验收文档', 'content': '验收段落一。\n\n验收段落二。'}, 202)['job']
    for _ in range(60):
        state = call('GET', '/knowledge/jobs/' + job['id'], operator)
        if state['status'] in ('succeeded', 'failed'):
            break
        time.sleep(0.5)
    assert state['status'] == 'succeeded', state
    usage = call('GET', '/usage?days=1', operator)
    assert usage['total']['requests'] >= 2 and any(f['feature'] == 'suggest_reply' for f in usage['by_feature'])
    user = 'verify_' + suffix
    call('POST', '/users', operator, {'user': user, 'name': '验收客户', 'password': 'test-only-password-123', 'roles': ['customer']}, 201)
    account = call('POST', '/auth/login', body={'tenant': 'demo', 'user': user, 'password': 'test-only-password-123'})
    call('GET', '/orders/' + order_id, account['token'], expected=403)
    call('PATCH', '/users/' + user, operator, {'disabled': True})
    call('GET', '/auth/me', account['token'], expected=401)
    call('DELETE', '/merchant/orders/' + order_id + '?version=1', merchant)
    call('POST', '/merchant/orders/' + order_id + '/restore', merchant)
    client.close()
    print(json.dumps({'result': 'passed', 'order': order_id, 'conversation': conv,
                      'checks': ['live order state', 'refund approval/settlement', 'idempotent replay', 'human takeover/reply/resume', 'SSE', 'MCP', 'knowledge/audit', 'account ownership/revocation', 'delete/restore',
                                 'copilot SSE/summary', 'async knowledge ingestion', 'usage metering']}, ensure_ascii=False))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:18002')
    verify(parser.parse_args().url)
