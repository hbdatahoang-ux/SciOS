"""
Contract tests for scios.cognitive_core.common.context.

These tests lock the public behavior of CognitiveContext without
depending on higher-level Cognitive Core subsystems.
"""

from uuid import UUID

from scios.cognitive_core.common.context import CognitiveContext


# ============================================================================
# Construction
# ============================================================================


def test_context_creates_with_default_values():
    context = CognitiveContext()

    assert isinstance(context.context_id, UUID)
    assert context.data == {}
    assert context.metadata == {}
    assert context.stage is None


def test_context_generates_unique_context_ids():
    first = CognitiveContext()
    second = CognitiveContext()

    assert first.context_id != second.context_id


def test_context_accepts_explicit_values():
    context_id = UUID("12345678-1234-5678-1234-567812345678")

    context = CognitiveContext(
        context_id=context_id,
        data={"input": "hello"},
        metadata={"source": "test"},
        stage="reasoning",
    )

    assert context.context_id == context_id
    assert context.data == {"input": "hello"}
    assert context.metadata == {"source": "test"}
    assert context.stage == "reasoning"


# ============================================================================
# Data API
# ============================================================================


def test_set_stores_value():
    context = CognitiveContext()

    context.set("answer", 42)

    assert context.data["answer"] == 42
    assert context.get("answer") == 42


def test_set_overwrites_existing_value():
    context = CognitiveContext()

    context.set("value", 1)
    context.set("value", 2)

    assert context.get("value") == 2


def test_get_returns_default_for_missing_key():
    context = CognitiveContext()

    assert context.get("missing") is None
    assert context.get("missing", "fallback") == "fallback"


def test_get_preserves_falsy_values():
    context = CognitiveContext()

    context.set("zero", 0)
    context.set("false", False)
    context.set("empty", "")
    context.set("none", None)

    assert context.get("zero") == 0
    assert context.get("false") is False
    assert context.get("empty") == ""
    assert context.get("none") is None


# ============================================================================
# Metadata API
# ============================================================================


def test_update_metadata_stores_value():
    context = CognitiveContext()

    context.update_metadata("source", "unit-test")

    assert context.metadata["source"] == "unit-test"
    assert context.get_metadata("source") == "unit-test"


def test_update_metadata_overwrites_existing_value():
    context = CognitiveContext()

    context.update_metadata("attempt", 1)
    context.update_metadata("attempt", 2)

    assert context.get_metadata("attempt") == 2


def test_get_metadata_returns_default_for_missing_key():
    context = CognitiveContext()

    assert context.get_metadata("missing") is None
    assert context.get_metadata("missing", "fallback") == "fallback"


def test_metadata_is_independent_from_data():
    context = CognitiveContext()

    context.set("key", "data")
    context.update_metadata("key", "metadata")

    assert context.get("key") == "data"
    assert context.get_metadata("key") == "metadata"


# ============================================================================
# Stage
# ============================================================================


def test_stage_can_be_set_and_read():
    context = CognitiveContext()

    context.stage = "planning"

    assert context.stage == "planning"


def test_stage_can_be_reset_to_none():
    context = CognitiveContext(stage="reasoning")

    context.stage = None

    assert context.stage is None


# ============================================================================
# Snapshot
# ============================================================================


def test_snapshot_contains_context_id():
    context = CognitiveContext()

    snapshot = context.snapshot()

    assert snapshot["id"] == str(context.context_id)


def test_snapshot_contains_stage():
    context = CognitiveContext(stage="reasoning")

    snapshot = context.snapshot()

    assert snapshot["stage"] == "reasoning"


def test_snapshot_contains_data():
    context = CognitiveContext()

    context.set("query", "test")
    context.set("value", 123)

    snapshot = context.snapshot()

    assert snapshot["data"] == {
        "query": "test",
        "value": 123,
    }


def test_snapshot_contains_metadata():
    context = CognitiveContext()

    context.update_metadata("source", "test")
    context.update_metadata("version", 1)

    snapshot = context.snapshot()

    assert snapshot["metadata"] == {
        "source": "test",
        "version": 1,
    }


def test_snapshot_returns_top_level_copies():
    context = CognitiveContext()

    context.set("key", "value")
    context.update_metadata("source", "test")

    snapshot = context.snapshot()

    snapshot["data"]["key"] = "changed"
    snapshot["metadata"]["source"] = "changed"

    assert context.get("key") == "value"
    assert context.get_metadata("source") == "test"


def test_snapshot_does_not_change_context():
    context = CognitiveContext(stage="reasoning")
    context.set("input", "hello")
    context.update_metadata("source", "test")

    before = context.snapshot()
    after = context.snapshot()

    assert after == before


# ============================================================================
# Clear
# ============================================================================


def test_clear_removes_data():
    context = CognitiveContext()

    context.set("a", 1)
    context.set("b", 2)

    context.clear()

    assert context.data == {}


def test_clear_removes_metadata():
    context = CognitiveContext()

    context.update_metadata("source", "test")
    context.update_metadata("version", 1)

    context.clear()

    assert context.metadata == {}


def test_clear_resets_stage():
    context = CognitiveContext(stage="reflection")

    context.clear()

    assert context.stage is None


def test_clear_does_not_replace_context_id():
    context = CognitiveContext()

    original_id = context.context_id

    context.set("key", "value")
    context.update_metadata("source", "test")
    context.stage = "reasoning"

    context.clear()

    assert context.context_id == original_id


def test_clear_is_idempotent():
    context = CognitiveContext()

    context.set("key", "value")
    context.update_metadata("source", "test")
    context.stage = "reasoning"

    context.clear()
    context.clear()

    assert context.data == {}
    assert context.metadata == {}
    assert context.stage is None


# ============================================================================
# Isolation
# ============================================================================


def test_context_instances_have_independent_data():
    first = CognitiveContext()
    second = CognitiveContext()

    first.set("value", "first")
    second.set("value", "second")

    assert first.get("value") == "first"
    assert second.get("value") == "second"


def test_context_instances_have_independent_metadata():
    first = CognitiveContext()
    second = CognitiveContext()

    first.update_metadata("source", "first")
    second.update_metadata("source", "second")

    assert first.get_metadata("source") == "first"
    assert second.get_metadata("source") == "second"


def test_context_instances_have_independent_default_dicts():
    first = CognitiveContext()
    second = CognitiveContext()

    first.data["x"] = 1
    first.metadata["y"] = 2

    assert second.data == {}
    assert second.metadata == {}