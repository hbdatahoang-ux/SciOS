"""
Tests for SciOS Runtime Metrics MetricMiddlewarePipeline.
"""

from __future__ import annotations

import pytest

from ..pipeline import MetricMiddlewarePipeline
from ..stage import MetricMiddlewareStage


# ==============================================================
# Fixtures
# ==============================================================


@pytest.fixture
def pipeline() -> MetricMiddlewarePipeline:
    return MetricMiddlewarePipeline()


def make_stage(
    name: str,
    handler=None,
) -> MetricMiddlewareStage:
    return MetricMiddlewareStage(
        name=name,
        handler=handler,
    )


# ==============================================================
# Construction
# ==============================================================


def test_default_construction(pipeline):
    assert pipeline.name == "MetricMiddlewarePipeline"
    assert pipeline.description == ""
    assert pipeline.enabled is True
    assert pipeline.running is False
    assert pipeline.closed is False
    assert pipeline.active is True
    assert len(pipeline) == 0


def test_custom_construction():
    pipeline = MetricMiddlewarePipeline(
        name="custom",
        description="test",
    )

    assert pipeline.name == "custom"
    assert pipeline.description == "test"


def test_id_is_unique():
    first = MetricMiddlewarePipeline()
    second = MetricMiddlewarePipeline()

    assert first.id != second.id


# ==============================================================
# Stage Management
# ==============================================================


def test_add_stage(pipeline):
    stage = make_stage("first")

    assert pipeline.add_stage(stage) is pipeline
    assert len(pipeline) == 1
    assert pipeline.get_stage("first") is stage


def test_add_stage_preserves_order(pipeline):
    first = make_stage("first")
    second = make_stage("second")

    pipeline.add_stage(first)
    pipeline.add_stage(second)

    assert pipeline.stages() == [
        first,
        second,
    ]


def test_add_stage_requires_stage(pipeline):
    with pytest.raises(TypeError):
        pipeline.add_stage("invalid")


def test_add_stage_rejects_duplicate_name(pipeline):
    pipeline.add_stage(make_stage("stage"))

    with pytest.raises(ValueError):
        pipeline.add_stage(make_stage("stage"))


def test_add_alias(pipeline):
    stage = make_stage("stage")

    assert pipeline.add(stage) is pipeline
    assert pipeline.get_stage("stage") is stage


def test_remove_stage(pipeline):
    stage = make_stage("stage")

    pipeline.add_stage(stage)

    assert pipeline.remove_stage("stage") is pipeline
    assert len(pipeline) == 0
    assert pipeline.get_stage("stage") is None


def test_remove_missing_stage_is_safe(pipeline):
    assert pipeline.remove_stage("missing") is pipeline


def test_remove_alias(pipeline):
    pipeline.add_stage(make_stage("stage"))

    assert pipeline.remove("stage") is pipeline
    assert len(pipeline) == 0


def test_clear_stages(pipeline):
    pipeline.add_stage(make_stage("one"))
    pipeline.add_stage(make_stage("two"))

    assert pipeline.clear_stages() is pipeline
    assert pipeline.stages() == []
    assert len(pipeline) == 0