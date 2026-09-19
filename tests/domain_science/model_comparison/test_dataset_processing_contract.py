from __future__ import annotations

import pytest

from scios.domain_science.model_comparison.dataset import (
    Dataset,
    Processing,
)


def test_dataset_requires_core_fields():
    dataset = Dataset(
        dataset_id="dataset-001",
        source="experiment-001",
        metadata={"format": "csv"},
    )

    assert dataset.dataset_id == "dataset-001"
    assert dataset.source == "experiment-001"
    assert dataset.metadata == {"format": "csv"}


def test_dataset_metadata_is_model_neutral():
    dataset = Dataset(
        dataset_id="dataset-001",
        source="experiment-001",
        metadata={
            "format": "csv",
            "observables": ["observable-001"],
            "geometry": "geometry-001",
        },
    )

    assert dataset.metadata["format"] == "csv"
    assert dataset.metadata["observables"] == ["observable-001"]
    assert dataset.metadata["geometry"] == "geometry-001"


def test_processing_requires_core_fields():
    processing = Processing(
        processing_id="processing-001",
        input_dataset_id="dataset-001",
        description="Deterministic preprocessing.",
        parameters={"filter": "noise-reduction"},
    )

    assert processing.processing_id == "processing-001"
    assert processing.input_dataset_id == "dataset-001"
    assert processing.description == "Deterministic preprocessing."
    assert processing.parameters == {"filter": "noise-reduction"}


def test_processing_is_descriptive_not_executable():
    processing = Processing(
        processing_id="processing-001",
        input_dataset_id="dataset-001",
        description="Model-independent processing description.",
        parameters={"method": "example"},
    )

    assert not hasattr(processing, "execute")
    assert not hasattr(processing, "run")
    assert not hasattr(processing, "pipeline")
    assert not hasattr(processing, "executor")


def test_processing_does_not_encode_model_identity():
    processing = Processing(
        processing_id="processing-001",
        input_dataset_id="dataset-001",
        description="Model-neutral processing.",
        parameters={"method": "example"},
    )

    assert not hasattr(processing, "model")
    assert not hasattr(processing, "model_id")
    assert not hasattr(processing, "entity_id")


@pytest.mark.parametrize(
    "metadata",
    [
        {},
        {"format": "csv"},
        {"source": "experiment-001"},
        {"observables": ["observable-001"]},
    ],
)
def test_dataset_accepts_neutral_metadata(metadata):
    dataset = Dataset(
        dataset_id="dataset-001",
        source="experiment-001",
        metadata=metadata,
    )

    assert dataset.metadata == metadata


@pytest.mark.parametrize(
    "parameters",
    [
        {},
        {"method": "filter"},
        {"threshold": 0.5},
        {"bootstrap": 5000},
    ],
)
def test_processing_accepts_neutral_parameters(parameters):
    processing = Processing(
        processing_id="processing-001",
        input_dataset_id="dataset-001",
        description="Generic processing.",
        parameters=parameters,
    )

    assert processing.parameters == parameters