from core.skill_loader import SkillManager
from core.intent_recognizer import IntentRecognizer


def test_skill_reload_and_agent_scope(tmp_path):
    path = tmp_path / "SKILL.md"
    path.write_text(
        "---\nname: refund policy\nagents: billing\nkeywords: 退款，账单\n---\n# Policy\n第一版待审核。",
        encoding="utf-8",
    )
    manager = SkillManager(str(tmp_path))
    manager.load()
    assert "第一版" in manager.prompt_for("退款", "billing")
    assert not manager.prompt_for("退款", "technical")
    path.write_text(
        path.read_text(encoding="utf-8").replace("第一版", "第二版"), encoding="utf-8"
    )
    manager.reload()
    assert "第二版" in manager.prompt_for("账单", "billing")


def test_intent_cache_uses_full_message_and_history():
    recognizer = IntentRecognizer("test")
    assert recognizer._cache_key("a" * 200 + "订单") != recognizer._cache_key(
        "a" * 200 + "退款"
    )
    assert recognizer._cache_key(
        "same", [{"role": "user", "content": "b" * 160 + "订单"}]
    ) != recognizer._cache_key(
        "same", [{"role": "user", "content": "b" * 160 + "退款"}]
    )
    assert recognizer._extract_entities("订单编号是 ORD1001，登录401")["order_id"] == [
        "ORD1001"
    ]
    assert recognizer._extract_entities("订单编号是 ORD1001，登录401")[
        "error_code"
    ] == ["401"]
