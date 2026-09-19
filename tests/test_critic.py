# tests/test_critic.py
import pytest
from scios.cognitive_core.reflection.critic import Critic

def test_critic_with_success():
    critic = Critic()
    data = {"evaluation": {"success": True}}
    result = critic.process(data)
    assert "strengths" in result
    assert "Execution succeeded" in result["strengths"]
    assert result["weaknesses"] == []
    assert result["risks"] == []

def test_critic_with_failure():
    critic = Critic()
    data = {"evaluation": {"success": False}}
    result = critic.process(data)
    assert "weaknesses" in result
    assert "Execution failed" in result["weaknesses"]
    assert result["strengths"] == []
    assert result["risks"] == []

def test_critic_with_missing_evaluation():
    critic = Critic()
    data = {}  # no evaluation key
    result = critic.process(data)
    # Default should be failure → weakness
    assert "weaknesses" in result
    assert "Execution failed" in result["weaknesses"]
