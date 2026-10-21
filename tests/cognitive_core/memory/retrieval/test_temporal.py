from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from scios.cognitive_core.memory.core import MemoryRecord
from scios.cognitive_core.memory.retrieval.base import RetrievalStrategy
from scios.cognitive_core.memory.retrieval.temporal import TemporalRetrieval


def make_record(
    content: str,
    created_at: datetime,
) -> MemoryRecord:
    return MemoryRecord(
        content=content,
        created_at=created_at,
    )


class TestTemporalRetrieval:
    def test_is_retrieval_strategy(self):
        assert issubclass(TemporalRetrieval, RetrievalStrategy)

    def test_default_name(self):
        retriever = TemporalRetrieval()

        assert retriever.name == "TemporalRetrieval"

    def test_custom_name(self):
        retriever = TemporalRetrieval(name="CustomTemporal")

        assert retriever.name == "CustomTemporal"

    def test_valid_name_is_preserved(self):
        retriever = TemporalRetrieval(name="  Temporal  ")

        assert retriever.name == "  Temporal  "

    def test_empty_name_rejected(self):
        with pytest.raises(
            ValueError,
            match="name must be a non-empty string",
        ):
            TemporalRetrieval(name="")

    def test_whitespace_name_rejected(self):
        with pytest.raises(
            ValueError,
            match="name must be a non-empty string",
        ):
            TemporalRetrieval(name="   ")

    def test_non_string_name_rejected(self):
        with pytest.raises(
            ValueError,
            match="name must be a non-empty string",
        ):
            TemporalRetrieval(name=123)  # type: ignore[arg-type]

    def test_retrieve_returns_tuple(self):
        timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
        record = make_record("memory", timestamp)

        result = TemporalRetrieval().retrieve([record], timestamp)

        assert isinstance(result, tuple)

    def test_record_at_query_timestamp_is_included(self):
        timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
        record = make_record("memory", timestamp)

        result = TemporalRetrieval().retrieve([record], timestamp)

        assert result == (record,)

    def test_record_after_query_timestamp_is_included(self):
        query = datetime(2026, 1, 1, tzinfo=timezone.utc)
        record = make_record(
            "memory",
            query + timedelta(seconds=1),
        )

        result = TemporalRetrieval().retrieve([record], query)

        assert result == (record,)

    def test_record_before_query_timestamp_is_excluded(self):
        query = datetime(2026, 1, 1, tzinfo=timezone.utc)
        record = make_record(
            "memory",
            query - timedelta(seconds=1),
        )

        result = TemporalRetrieval().retrieve([record], query)

        assert result == ()

    def test_multiple_records_are_filtered(self):
        query = datetime(2026, 1, 1, tzinfo=timezone.utc)

        old = make_record(
            "old",
            query - timedelta(days=1),
        )
        exact = make_record(
            "exact",
            query,
        )
        new = make_record(
            "new",
            query + timedelta(days=1),
        )

        result = TemporalRetrieval().retrieve(
            [old, exact, new],
            query,
        )

        assert result == (exact, new)

    def test_input_order_is_preserved(self):
        query = datetime(2026, 1, 1, tzinfo=timezone.utc)

        first = make_record(
            "first",
            query + timedelta(days=3),
        )
        second = make_record(
            "second",
            query + timedelta(days=1),
        )
        third = make_record(
            "third",
            query + timedelta(days=2),
        )

        result = TemporalRetrieval().retrieve(
            [first, second, third],
            query,
        )

        assert result == (first, second, third)

    def test_record_identity_is_preserved(self):
        query = datetime(2026, 1, 1, tzinfo=timezone.utc)
        record = make_record(
            "memory",
            query,
        )

        result = TemporalRetrieval().retrieve([record], query)

        assert result[0] is record

    def test_multiple_record_identity_is_preserved(self):
        query = datetime(2026, 1, 1, tzinfo=timezone.utc)

        first = make_record("first", query)
        second = make_record(
            "second",
            query + timedelta(seconds=1),
        )

        result = TemporalRetrieval().retrieve(
            [first, second],
            query,
        )

        assert result[0] is first
        assert result[1] is second

    def test_empty_records_return_empty_tuple(self):
        query = datetime(2026, 1, 1, tzinfo=timezone.utc)

        result = TemporalRetrieval().retrieve([], query)

        assert result == ()

    def test_non_matching_records_return_empty_tuple(self):
        query = datetime(2026, 1, 1, tzinfo=timezone.utc)
        record = make_record(
            "memory",
            query - timedelta(days=1),
        )

        result = TemporalRetrieval().retrieve([record], query)

        assert result == ()

    def test_non_datetime_query_rejected(self):
        with pytest.raises(
            TypeError,
            match="query must be a datetime",
        ):
            TemporalRetrieval().retrieve([], "2026-01-01")  # type: ignore[arg-type]

    def test_integer_query_rejected(self):
        with pytest.raises(
            TypeError,
            match="query must be a datetime",
        ):
            TemporalRetrieval().retrieve([], 123)  # type: ignore[arg-type]

    def test_none_query_rejected(self):
        with pytest.raises(
            TypeError,
            match="query must be a datetime",
        ):
            TemporalRetrieval().retrieve([], None)  # type: ignore[arg-type]

    def test_accepts_any_iterable(self):
        query = datetime(2026, 1, 1, tzinfo=timezone.utc)
        record = make_record("memory", query)

        records = (item for item in [record])

        result = TemporalRetrieval().retrieve(records, query)

        assert result == (record,)

    def test_duplicate_records_are_preserved(self):
        query = datetime(2026, 1, 1, tzinfo=timezone.utc)
        record = make_record("memory", query)

        result = TemporalRetrieval().retrieve(
            [record, record],
            query,
        )

        assert result == (record, record)
        assert result[0] is record
        assert result[1] is record

    def test_records_are_not_mutated(self):
        query = datetime(2026, 1, 1, tzinfo=timezone.utc)
        record = make_record("memory", query)

        before = (
            record.content,
            record.id,
            dict(record.metadata),
            record.created_at,
            record.updated_at,
            record.kind,
        )

        TemporalRetrieval().retrieve([record], query)

        after = (
            record.content,
            record.id,
            dict(record.metadata),
            record.created_at,
            record.updated_at,
            record.kind,
        )

        assert after == before

    def test_metadata_does_not_affect_temporal_matching(self):
        query = datetime(2026, 1, 1, tzinfo=timezone.utc)

        record = MemoryRecord(
            content="memory",
            created_at=query - timedelta(days=1),
            metadata={
                "created_at": query.isoformat(),
                "timestamp": query.isoformat(),
            },
        )

        result = TemporalRetrieval().retrieve([record], query)

        assert result == ()

    def test_only_created_at_is_used(self):
        query = datetime(2026, 1, 1, tzinfo=timezone.utc)

        record = MemoryRecord(
            content="memory",
            created_at=query - timedelta(days=1),
            updated_at=query + timedelta(days=1),
        )

        result = TemporalRetrieval().retrieve([record], query)

        assert result == ()

    def test_retriever_does_not_store_records(self):
        retriever = TemporalRetrieval()
        query = datetime(2026, 1, 1, tzinfo=timezone.utc)
        record = make_record("memory", query)

        retriever.retrieve([record], query)

        assert not hasattr(retriever, "_records")

    def test_repeated_calls_are_independent(self):
        query = datetime(2026, 1, 1, tzinfo=timezone.utc)

        first = make_record("first", query)
        second = make_record(
            "second",
            query - timedelta(days=1),
        )

        retriever = TemporalRetrieval()

        first_result = retriever.retrieve([first], query)
        second_result = retriever.retrieve([second], query)

        assert first_result == (first,)
        assert second_result == ()

    def test_timezone_aware_datetimes_are_supported(self):
        query = datetime(2026, 1, 1, tzinfo=timezone.utc)
        record = make_record(
            "memory",
            datetime(
                2026,
                1,
                1,
                1,
                tzinfo=timezone.utc,
            ),
        )

        result = TemporalRetrieval().retrieve([record], query)

        assert result == (record,)

    def test_naive_datetime_comparison_is_supported_when_both_are_naive(self):
        query = datetime(2026, 1, 1)
        record = make_record(
            "memory",
            query + timedelta(days=1),
        )

        result = TemporalRetrieval().retrieve([record], query)

        assert result == (record,)

    def test_mixed_naive_and_aware_datetimes_raise_type_error(self):
        query = datetime(2026, 1, 1, tzinfo=timezone.utc)
        record = make_record(
            "memory",
            datetime(2026, 1, 2),
        )

        with pytest.raises(TypeError):
            TemporalRetrieval().retrieve([record], query)
