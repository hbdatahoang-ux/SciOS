import pytest
from scios.cognitive_core.reasoning.rule_engine import RuleEngine

def test_rule_engine_infer_matches_condition():
    engine = RuleEngine()
    context = {"weather": "rain"}
    conclusions = engine.infer(context)
    # Rule mặc định trong RuleBase: "rain → carry umbrella"
    assert "carry umbrella" in conclusions

def test_rule_engine_add_and_remove_rule():
    engine = RuleEngine()
    engine.add_rule("cold", "wear jacket")
    assert any(r["condition"] == "cold" for r in engine.get_rules())
    engine.remove_rule("cold")
    assert not any(r["condition"] == "cold" for r in engine.get_rules())

def test_rule_engine_status_and_clear():
    engine = RuleEngine()
    count_before = engine.status()["rules_count"]
    engine.add_rule("hungry", "eat food")
    assert engine.status()["rules_count"] == count_before + 1
    engine.clear()
    assert engine.status()["rules_count"] == 0
