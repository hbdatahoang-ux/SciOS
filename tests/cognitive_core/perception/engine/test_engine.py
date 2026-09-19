"""Contract tests for PerceptionEngine."""

from __future__ import annotations

import pytest

from scios.cognitive_core.perception.core import (
    BasePerceptor,
    Modality,
    PerceptionResult,
    PerceptionStatus,
)
from scios.cognitive_core.perception.engine.engine import (
    PerceptionEngine,
)
from scios.cognitive_core.perception.engine.pipeline import (
    PerceptionPipeline,
)
from scios.cognitive_core.perception.factory import PerceptorFactory
from scios.cognitive_core.perception.registry import PerceptorRegistry


class TextPerceptor(BasePerceptor):

    def __init__(self, name: str = "text") -> None:
        super().__init__(
            name=name,
            modality=Modality.TEXT,
        )

    def perceive(self, raw_input, metadata=None) -> PerceptionResult:
        return PerceptionResult(
            status=PerceptionStatus.SUCCESS,
            modality=self.modality,
            content=raw_input,
            metadata=metadata or {},
        )


class TestPerceptionEngine:

    @pytest.fixture
    def registry(self) -> PerceptorRegistry:
        registry = PerceptorRegistry()
        registry.register(TextPerceptor())
        return registry

    @pytest.fixture
    def factory(
        self,
        registry: PerceptorRegistry,
    ) -> PerceptorFactory:
        return PerceptorFactory(registry)

    def test_constructor_requires_factory(self) -> None:
        factory = PerceptorFactory(PerceptorRegistry())

        engine = PerceptionEngine(factory)

        assert engine.factory is factory
        assert engine.pipeline is None

    def test_constructor_rejects_invalid_factory(self) -> None:
        with pytest.raises(TypeError, match="PerceptorFactory"):
            PerceptionEngine(object())  # type: ignore[arg-type]

    def test_constructor_accepts_pipeline(
        self,
        factory: PerceptorFactory,
    ) -> None:
        pipeline = PerceptionPipeline()

        engine = PerceptionEngine(
            factory,
            pipeline,
        )

        assert engine.pipeline is pipeline

    def test_constructor_rejects_invalid_pipeline(
        self,
        factory: PerceptorFactory,
    ) -> None:
        with pytest.raises(TypeError, match="PerceptionPipeline"):
            PerceptionEngine(
                factory,
                object(),  # type: ignore[arg-type]
            )

    def test_perceive_uses_factory(
        self,
        factory: PerceptorFactory,
    ) -> None:
        engine = PerceptionEngine(factory)

        result = engine.perceive("text", "hello")

        assert isinstance(result, PerceptionResult)
        assert result.content == "hello"
        assert result.modality is Modality.TEXT

    def test_perceive_forwards_metadata(
        self,
        factory: PerceptorFactory,
    ) -> None:
        engine = PerceptionEngine(factory)

        result = engine.perceive(
            "text",
            "hello",
            {"source": "test"},
        )

        assert result.metadata == {"source": "test"}

    def test_perceive_missing_name_raises(
        self,
        factory: PerceptorFactory,
    ) -> None:
        engine = PerceptionEngine(factory)

        with pytest.raises(KeyError):
            engine.perceive("missing", "hello")

    def test_perceive_pipeline_requires_pipeline(
        self,
        factory: PerceptorFactory,
    ) -> None:
        engine = PerceptionEngine(factory)

        with pytest.raises(RuntimeError, match="pipeline"):
            engine.perceive_pipeline("hello")

    def test_perceive_pipeline_executes_pipeline(
        self,
        factory: PerceptorFactory,
    ) -> None:
        pipeline = PerceptionPipeline([TextPerceptor()])

        engine = PerceptionEngine(
            factory,
            pipeline,
        )

        result = engine.perceive_pipeline("hello")

        assert isinstance(result, PerceptionResult)
        assert result.content == "hello"
        assert result.status is PerceptionStatus.SUCCESS

    def test_engine_exposes_same_factory_and_pipeline(
        self,
        factory: PerceptorFactory,
    ) -> None:
        pipeline = PerceptionPipeline()
        engine = PerceptionEngine(factory, pipeline)

        assert engine.factory is factory
        assert engine.pipeline is pipeline


class TestPerceptionEnginePublicAPI:

    def test_all_is_exact(self) -> None:
        from scios.cognitive_core.perception.engine import engine

        assert engine.__all__ == ["PerceptionEngine"]

    def test_export_is_available(self) -> None:
        from scios.cognitive_core.perception.engine import engine

        assert engine.PerceptionEngine is PerceptionEngine
