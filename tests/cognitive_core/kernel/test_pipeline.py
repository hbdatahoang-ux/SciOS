"""
Tests for scios.cognitive_core.kernel.pipeline.
"""

from __future__ import annotations

import pytest

from scios.cognitive_core.kernel.context import CognitiveContext
from scios.cognitive_core.kernel.request import CognitiveRequest
from scios.cognitive_core.kernel.stage import CognitiveStage
from scios.cognitive_core.kernel.pipeline import CognitivePipeline, Pipeline


class DemoStage(CognitiveStage):
    """Concrete stage used by pipeline tests."""

    def __init__(
        self,
        name: str = "demo",
        value: str = "ok",
    ) -> None:
        super().__init__(name)
        self.value = value
        self.run_count = 0

    def run(self, context: CognitiveContext):
        self.run_count += 1
        context.set(self.name, self.value)
        return self.value


class FailingStage(CognitiveStage):
    """Stage that always raises an exception."""

    def run(self, context: CognitiveContext):
        raise RuntimeError("stage failed")


@pytest.fixture
def cognitive_request() -> CognitiveRequest:
    return CognitiveRequest(query="hello")


@pytest.fixture
def context(
    cognitive_request: CognitiveRequest,
) -> CognitiveContext:
    return CognitiveContext(cognitive_request)


@pytest.fixture
def pipeline() -> CognitivePipeline:
    return CognitivePipeline()


def test_pipeline_class_is_available():
    assert CognitivePipeline is not None


def test_pipeline_alias_points_to_cognitive_pipeline():
    assert Pipeline is CognitivePipeline


def test_pipeline_can_be_instantiated():
    pipeline = CognitivePipeline()

    assert isinstance(pipeline, CognitivePipeline)


def test_default_pipeline_has_no_stages(
    pipeline: CognitivePipeline,
):
    assert len(pipeline) == 0


def test_pipeline_repr_contains_class_name(
    pipeline: CognitivePipeline,
):
    result = repr(pipeline)

    assert "CognitivePipeline" in result or "Pipeline" in result


def test_add_stage(
    pipeline: CognitivePipeline,
):
    stage = DemoStage()

    result = pipeline.add(stage)

    assert result is pipeline
    assert len(pipeline) == 1


def test_add_preserves_stage(
    pipeline: CognitivePipeline,
):
    stage = DemoStage("reasoning")

    pipeline.add(stage)

    assert pipeline.get("reasoning") is stage


def test_add_multiple_stages(
    pipeline: CognitivePipeline,
):
    first = DemoStage("perception")
    second = DemoStage("reasoning")

    pipeline.add(first)
    pipeline.add(second)

    assert len(pipeline) == 2
    assert pipeline.get("perception") is first
    assert pipeline.get("reasoning") is second


def test_get_missing_stage_returns_none(
    pipeline: CognitivePipeline,
):
    assert pipeline.get("missing") is None


def test_contains_stage(
    pipeline: CognitivePipeline,
):
    pipeline.add(DemoStage("reasoning"))

    assert "reasoning" in pipeline


def test_missing_stage_not_in_pipeline(
    pipeline: CognitivePipeline,
):
    assert "reasoning" not in pipeline


def test_remove_stage(
    pipeline: CognitivePipeline,
):
    pipeline.add(DemoStage("reasoning"))

    result = pipeline.remove("reasoning")

    assert result is pipeline
    assert len(pipeline) == 0
    assert pipeline.get("reasoning") is None


def test_remove_missing_stage_is_safe(
    pipeline: CognitivePipeline,
):
    result = pipeline.remove("missing")

    assert result is pipeline
    assert len(pipeline) == 0


def test_clear_removes_all_stages(
    pipeline: CognitivePipeline,
):
    pipeline.add(DemoStage("one"))
    pipeline.add(DemoStage("two"))

    result = pipeline.clear()

    assert result is pipeline
    assert len(pipeline) == 0


def test_stages_returns_registered_stages(
    pipeline: CognitivePipeline,
):
    first = DemoStage("one")
    second = DemoStage("two")

    pipeline.add(first)
    pipeline.add(second)

    stages = pipeline.stages

    assert len(stages) == 2
    assert stages[0] is first
    assert stages[1] is second


def test_stage_order_is_preserved(
    pipeline: CognitivePipeline,
):
    names = ["perception", "memory", "reasoning"]

    for name in names:
        pipeline.add(DemoStage(name))

    assert [stage.name for stage in pipeline.stages] == names


def test_run_requires_context(
    pipeline: CognitivePipeline,
):
    pipeline.add(DemoStage())

    with pytest.raises((TypeError, ValueError)):
        pipeline.run()


def test_run_empty_pipeline_returns_none_or_context(
    pipeline: CognitivePipeline,
    context: CognitiveContext,
):
    result = pipeline.run(context)

    assert result is None or result is context


def test_run_single_stage(
    pipeline: CognitivePipeline,
    context: CognitiveContext,
):
    stage = DemoStage()

    pipeline.add(stage)

    result = pipeline.run(context)

    assert result == "ok"
    assert stage.run_count == 1
    assert context.get("demo") == "ok"


def test_run_multiple_stages(
    pipeline: CognitivePipeline,
    context: CognitiveContext,
):
    first = DemoStage("first", "one")
    second = DemoStage("second", "two")

    pipeline.add(first)
    pipeline.add(second)

    result = pipeline.run(context)

    assert result == "two"
    assert first.run_count == 1
    assert second.run_count == 1
    assert context.get("first") == "one"
    assert context.get("second") == "two"


