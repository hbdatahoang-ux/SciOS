import pytest

from scios.domain_science.model_comparison.definition import (
    ExplanatoryEntityDefinition,
)


def test_definition_requires_core_fields():
    definition = ExplanatoryEntityDefinition(
        definition_id="definition-001",
        entity_id="entity-001",
        description="An explanatory entity definition.",
        metadata={"assumptions": ["example"]},
    )

    assert definition.definition_id == "definition-001"
    assert definition.entity_id == "entity-001"
    assert definition.description == "An explanatory entity definition."
    assert definition.metadata == {"assumptions": ["example"]}


@pytest.mark.parametrize(
    "metadata",
    [
        {"assumptions": ["example"]},
        {"fields": ["observable"]},
        {"mechanism": "example mechanism"},
        {"expected_signatures": ["signature-1", "signature-2"]},
    ],
)
def test_definition_accepts_model_neutral_metadata(metadata):
    definition = ExplanatoryEntityDefinition(
        definition_id="definition-001",
        entity_id="entity-001",
        description="Model-neutral definition.",
        metadata=metadata,
    )

    assert definition.metadata == metadata


def test_definition_metadata_is_independent_of_entity_role():
    constitutive_definition = ExplanatoryEntityDefinition(
        definition_id="definition-001",
        entity_id="entity-001",
        description="Constitutive explanatory definition.",
        metadata={
            "assumptions": ["assumption-1"],
            "fields": ["field-1"],
        },
    )

    competing_definition = ExplanatoryEntityDefinition(
        definition_id="definition-002",
        entity_id="entity-002",
        description="Competing explanatory definition.",
        metadata={
            "mechanism": "alternative mechanism",
            "expected_signatures": ["signature-1"],
        },
    )

    assert constitutive_definition.entity_id != competing_definition.entity_id
    assert constitutive_definition.metadata != competing_definition.metadata


def test_definition_does_not_encode_evaluation_state():
    definition = ExplanatoryEntityDefinition(
        definition_id="definition-001",
        entity_id="entity-001",
        description="Neutral definition.",
        metadata={},
    )

    assert not hasattr(definition, "evaluation")
    assert not hasattr(definition, "evaluation_state")
    assert not hasattr(definition, "supported")
    assert not hasattr(definition, "disfavored")
    assert not hasattr(definition, "inconclusive")


def test_definition_does_not_require_entity_specific_fields():
    definition = ExplanatoryEntityDefinition(
        definition_id="definition-001",
        entity_id="entity-001",
        description="Generic explanatory definition.",
        metadata={"custom": "value"},
    )

    assert definition.metadata["custom"] == "value"
