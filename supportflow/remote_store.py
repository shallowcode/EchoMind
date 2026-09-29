"""Typed internal RPC adapter. Business data is owned exclusively by Go."""
from dataclasses import asdict
import httpx
from supportflow.contracts import Principal, BusinessRejection


class RemoteStore:
    def __init__(self, url, service_key):
        if len(service_key) < 32:
            raise ValueError("SF_SERVICE_KEY must have at least 32 characters")
        self.client = httpx.Client(base_url=url.rstrip('/'), timeout=15, trust_env=False,
                                   headers={'X-SupportFlow-Service-Key': service_key})

    def close(self):
        self.client.close()

    def call(self, p, operation, **arguments):
        principal = {**asdict(p), 'roles': sorted(p.roles)} if p else {}
        r = self.client.post('/internal/store', json={
            'principal': principal, 'operation': operation, 'arguments': arguments})
        result = r.json()
        if not r.is_success:
            message = result.get('detail', 'Business service unavailable')
            if r.status_code in (401, 403):
                raise PermissionError(message)
            if r.status_code == 409 and result.get('code') != 'conflict':
                raise BusinessRejection(result['code'], message)
            if r.status_code in (409, 422):
                raise ValueError(message)
            raise RuntimeError(message)
        return result

    def authenticate(self, token):
        p = self.call(None, 'authenticate', token=token)
        return Principal(p['tenant'], p['user'], frozenset(p['roles']))

    def history(self, p, conv, limit=20):
        return self.call(p, 'history', conv=conv, limit=limit)

    def profile(self, p):
        return self.call(p, 'profile')

    def cached_request(self, p, rid, fingerprint):
        return self.call(p, 'cached_request', rid=rid, fingerprint=fingerprint)

    def acquire_conversation(self, p, conv, owner, ttl):
        return self.call(p, 'acquire_conversation', conv=conv, owner=owner, ttl=int(ttl))

    def release(self, p, conv, owner):
        return self.call(p, 'release', conv=conv, owner=owner)

    def commit_turn(self, p, conv, owner, rid, fingerprint, message, response, state):
        return self.call(p, 'commit_turn', conv=conv, owner=owner, rid=rid,
                         fingerprint=fingerprint, message=message, response=response, state=state)

    def finalize_turn(self, p, rid, response):
        return self.call(p, 'finalize_turn', rid=rid, response=response)

    def order(self, p, order_id):
        return self.call(p, 'order', order_id=order_id)

    def order_list(self, p):
        return self.call(p, 'order_list')

    def refund_status(self, p, order_id=None, refund_id=None):
        return self.call(p, 'refund_status', order_id=order_id, refund_id=refund_id)

    def refund_request(self, p, order_id, amount, reason, idem, *, full=False):
        return self.call(p, 'refund_request', order_id=order_id, amount=amount,
                         reason=reason, idem=idem, full=full)

    def create_ticket(self, p, conv, summary, idem):
        return self.call(p, 'create_ticket', conv=conv, summary=summary, idem=idem)

    def ticket(self, p, tid):
        return self.call(p, 'ticket', tid=tid)

    def audit_log(self, p):
        return self.call(p, 'audit_log')

    def append_audit(self, p, action, target, detail):
        return self.call(p, 'append_audit', action=action, target=target, detail=detail)