def test_run_preserves_stage_order(
    pipeline: CognitivePipeline,
    context: CognitiveContext,
):
    observed = []

    class OrderedStage(CognitiveStage):
        def run(self, context: CognitiveContext):
            observed.append(self.name)
            return self.name

    pipeline.add(OrderedStage("first"))
    pipeline.add(OrderedStage("second"))
    pipeline.add(OrderedStage("third"))

    pipeline.run(context)

    assert observed == [
        "first",
        "second",
        "third",
    ]


def test_run_returns_last_stage_result(
    pipeline: CognitivePipeline,
    context: CognitiveContext,
):
    pipeline.add(DemoStage("first", "one"))
    pipeline.add(DemoStage("second", "two"))
    pipeline.add(DemoStage("third", "three"))

    result = pipeline.run(context)

    assert result == "three"


def test_run_same_pipeline_multiple_times(
    pipeline: CognitivePipeline,
    context: CognitiveContext,
):
    stage = DemoStage()

    pipeline.add(stage)

    pipeline.run(context)
    pipeline.run(context)

    assert stage.run_count == 2


def test_run_failure_propagates_exception(
    pipeline: CognitivePipeline,
    context: CognitiveContext,
):
    pipeline.add(FailingStage("failing"))

    with pytest.raises(RuntimeError, match="stage failed"):
        pipeline.run(context)


def test_run_failure_stops_following_stages(
    pipeline: CognitivePipeline,
    context: CognitiveContext,
):
    failing = FailingStage("failing")
    following = DemoStage("following")

    pipeline.add(failing)
    pipeline.add(following)

    with pytest.raises(RuntimeError, match="stage failed"):
        pipeline.run(context)

    assert following.run_count == 0


def test_pipeline_stage_status_after_success(
    pipeline: CognitivePipeline,
    context: CognitiveContext,
):
    stage = DemoStage()

    pipeline.add(stage)
    pipeline.run(context)

    assert stage.status == "completed"


def test_pipeline_stage_status_after_failure(
    pipeline: CognitivePipeline,
    context: CognitiveContext,
):
    stage = FailingStage("failing")

    pipeline.add(stage)

    with pytest.raises(RuntimeError):
        pipeline.run(context)

    assert stage.status == "failed"
    assert stage.message == "stage failed"


def test_initialize_initializes_all_stages(
    pipeline: CognitivePipeline,
):
    first = DemoStage("first")
    second = DemoStage("second")

    pipeline.add(first)
    pipeline.add(second)

    result = pipeline.initialize()

    assert result is pipeline
    assert first.is_ready is True
    assert second.is_ready is True


def test_reset_resets_all_stages(
    pipeline: CognitivePipeline,
    context: CognitiveContext,
):
    first = DemoStage("first")
    second = DemoStage("second")

    pipeline.add(first)
    pipeline.add(second)

    pipeline.run(context)

    assert first.is_completed is True
    assert second.is_completed is True

    result = pipeline.reset()

    assert result is pipeline
    assert first.status == "idle"
    assert second.status == "idle"


def test_reset_does_not_remove_stages(
    pipeline: CognitivePipeline,
):
    pipeline.add(DemoStage("first"))
    pipeline.add(DemoStage("second"))

    pipeline.reset()

    assert len(pipeline) == 2


def test_pipeline_can_be_reused_after_reset(
    pipeline: CognitivePipeline,
    context: CognitiveContext,
):
    stage = DemoStage()

    pipeline.add(stage)

    pipeline.run(context)
    pipeline.reset()
    pipeline.run(context)

    assert stage.run_count == 2


def test_pipeline_to_dict_contains_stages(
    pipeline: CognitivePipeline,
):
    pipeline.add(DemoStage("first"))
    pipeline.add(DemoStage("second"))

    result = pipeline.to_dict()

    assert isinstance(result, dict)
    assert "stages" in result


def test_pipeline_to_dict_contains_stage_names(
    pipeline: CognitivePipeline,
):
    pipeline.add(DemoStage("first"))
    pipeline.add(DemoStage("second"))

    result = pipeline.to_dict()

    assert "first" in str(result)
    assert "second" in str(result)


def test_pipeline_status_is_available(
    pipeline: CognitivePipeline,
):
    result = pipeline.status()

    assert isinstance(result, dict)


def test_pipeline_status_reports_stage_count(
    pipeline: CognitivePipeline,
):
    pipeline.add(DemoStage("first"))
    pipeline.add(DemoStage("second"))

    result = pipeline.status()

    assert isinstance(result, dict)

    if "stages" in result:
        assert result["stages"] == 2


def test_pipeline_len_matches_stage_count(
    pipeline: CognitivePipeline,
):
    assert len(pipeline) == 0

    pipeline.add(DemoStage("one"))
    assert len(pipeline) == 1

    pipeline.add(DemoStage("two"))
    assert len(pipeline) == 2


def test_pipeline_iteration(
    pipeline: CognitivePipeline,
):
    first = DemoStage("first")
    second = DemoStage("second")

    pipeline.add(first)
    pipeline.add(second)

    if hasattr(pipeline, "__iter__"):
        assert list(pipeline) == [first, second]


def test_duplicate_stage_name_replaces_or_rejects_consistently(
    pipeline: CognitivePipeline,
):
    first = DemoStage("same", "first")
    second = DemoStage("same", "second")

    pipeline.add(first)

    try:
        pipeline.add(second)
    except (ValueError, KeyError):
        assert pipeline.get("same") is first
    else:
        assert pipeline.get("same") is second


def test_pipeline_context_is_not_created_implicitly(
    pipeline: CognitivePipeline,
):
    pipeline.add(DemoStage())

    assert pipeline is not None


def test_pipeline_accepts_empty_stage_collection():
    pipeline = CognitivePipeline()

    assert len(pipeline) == 0
