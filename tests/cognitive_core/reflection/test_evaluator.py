# tests/test_evaluator.py
import pytest
from scios.cognitive_core.reflection.evaluator import Evaluator

def test_evaluator_success():
    evaluator = Evaluator()
    data = {"execution_result": {"success": True, "output": "Result OK"}}
    result = evaluator.process(data)
    assert result["success"] is True
    assert "Execution succeeded" in result["message"]

def test_evaluator_failure():
    evaluator = Evaluator()
    data = {"execution_result": {"success": False, "error": "Runtime error"}}
    result = evaluator.process(data)
    assert result["success"] is False
    assert "Execution failed" in result["message"]

def test_evaluator_missing_keys():
    evaluator = Evaluator()
    data = {}  # no execution_result
    result = evaluator.process(data)
    # Default should be failure
    assert result["success"] is False
    assert "Execution failed" in result["message"]
