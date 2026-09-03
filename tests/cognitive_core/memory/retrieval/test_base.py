from __future__ import annotations

from datetime import datetime, timezone
from typing import Iterable

import pytest

from scios.cognitive_core.memory.core import MemoryRecord
from scios.cognitive_core.memory.retrieval.base import RetrievalStrategy


class ConcreteRetrieval(RetrievalStrategy):
    def retrieve(
        self,
        records: Iterable[MemoryRecord],
        query: str,
    ) -> tuple[MemoryRecord, ...]:
        return tuple(
            record
            for record in records
            if query.lower() in record.content.lower()
        )


def test_is_abstract() -> None:
    assert RetrievalStrategy.__abstractmethods__ == {"retrieve"}


def test_cannot_instantiate_directly() -> None:
    with pytest.raises(TypeError):
        RetrievalStrategy(name="RetrievalStrategy")


def test_valid_name() -> None:
    strategy = ConcreteRetrieval(name="KeywordRetrieval")

    assert strategy.name == "KeywordRetrieval"


@pytest.mark.parametrize(
    "name",
    [
        "",
        "   ",
        "\t",
        "\n",
    ],
)
def test_rejects_empty_or_whitespace_name(name: str) -> None:
    with pytest.raises(ValueError, match="name must be a non-empty string"):
        ConcreteRetrieval(name=name)


@pytest.mark.parametrize(
    "name",
    [
        None,
        123,
        object(),
        [],
        {},
    ],
)
def test_rejects_non_string_name(name: object) -> None:
    with pytest.raises(ValueError, match="name must be a non-empty string"):
        ConcreteRetrieval(name=name)  # type: ignore[arg-type]


def test_concrete_subclass_can_be_instantiated() -> None:
    strategy = ConcreteRetrieval(name="TestRetrieval")

    assert isinstance(strategy, RetrievalStrategy)


def test_concrete_subclass_implements_retrieve() -> None:
    strategy = ConcreteRetrieval(name="TestRetrieval")

    records = [
        MemoryRecord(content="Python programming"),
        MemoryRecord(content="Scientific computing"),
    ]

    result = strategy.retrieve(records, "python")

    assert isinstance(result, tuple)
    assert len(result) == 1
    assert result[0] is records[0]


def test_retrieve_returns_empty_tuple_when_no_match() -> None:
    strategy = ConcreteRetrieval(name="TestRetrieval")

    records = [
        MemoryRecord(content="Python programming"),
        MemoryRecord(content="Scientific computing"),
    ]

    result = strategy.retrieve(records, "quantum")

    assert result == ()
    assert isinstance(result, tuple)


def test_retrieve_preserves_record_identity() -> None:
    strategy = ConcreteRetrieval(name="TestRetrieval")

    record = MemoryRecord(
        content="Thermodynamics",
        metadata={"domain": "physics"},
        created_at=datetime(2026, 9, 1, tzinfo=timezone.utc),
    )

    result = strategy.retrieve([record], "thermo")

    assert result == (record,)
    assert result[0] is record


def test_retrieve_preserves_input_order() -> None:
    strategy = ConcreteRetrieval(name="TestRetrieval")

    records = [
        MemoryRecord(content="Python"),
        MemoryRecord(content="Python and NumPy"),
        MemoryRecord(content="Python and SciOS"),
    ]

    result = strategy.retrieve(records, "python")

    assert result == tuple(records)


def test_retrieve_does_not_mutate_records() -> None:
    strategy = ConcreteRetrieval(name="TestRetrieval")

    records = [
        MemoryRecord(
            content="Python",
            metadata={"source": "test"},
        ),
        MemoryRecord(
            content="Scientific Python",
            metadata={"source": "research"},
        ),
    ]

    before = tuple(records)

    result = strategy.retrieve(records, "python")

    assert tuple(records) == before
    assert result[0] is records[0]
    assert result[1] is records[1]


def test_retrieve_accepts_any_iterable() -> None:
    strategy = ConcreteRetrieval(name="TestRetrieval")

    records = (
        record
        for record in [
            MemoryRecord(content="Python"),
            MemoryRecord(content="Java"),
        ]
    )

    result = strategy.retrieve(records, "python")

    assert isinstance(result, tuple)
    assert len(result) == 1
    assert result[0].content == "Python"


def test_retrieve_accepts_empty_iterable() -> None:
    strategy = ConcreteRetrieval(name="TestRetrieval")

    result = strategy.retrieve([], "anything")

    assert result == ()


def test_retrieve_accepts_string_query() -> None:
    strategy = ConcreteRetrieval(name="TestRetrieval")

    record = MemoryRecord(content="Scientific Operating System")

    result = strategy.retrieve([record], "Operating")

    assert result == (record,)


def test_retrieval_strategy_has_no_store_dependency() -> None:
    strategy = ConcreteRetrieval(name="TestRetrieval")

    assert not hasattr(strategy, "store")
    assert not hasattr(strategy, "records")


def test_strategy_name_is_instance_specific() -> None:
    first = ConcreteRetrieval(name="First")
    second = ConcreteRetrieval(name="Second")

    assert first.name == "First"
    assert second.name == "Second"
    assert first.name != second.name


def test_retrieve_can_be_called_multiple_times() -> None:
    strategy = ConcreteRetrieval(name="TestRetrieval")

    records = [
        MemoryRecord(content="Python"),
        MemoryRecord(content="Rust"),
        MemoryRecord(content="Python and Rust"),
    ]

    first = strategy.retrieve(records, "python")
    second = strategy.retrieve(records, "rust")

    assert first == (records[0], records[2])
    assert second == (records[1], records[2])


def test_retrieve_does_not_modify_strategy_name() -> None:
    strategy = ConcreteRetrieval(name="StableName")

    record = MemoryRecord(content="Python")

    strategy.retrieve([record], "python")

    assert strategy.name == "StableName"
