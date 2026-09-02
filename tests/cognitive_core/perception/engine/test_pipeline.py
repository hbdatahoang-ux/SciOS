"""Contract tests for PerceptionPipeline."""

from __future__ import annotations

import pytest

from scios.cognitive_core.perception.core import (
    BasePerceptor,
    Modality,
    PerceptionResult,
    PerceptionStatus,
)
from scios.cognitive_core.perception.engine.pipeline import (
    PerceptionPipeline,
)


class RecordingPerceptor(BasePerceptor):
    """Minimal perceptor that records received input."""

    def __init__(self, name: str, modality: Modality = Modality.TEXT) -> None:
        super().__init__(name=name, modality=modality)
        self.inputs: list[object] = []

    def perceive(self, raw_input, metadata=None) -> PerceptionResult:
        self.inputs.append(raw_input)

        return PerceptionResult(
            status=PerceptionStatus.SUCCESS,
            modality=self.modality,
            content=f"{raw_input}:{self.name}",
            metadata=metadata or {},
        )


class TestPerceptionPipeline:

    def test_empty_pipeline_is_valid(self) -> None:
        pipeline = PerceptionPipeline()

        assert len(pipeline) == 0
        assert pipeline.perceptors == ()

    def test_constructor_accepts_perceptors(self) -> None:
        first = RecordingPerceptor("first")
        second = RecordingPerceptor("second")

        pipeline = PerceptionPipeline([first, second])

        assert len(pipeline) == 2
        assert pipeline.perceptors == (first, second)

    def test_add_returns_perceptor(self) -> None:
        pipeline = PerceptionPipeline()
        perceptor = RecordingPerceptor("text")

        result = pipeline.add(perceptor)

        assert result is perceptor
        assert len(pipeline) == 1

    def test_add_rejects_invalid_perceptor(self) -> None:
        pipeline = PerceptionPipeline()

        with pytest.raises(TypeError, match="BasePerceptor"):
            pipeline.add(object())  # type: ignore[arg-type]

    def test_remove_returns_perceptor(self) -> None:
        perceptor = RecordingPerceptor("text")
        pipeline = PerceptionPipeline([perceptor])

        result = pipeline.remove("text")

        assert result is perceptor
        assert len(pipeline) == 0

    def test_remove_missing_name_raises_key_error(self) -> None:
        pipeline = PerceptionPipeline()

        with pytest.raises(KeyError, match="not found"):
            pipeline.remove("missing")

    def test_clear_removes_all_perceptors(self) -> None:
        pipeline = PerceptionPipeline(
            [
                RecordingPerceptor("first"),
                RecordingPerceptor("second"),
            ]
        )

        pipeline.clear()

        assert len(pipeline) == 0
        assert pipeline.perceptors == ()

    def test_run_empty_pipeline_raises(self) -> None:
        pipeline = PerceptionPipeline()

        with pytest.raises(RuntimeError, match="empty"):
            pipeline.run("input")

    def test_run_executes_perceptors_in_order(self) -> None:
        first = RecordingPerceptor("first")
        second = RecordingPerceptor("second")

        pipeline = PerceptionPipeline([first, second])

        result = pipeline.run("input")

        assert first.inputs == ["input"]
        assert second.inputs == ["input:first"]
        assert result.content == "input:first:second"

    def test_run_returns_last_result(self) -> None:
        first = RecordingPerceptor("first")
        second = RecordingPerceptor("second")

        pipeline = PerceptionPipeline([first, second])

        result = pipeline.run("input")

        assert result is not None
        assert result.status is PerceptionStatus.SUCCESS
        assert result.modality is Modality.TEXT

    def test_metadata_is_forwarded(self) -> None:
        perceptor = RecordingPerceptor("text")
        pipeline = PerceptionPipeline([perceptor])

        result = pipeline.run(
            "input",
            {"source": "test"},
        )

        assert result.metadata["source"] == "test"

    def test_metadata_is_copied(self) -> None:
        metadata = {"source": "test"}
        pipeline = PerceptionPipeline([RecordingPerceptor("text")])

        pipeline.run("input", metadata)

        assert metadata == {"source": "test"}

    def test_perceptors_property_is_immutable_view(self) -> None:
        perceptor = RecordingPerceptor("text")
        pipeline = PerceptionPipeline([perceptor])

        perceptors = pipeline.perceptors

        assert isinstance(perceptors, tuple)

    def test_pipeline_preserves_perceptor_identity(self) -> None:
        first = RecordingPerceptor("first")
        pipeline = PerceptionPipeline([first])

        assert pipeline.perceptors[0] is first


class TestPerceptionPipelinePublicAPI:

    def test_all_is_exact(self) -> None:
        from scios.cognitive_core.perception.engine import pipeline

        assert pipeline.__all__ == ["PerceptionPipeline"]

    def test_export_is_available(self) -> None:
        from scios.cognitive_core.perception.engine import pipeline

        assert pipeline.PerceptionPipeline is PerceptionPipeline
