"""
Tests for SciOS Runtime Metrics Processors public API.
"""

from __future__ import annotations

import pytest

import scios.runtime.observability.metrics.processors as processors

from scios.runtime.observability.metrics.processors import (
    BatchingProcessor,
    CompressionProcessor,
    EnrichmentProcessor,
    FilterProcessor,
    MetricProcessor,
    NormalizerProcessor,
    Processor,
    SamplingProcessor,
    SamplerProcessor,
    ValidatorProcessor,
    PROCESSORS,
    available_processors,
    build_pipeline,
    create_processor,
    get_processor_class,
)


# ======================================================================
# Imports
# ======================================================================


def test_public_imports():
    assert MetricProcessor is Processor

    assert SamplerProcessor is SamplingProcessor

    assert FilterProcessor is not None
    assert NormalizerProcessor is not None
    assert ValidatorProcessor is not None
    assert EnrichmentProcessor is not None
    assert BatchingProcessor is not None
    assert CompressionProcessor is not None


# ======================================================================
# Registry
# ======================================================================


def test_registry_contains_all_processors():
    expected = {
        "processor",
        "filter",
        "sampler",
        "sampling",
        "normalizer",
        "validator",
        "enrichment",
        "batching",
        "compression",
    }

    assert set(PROCESSORS) == expected


def test_sampler_aliases_same_class():
    assert PROCESSORS["sampler"] is SamplingProcessor
    assert PROCESSORS["sampling"] is SamplingProcessor


def test_available_processors():
    names = available_processors()

    assert isinstance(names, tuple)
    assert names == tuple(sorted(PROCESSORS))
    assert "filter" in names
    assert "compression" in names


# ======================================================================
# Class Resolution
# ======================================================================


@pytest.mark.parametrize(
    "name, expected",
    [
        ("processor", MetricProcessor),
        ("filter", FilterProcessor),
        ("sampler", SamplingProcessor),
        ("sampling", SamplingProcessor),
        ("normalizer", NormalizerProcessor),
        ("validator", ValidatorProcessor),
        ("enrichment", EnrichmentProcessor),
        ("batching", BatchingProcessor),
        ("compression", CompressionProcessor),
    ],
)
def test_get_processor_class(name, expected):
    assert get_processor_class(name) is expected


def test_get_processor_class_strips_name():
    assert (
        get_processor_class("  filter  ")
        is FilterProcessor
    )


def test_get_processor_class_normalizes_case():
    assert (
        get_processor_class("FILTER")
        is FilterProcessor
    )


def test_get_processor_class_requires_string():
    with pytest.raises(TypeError):
        get_processor_class(None)


def test_get_processor_class_rejects_empty_name():
    with pytest.raises(ValueError):
        get_processor_class("")


def test_get_processor_class_rejects_unknown():
    with pytest.raises(ValueError):
        get_processor_class("unknown")


# ======================================================================
# Factory
# ======================================================================


def test_create_processor():
    processor = create_processor(
        "filter"
    )

    assert isinstance(
        processor,
        FilterProcessor,
    )


def test_create_processor_forwards_kwargs():
    processor = create_processor(
        "sampler",
        rate=0.25,
    )

    assert isinstance(
        processor,
        SamplingProcessor,
    )

    assert processor.rate() == 0.25


def test_create_processor_compression_kwargs():
    processor = create_processor(
        "compression",
        algorithm="zlib",
        level=9,
    )

    assert isinstance(
        processor,
        CompressionProcessor,
    )

    assert processor.algorithm == "zlib"
    assert processor.level == 9


def test_create_processor_unknown():
    with pytest.raises(ValueError):
        create_processor(
            "unknown"
        )


# ======================================================================
# Pipeline
# ======================================================================


def test_build_pipeline():
    pipeline = build_pipeline(
        [
            "validator",
            "normalizer",
            "compression",
        ]
    )

    assert len(pipeline) == 3

    assert isinstance(
        pipeline[0],
        ValidatorProcessor,
    )

    assert isinstance(
        pipeline[1],
        NormalizerProcessor,
    )

    assert isinstance(
        pipeline[2],
        CompressionProcessor,
    )


def test_build_pipeline_preserves_order():
    pipeline = build_pipeline(
        [
            "compression",
            "filter",
            "sampler",
        ]
    )

    assert [
        type(item)
        for item in pipeline
    ] == [
        CompressionProcessor,
        FilterProcessor,
        SamplingProcessor,
    ]


def test_build_pipeline_creates_fresh_instances():
    first = build_pipeline(
        ["filter"]
    )

    second = build_pipeline(
        ["filter"]
    )

    assert first[0] is not second[0]


def test_build_pipeline_rejects_string():
    with pytest.raises(TypeError):
        build_pipeline(
            "filter"
        )


def test_build_pipeline_empty():
    assert build_pipeline([]) == []


# ======================================================================
# __all__
# ======================================================================


def test_all_contains_public_api():
    expected = {
        "MetricProcessor",
        "Processor",
        "FilterProcessor",
        "SamplingProcessor",
        "SamplerProcessor",
        "NormalizerProcessor",
        "ValidatorProcessor",
        "EnrichmentProcessor",
        "BatchingProcessor",
        "CompressionProcessor",
        "PROCESSORS",
        "ProcessorClass",
        "available_processors",
        "get_processor_class",
        "create_processor",
        "build_pipeline",
    }

    assert set(processors.__all__) == expected


def test_all_has_no_duplicates():
    assert len(
        processors.__all__
    ) == len(
        set(processors.__all__)
    )