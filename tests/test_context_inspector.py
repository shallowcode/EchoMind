import json
import httpx
import pytest

from supportflow.contracts import Settings, Trace
from supportflow.model import Model, active_trace
from supportflow.presentation import execution_view


@pytest.mark.asyncio
@pytest.mark.parametrize('backend,schema_support', [('compatible', True), ('compatible', False), ('anthropic', False)])
async def test_captures_exact_outbound_body_and_immutable_rounds(backend, schema_support):
    sent = []

    def respond(request):
        sent.append(json.loads(request.content))
        if backend == 'compatible':
            return httpx.Response(200, json={'choices': [{'message': {'content': 'answer'}}], 'usage': {'prompt_tokens': 10, 'completion_tokens': 2}})
        return httpx.Response(200, json={'content': [{'type': 'text', 'text': 'answer'}], 'usage': {'input_tokens': 10, 'output_tokens': 2}})

    settings = Settings(model_backend=backend, supports_json_schema=schema_support, model_key='HEADER-SECRET-ONLY', model_url='https://model.example/v1')
    model = Model(settings)
    await model.client.aclose()
    model.client = httpx.AsyncClient(transport=httpx.MockTransport(respond))
    trace = Trace('trace-input')
    token = active_trace.set(trace)
    try:
        messages = [{'role': 'user', 'content': '本轮问题'}]
        schema = {'type': 'object', 'properties': {'answer': {'type': 'string'}}}
        await model.complete(messages, '应用系统提示', json_mode=schema, purpose='账单助手 · 第 1 轮')
        messages.append({'role': 'user', 'content': '工具执行结果：已批准'})
        await model.complete(messages, '应用系统提示', purpose='账单助手 · 第 2 轮')
        assert [call['request'] for call in trace.model_inputs] == sent
        assert trace.model_inputs[0]['request']['messages'][-1]['content'] == '本轮问题'
        assert trace.model_inputs[1]['request']['messages'][-1]['content'].endswith('已批准')
        assert [call['index'] for call in trace.model_inputs] == [1, 2]
        assert all(call['status'] == 'completed' for call in trace.model_inputs)
        assert 'HEADER-SECRET-ONLY' not in json.dumps(trace.model_inputs)
        if backend == 'compatible' and not schema_support:
            assert 'JSON Schema' in trace.model_inputs[0]['request']['messages'][0]['content']
        view = execution_view({'status': 'completed', 'latency_ms': 1}, trace, settings)
        assert view['schema_version'] == 2 and view['model_inputs'] == trace.model_inputs
    finally:
        active_trace.reset(token)
        await model.close()


@pytest.mark.asyncio
async def test_failed_request_still_records_input_without_error_response_body():
    model = Model(Settings(model_url='https://model.example/v1'))
    await model.client.aclose()
    model.client = httpx.AsyncClient(transport=httpx.MockTransport(lambda request: httpx.Response(500, text='provider-error-private-body')))
    trace = Trace('failed-input')
    token = active_trace.set(trace)
    try:
        with pytest.raises(httpx.HTTPStatusError):
            await model.complete([{'role': 'user', 'content': '输入'}], purpose='失败调用')
        assert trace.model_inputs[0]['status'] == 'failed'
        assert trace.model_inputs[0]['error'] == 'HTTPStatusError'
        assert 'provider-error-private-body' not in json.dumps(trace.model_inputs)
    finally:
        active_trace.reset(token)
        await model.close()


def test_memory_and_knowledge_details_use_actual_trace_results():
    trace = Trace('context-input')
    trace.memory = {'history': [{'role': 'user', 'content': '旧问题'}], 'recall': [{'content': '召回事实'}], 'summary': '会话摘要'}
    trace.tools = [{'name': 'knowledge_search', 'success': True, 'cached': True, 'arguments': {'query': '退款政策'}, 'result': {'items': [{'id': 'doc1', 'title': '政策', 'content': '实际检索正文'}], 'queries': ['退款政策', '退款规则'], 'rerank_applied': True}}]
    view = execution_view({'status': 'completed', 'latency_ms': 1}, trace, Settings())
    assert view['memory'] == trace.memory
    assert view['knowledge'][0]['cached']
    assert view['knowledge'][0]['result']['items'][0]['content'] == '实际检索正文'
    assert view['model_inputs'] == []
