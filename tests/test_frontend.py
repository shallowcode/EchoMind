"""The browser shell is public; identity and business data still require a token."""

from fastapi.testclient import TestClient
from supportflow.api import create_app
from supportflow.contracts import Settings, Principal


def test_frontend_and_identity_boundary(tmp_path):
    app = create_app(Settings(db_path=str(tmp_path / "ui.sqlite"), model_backend="fixture"))
    store = app.state.store
    principal = Principal("demo", "alice")
    token = store.issue_token(principal)
    with TestClient(app) as client:
        assert client.get("/").status_code == 200
        assert client.get("/assets/app.js").status_code == 200
        assert client.get("/assets/style.css").status_code == 200
        assert client.get("/assets/../.runtime/glm-demo-tokens.json").status_code == 404
        assert client.get("/auth/me").status_code == 401
        headers = {"Authorization": f"Bearer {token}"}
        assert client.get("/auth/me", headers=headers).json() == {
            "tenant": "demo", "user": "alice", "roles": ["customer"]
        }
        expired = store.issue_token(principal, -1)
        assert client.get("/auth/me", headers={"Authorization": f"Bearer {expired}"}).status_code == 401
        store.revoke(Principal("demo", "admin", frozenset({"admin"})), token)
        assert client.get("/auth/me", headers=headers).status_code == 401
