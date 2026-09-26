# ==============================================================================
# SciOS Runtime Science
# Provenance Model & Lineage Tests
# ==============================================================================

from dataclasses import FrozenInstanceError
from datetime import datetime

import pytest

from scios.runtime.science.provenance.lineage import (
    DuplicateRecordError,
    LineageCycleError,
    MissingParentError,
    ProvenanceLineage,
    RecordNotFoundError,
)
from scios.runtime.science.provenance.models import (
    InvalidProvenanceError,
    ProvenanceRecord,
)


# ==============================================================================
# Helpers
# ==============================================================================


def make_record(
    record_id: str,
    entity_type: str = "hypothesis",
    parent_ids: tuple[str, ...] = (),
) -> ProvenanceRecord:
    return ProvenanceRecord(
        id=record_id,
        entity_type=entity_type,
        parent_ids=parent_ids,
    )


# ==============================================================================
# ProvenanceRecord
# ==============================================================================


def test_provenance_record_creation():
    record = ProvenanceRecord(
        id="H001",
        entity_type="hypothesis",
    )

    assert record.id == "H001"
    assert record.entity_type == "hypothesis"
    assert record.parent_ids == ()
    assert record.metadata == {}
    assert record.created_at.tzinfo is not None


def test_created_at_is_timezone_aware():
    record = ProvenanceRecord(
        id="H001",
        entity_type="hypothesis",
    )

    assert record.created_at.utcoffset() is not None


def test_naive_datetime_is_rejected():
    with pytest.raises(InvalidProvenanceError):
        ProvenanceRecord(
            id="H001",
            entity_type="hypothesis",
            created_at=datetime(2026, 1, 1),
        )


def test_empty_id_is_rejected():
    with pytest.raises(InvalidProvenanceError):
        ProvenanceRecord(
            id="",
            entity_type="hypothesis",
        )


def test_empty_entity_type_is_rejected():
    with pytest.raises(InvalidProvenanceError):
        ProvenanceRecord(
            id="H001",
            entity_type="",
        )


def test_duplicate_parent_ids_are_rejected():
    with pytest.raises(InvalidProvenanceError):
        ProvenanceRecord(
            id="H002",
            entity_type="hypothesis",
            parent_ids=("H001", "H001"),
        )


def test_parent_ids_are_immutable():
    record = ProvenanceRecord(
        id="H002",
        entity_type="revision",
        parent_ids=("H001",),
    )

    assert isinstance(record.parent_ids, tuple)

    with pytest.raises(FrozenInstanceError):
        record.parent_ids += ("H003",)


def test_metadata_is_read_only():
    record = ProvenanceRecord(
        id="H001",
        entity_type="hypothesis",
        metadata={"source": "human"},
    )

    with pytest.raises(TypeError):
        record.metadata["source"] = "ai"


def test_has_parent():
    record = ProvenanceRecord(
        id="H002",
        entity_type="revision",
        parent_ids=("H001",),
    )

    assert record.has_parent("H001")
    assert not record.has_parent("H999")


def test_with_parent_returns_new_record():
    record = ProvenanceRecord(
        id="H002",
        entity_type="revision",
        parent_ids=("H001",),
    )

    updated = record.with_parent("H003")

    assert record.parent_ids == ("H001",)
    assert updated.parent_ids == ("H001", "H003")
    assert updated.id == record.id
    assert updated.entity_type == record.entity_type


def test_with_existing_parent_returns_same_record():
    record = ProvenanceRecord(
        id="H002",
        entity_type="revision",
        parent_ids=("H001",),
    )

    result = record.with_parent("H001")

    assert result is record


def test_record_is_immutable():
    record = ProvenanceRecord(
        id="H001",
        entity_type="hypothesis",
    )

    with pytest.raises(FrozenInstanceError):
        record.id = "H002"


# ==============================================================================
# ProvenanceLineage - Basic Access
# ==============================================================================


def test_empty_lineage():
    lineage = ProvenanceLineage()

    assert len(lineage) == 0
    assert tuple(lineage) == ()


def test_lineage_creation():
    h001 = make_record("H001")

    lineage = ProvenanceLineage(
        records=(h001,),
    )

    assert len(lineage) == 1
    assert lineage.contains("H001")
    assert lineage.get("H001") is h001


def test_lineage_iteration_preserves_insertion_order():
    h001 = make_record("H001")
    h002 = make_record("H002")
    h003 = make_record("H003")

    lineage = ProvenanceLineage(
        records=(h001, h002, h003),
    )

    assert tuple(record.id for record in lineage) == (
        "H001",
        "H002",
        "H003",
    )


def test_contains_unknown_record():
    lineage = ProvenanceLineage(
        records=(make_record("H001"),),
    )

    assert not lineage.contains("H999")


