# tests/test_recovery.py

import pytest
from scios.cognitive_core.tool_use.recovery import Recovery


def test_recovery_initialization_and_schema():
    r = Recovery(max_retries=2)
    assert r.max_retries == 2
    assert r.attempts == 0

    data = r.to_dict()
    required_keys = {"max_retries", "attempts", "status", "message"}
    assert required_keys.issubset(data.keys())
    assert data["status"] == "idle"


def test_recovery_retry_success():
    r = Recovery(max_retries=3)

    def succeed_on_second_attempt():
        if r.attempts < 1:
            raise RuntimeError("First attempt fails")
        return "ok"

    result = r.run(succeed_on_second_attempt)
    assert result == "ok"
    assert r.attempts == 2
    assert r.status == "success"


def test_recovery_retry_failure_exceeds_max():
    r = Recovery(max_retries=2)

    def always_fail():
        raise RuntimeError("Always fails")

    with pytest.raises(RuntimeError):
        r.run(always_fail)

    assert r.attempts == 2
    assert r.status == "error"
    assert "Always fails" in r.message


def test_recovery_fallback_triggered():
    r = Recovery(max_retries=1)

    def fail():
        raise RuntimeError("Failing")

    def fallback():
        return "fallback result"

    result = r.run(fail, fallback=fallback)
    assert result == "fallback result"
    assert r.status == "fallback"


def test_recovery_reset():
    r = Recovery(max_retries=2)

    def fail():
        raise RuntimeError("Failing")

    try:
        r.run(fail)
    except RuntimeError:
        pass

    assert r.status == "error"
    r.reset()
    assert r.attempts == 0
    assert r.status == "idle"
    assert r.message is None


def test_recovery_repr_shows_status_and_attempts():
    r = Recovery(max_retries=2)
    def fail(): raise RuntimeError("Failing")
    try:
        r.run(fail)
    except RuntimeError:
        pass

    repr_str = repr(r)
    assert "status=error" in repr_str
    assert "attempts=2" in repr_str
