from __future__ import annotations

import pytest

from scios.domain_science.model_comparison.claim import (
    Claim,
    ClaimRelation,
    ClaimRelationType,
)


def test_claim_requires_core_fields():
    claim = Claim(
        claim_id="claim-001",
        statement="The observed response changes with geometry.",
    )

    assert claim.claim_id == "claim-001"
    assert claim.statement == "The observed response changes with geometry."


def test_claim_is_model_name_neutral():
    claim = Claim(
        claim_id="claim-001",
        statement="The observed response changes with geometry.",
    )

    assert not hasattr(claim, "ceit")
    assert not hasattr(claim, "uniform_wlc")
    assert not hasattr(claim, "heterogeneous_elasticity")
    assert not hasattr(claim, "viscoelastic_gradient")
    assert not hasattr(claim, "boundary_artifact")


def test_claim_does_not_encode_evaluation_state():
    claim = Claim(
        claim_id="claim-001",
        statement="The observed response changes with geometry.",
    )

    assert not hasattr(claim, "supported")
    assert not hasattr(claim, "disfavored")
    assert not hasattr(claim, "inconclusive")
    assert not hasattr(claim, "evaluation_state")


def test_claim_does_not_encode_probability_or_confidence():
    claim = Claim(
        claim_id="claim-001",
        statement="The observed response changes with geometry.",
    )

    assert not hasattr(claim, "probability")
    assert not hasattr(claim, "confidence")
    assert not hasattr(claim, "posterior")
    assert not hasattr(claim, "likelihood")


@pytest.mark.parametrize(
    "relation_type",
    [
        ClaimRelationType.SUPPORTS,
        ClaimRelationType.CONTRADICTS,
    ],
)
def test_claim_relations_support_evidence_to_claim_links(relation_type):
    relation = ClaimRelation(
        relation_id="relation-001",
        relation_type=relation_type,
        source_id="evidence-001",
        target_id="claim-001",
    )

    assert relation.relation_id == "relation-001"
    assert relation.relation_type is relation_type
    assert relation.source_id == "evidence-001"
    assert relation.target_id == "claim-001"


def test_claim_relation_accepts_string_relation_type():
    relation = ClaimRelation(
        relation_id="relation-001",
        relation_type="supports",
        source_id="evidence-001",
        target_id="claim-001",
    )

    assert relation.relation_type is ClaimRelationType.SUPPORTS


def test_claim_relation_does_not_encode_model_specific_names():
    relation = ClaimRelation(
        relation_id="relation-001",
        relation_type="supports",
        source_id="evidence-001",
        target_id="claim-001",
    )

    assert not hasattr(relation, "ceit")
    assert not hasattr(relation, "uniform_wlc")
    assert not hasattr(relation, "boundary_artifact")


def test_claim_relation_is_not_an_inference_engine():
    relation = ClaimRelation(
        relation_id="relation-001",
        relation_type="supports",
        source_id="evidence-001",
        target_id="claim-001",
    )

    assert not hasattr(relation, "infer")
    assert not hasattr(relation, "predict")
    assert not hasattr(relation, "fit")
    assert not hasattr(relation, "score")
    assert not hasattr(relation, "run")


@pytest.mark.parametrize(
    "relation_type",
    [
        "produces",
        "supports",
        "contradicts",
        "evaluates",
    ],
)
def test_lineage_relation_types_are_explicit(relation_type):
    assert relation_type in {
        "produces",
        "supports",
        "contradicts",
        "evaluates",
    }