def test_get_unknown_record_raises():
    lineage = ProvenanceLineage(
        records=(make_record("H001"),),
    )

    with pytest.raises(RecordNotFoundError):
        lineage.get("H999")


# ==============================================================================
# ProvenanceLineage - Integrity
# ==============================================================================


def test_duplicate_record_ids_are_rejected():
    h001_a = make_record("H001")
    h001_b = make_record("H001")

    with pytest.raises(DuplicateRecordError):
        ProvenanceLineage(
            records=(h001_a, h001_b),
        )


def test_missing_parent_is_rejected():
    h002 = make_record(
        "H002",
        parent_ids=("H001",),
    )

    with pytest.raises(MissingParentError):
        ProvenanceLineage(
            records=(h002,),
        )


def test_self_cycle_is_rejected():
    h001 = make_record(
        "H001",
        parent_ids=("H001",),
    )

    with pytest.raises(LineageCycleError):
        ProvenanceLineage(
            records=(h001,),
        )


def test_indirect_cycle_is_rejected():
    h001 = make_record(
        "H001",
        parent_ids=("H003",),
    )
    h002 = make_record(
        "H002",
        parent_ids=("H001",),
    )
    h003 = make_record(
        "H003",
        parent_ids=("H002",),
    )

    with pytest.raises(LineageCycleError):
        ProvenanceLineage(
            records=(h001, h002, h003),
        )


def test_valid_dag_is_accepted():
    h001 = make_record("H001")
    h002 = make_record("H002")
    h003 = make_record(
        "H003",
        parent_ids=("H001", "H002"),
    )

    lineage = ProvenanceLineage(
        records=(h001, h002, h003),
    )

    assert len(lineage) == 3
    assert lineage.contains("H003")


# ==============================================================================
# ProvenanceLineage - Relationships
# ==============================================================================


def test_parents_returns_direct_parents():
    h001 = make_record("H001")
    h002 = make_record("H002")
    h003 = make_record(
        "H003",
        parent_ids=("H001", "H002"),
    )

    lineage = ProvenanceLineage(
        records=(h001, h002, h003),
    )

    parents = lineage.parents("H003")

    assert tuple(record.id for record in parents) == (
        "H001",
        "H002",
    )


def test_parents_returns_empty_for_root():
    h001 = make_record("H001")

    lineage = ProvenanceLineage(
        records=(h001,),
    )

    assert lineage.parents("H001") == ()


def test_children_returns_direct_children():
    h001 = make_record("H001")
    h002 = make_record(
        "H002",
        parent_ids=("H001",),
    )
    h003 = make_record(
        "H003",
        parent_ids=("H001",),
    )

    lineage = ProvenanceLineage(
        records=(h001, h002, h003),
    )

    children = lineage.children("H001")

    assert tuple(record.id for record in children) == (
        "H002",
        "H003",
    )


def test_children_returns_empty_for_leaf():
    h001 = make_record("H001")

    lineage = ProvenanceLineage(
        records=(h001,),
    )

    assert lineage.children("H001") == ()


def test_ancestors_returns_transitive_parents():
    h001 = make_record("H001")
    h002 = make_record(
        "H002",
        parent_ids=("H001",),
    )
    h003 = make_record(
        "H003",
        parent_ids=("H002",),
    )

    lineage = ProvenanceLineage(
        records=(h001, h002, h003),
    )

    ancestors = lineage.ancestors("H003")

    assert tuple(record.id for record in ancestors) == (
        "H002",
        "H001",
    )


def test_ancestors_returns_empty_for_root():
    h001 = make_record("H001")

    lineage = ProvenanceLineage(
        records=(h001,),
    )

    assert lineage.ancestors("H001") == ()


def test_ancestors_supports_dag():
    h001 = make_record("H001")
    h002 = make_record("H002")
    h003 = make_record(
        "H003",
        parent_ids=("H001", "H002"),
    )
    h004 = make_record(
        "H004",
        parent_ids=("H003",),
    )

    lineage = ProvenanceLineage(
        records=(h001, h002, h003, h004),
    )

    ancestors = lineage.ancestors("H004")

    assert tuple(record.id for record in ancestors) == (
        "H003",
        "H001",
        "H002",
    )


def test_relationship_lookup_unknown_record_raises():
    lineage = ProvenanceLineage(
        records=(make_record("H001"),),
    )

    with pytest.raises(RecordNotFoundError):
        lineage.parents("H999")

    with pytest.raises(RecordNotFoundError):
        lineage.children("H999")

    with pytest.raises(RecordNotFoundError):
        lineage.ancestors("H999")


# ==============================================================================
# ProvenanceLineage - Validation
# ==============================================================================


def test_validate_accepts_valid_lineage():
    h001 = make_record("H001")
    h002 = make_record(
        "H002",
        parent_ids=("H001",),
    )

    lineage = ProvenanceLineage(
        records=(h001, h002),
    )

    assert lineage.validate() is None