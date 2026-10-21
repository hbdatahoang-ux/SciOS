import pytest

from scios.domain_science.model_comparison.identity import (
    ExplanatoryEntityIdentity,
)


def test_identity_requires_core_fields():
    identity = ExplanatoryEntityIdentity(
        entity_id="entity-001",
        name="Example Entity",
        version="0.1",
        entity_type="constitutive_model",
    )

    assert identity.entity_id == "entity-001"
    assert identity.name == "Example Entity"
    assert identity.version == "0.1"
    assert identity.entity_type == "constitutive_model"


@pytest.mark.parametrize(
    "entity_type",
    [
        "constitutive_model",
        "competing_hypothesis",
    ],
)
def test_identity_accepts_supported_entity_types(entity_type):
    identity = ExplanatoryEntityIdentity(
        entity_id="entity-001",
        name="Example Entity",
        version="0.1",
        entity_type=entity_type,
    )

    assert identity.entity_type == entity_type


@pytest.mark.parametrize(
    "entity_type",
    [
        "confirmed",
        "refuted",
        "winner",
        "invalid",
    ],
)
def test_identity_rejects_non_entity_types(entity_type):
    with pytest.raises(ValueError):
        ExplanatoryEntityIdentity(
            entity_id="entity-001",
            name="Example Entity",
            version="0.1",
            entity_type=entity_type,
        )


def test_identity_does_not_encode_evaluation_state():
    identity = ExplanatoryEntityIdentity(
        entity_id="entity-001",
        name="Example Entity",
        version="0.1",
        entity_type="constitutive_model",
    )

    assert not hasattr(identity, "evaluation")
    assert not hasattr(identity, "supported")
    assert not hasattr(identity, "claim")
