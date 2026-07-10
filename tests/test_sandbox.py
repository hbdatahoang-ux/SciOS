# tests/test_sandbox.py

import pytest
import time
from scios.cognitive_core.tool_use.sandbox import ToolSandbox


def test_sandbox_execute_success():
    sandbox = ToolSandbox(timeout=2)

    def safe_func():
        return {"status": "success", "result": 42}

    response = sandbox.run(safe_func)
    assert response["status"] == "success"
    assert response["result"] == 42


def test_sandbox_execute_exception():
    sandbox = ToolSandbox(timeout=2)

    def failing_func():
        raise RuntimeError("Simulated failure")

    response = sandbox.run(failing_func)
    assert response["status"] == "error"
    assert "Simulated failure" in response["message"]


def test_sandbox_timeout():
    sandbox = ToolSandbox(timeout=1)

    def slow_func():
        time.sleep(2)
        return {"status": "success", "result": "done"}

    response = sandbox.run(slow_func)
    assert response["status"] == "error"
    assert "timeout" in response["message"].lower()


def test_sandbox_multiple_runs():
    sandbox = ToolSandbox(timeout=2)

    def func1():
        return {"status": "success", "result": "first"}

    def func2():
        return {"status": "success", "result": "second"}

    r1 = sandbox.run(func1)
    r2 = sandbox.run(func2)

    assert r1["result"] == "first"
    assert r2["result"] == "second"
