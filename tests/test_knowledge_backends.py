from unittest.mock import MagicMock

import pytest

from supportflow.contracts import Settings
from supportflow.knowledge import Knowledge
from supportflow.store import Store


def test_http_connection_and_reindex_preserve_sql_namespace(tmp_path, monkeypatch):
    import chromadb

    http = MagicMock()
    embedded = MagicMock()
    client = http.return_value
    monkeypatch.setattr(chromadb, "HttpClient", http)
    monkeypatch.setattr(chromadb, "PersistentClient", embedded)
    store = Store(tmp_path / "db.sqlite")
    # Add to SQL in the lightweight mode before switching to a fresh server.
    Knowledge(store, Settings(), None).add("t", "policy:refund", "退款", "先审核")
    Knowledge(store, Settings(), None).add("other", "private", "私有", "另一个租户")
    settings = Settings(storage="chroma", chroma_mode="http", chroma_host="chroma",
                        chroma_port=8000, chroma_ssl=True)
    kb = Knowledge(store, settings, None)
    http.assert_called_once_with(host="chroma", port=8000, ssl=True)
    embedded.assert_not_called()
    client.heartbeat.assert_called_once()
    kb.seed("t")
    args = kb.collection.upsert.call_args.kwargs
    assert args["documents"] == ["先审核"]
    assert args["metadatas"][0]["tenant"] == "t"
    assert args["metadatas"][0]["doc_id"] == "policy:refund"
    kb.collection.delete.assert_called_once_with(where={"tenant": "t"})
    kb.collection.query.return_value = {"ids": [args["ids"]], "documents": [args["documents"]],
        "metadatas": [args["metadatas"]], "distances": [[0.1]]}
    assert kb.search("t", "退款")[0]["content"] == "先审核"


def test_http_failure_never_silently_switches_to_embedded(tmp_path, monkeypatch):
    import chromadb

    monkeypatch.setattr(chromadb, "HttpClient", MagicMock(side_effect=ConnectionError("offline")))
    embedded = MagicMock()
    monkeypatch.setattr(chromadb, "PersistentClient", embedded)
    with pytest.raises(ConnectionError):
        Knowledge(Store(tmp_path / "db.sqlite"), Settings(storage="chroma", chroma_mode="http"), None)
    embedded.assert_not_called()
