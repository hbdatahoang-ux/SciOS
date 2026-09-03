from __future__ import annotations

from datetime import datetime, timezone

import pytest

from scios.cognitive_core.memory.core import MemoryRecord
from scios.cognitive_core.memory.retrieval.base import RetrievalStrategy
from scios.cognitive_core.memory.retrieval.semantic import SemanticRetrieval


def make_record(content: str) -> MemoryRecord:
    return MemoryRecord(
        content=content,
        created_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )


def similarity_by_content(
    record: MemoryRecord,
    query: str,
) -> float:
    scores = {
        "first": 0.9,
        "second": 0.7,
        "third": 0.3,
    }
    return scores.get(record.content, 0.0)


class TestSemanticRetrieval:
    def test_is_retrieval_strategy(self):
        assert issubclass(SemanticRetrieval, RetrievalStrategy)

    def test_default_name(self):
        retriever = SemanticRetrieval(
            similarity=similarity_by_content,
        )

        assert retriever.name == "SemanticRetrieval"

    def test_custom_name(self):
        retriever = SemanticRetrieval(
            name="CustomSemantic",
            similarity=similarity_by_content,
        )

        assert retriever.name == "CustomSemantic"

    def test_valid_name_is_preserved(self):
        retriever = SemanticRetrieval(
            name="  Semantic  ",
            similarity=similarity_by_content,
        )

        assert retriever.name == "  Semantic  "

    def test_empty_name_rejected(self):
        with pytest.raises(
            ValueError,
            match="name must be a non-empty string",
        ):
            SemanticRetrieval(
                name="",
                similarity=similarity_by_content,
            )

    def test_whitespace_name_rejected(self):
        with pytest.raises(
            ValueError,
            match="name must be a non-empty string",
        ):
            SemanticRetrieval(
                name="   ",
                similarity=similarity_by_content,
            )

    def test_non_string_name_rejected(self):
        with pytest.raises(
            ValueError,
            match="name must be a non-empty string",
        ):
            SemanticRetrieval(
                name=123,  # type: ignore[arg-type]
                similarity=similarity_by_content,
            )

    def test_similarity_must_be_callable(self):
        with pytest.raises(
            TypeError,
            match="similarity must be callable",
        ):
            SemanticRetrieval(
                similarity=123,  # type: ignore[arg-type]
            )

    def test_similarity_function_is_preserved(self):
        retriever = SemanticRetrieval(
            similarity=similarity_by_content,
        )

        assert retriever.similarity is similarity_by_content

    def test_default_threshold_is_zero(self):
        retriever = SemanticRetrieval(
            similarity=similarity_by_content,
        )

        assert retriever.threshold == 0.0

    def test_custom_threshold_is_preserved(self):
        retriever = SemanticRetrieval(
            similarity=similarity_by_content,
            threshold=0.75,
        )

        assert retriever.threshold == 0.75

    def test_integer_threshold_is_converted_to_float(self):
        retriever = SemanticRetrieval(
            similarity=similarity_by_content,
            threshold=1,
        )

        assert retriever.threshold == 1.0
        assert isinstance(retriever.threshold, float)

    def test_float_threshold_is_preserved(self):
        retriever = SemanticRetrieval(
            similarity=similarity_by_content,
            threshold=0.5,
        )

        assert retriever.threshold == 0.5

    def test_boolean_threshold_is_rejected(self):
        with pytest.raises(
            TypeError,
            match="threshold must be a number",
        ):
            SemanticRetrieval(
                similarity=similarity_by_content,
                threshold=True,
            )

    def test_string_threshold_is_rejected(self):
        with pytest.raises(
            TypeError,
            match="threshold must be a number",
        ):
            SemanticRetrieval(
                similarity=similarity_by_content,
                threshold="0.5",  # type: ignore[arg-type]
            )

    def test_none_threshold_is_rejected(self):
        with pytest.raises(
            TypeError,
            match="threshold must be a number",
        ):
            SemanticRetrieval(
                similarity=similarity_by_content,
                threshold=None,  # type: ignore[arg-type]
            )

    def test_retrieve_returns_tuple(self):
        record = make_record("first")

        result = SemanticRetrieval(
            similarity=similarity_by_content,
        ).retrieve([record], "query")

        assert isinstance(result, tuple)

    def test_score_above_threshold_is_included(self):
        record = make_record("first")

        result = SemanticRetrieval(
            similarity=similarity_by_content,
            threshold=0.8,
        ).retrieve([record], "query")

        assert result == (record,)

    def test_score_below_threshold_is_excluded(self):
        record = make_record("second")

        result = SemanticRetrieval(
            similarity=similarity_by_content,
            threshold=0.8,
        ).retrieve([record], "query")

        assert result == ()

    def test_score_equal_to_threshold_is_included(self):
        record = make_record("second")

        result = SemanticRetrieval(
            similarity=similarity_by_content,
            threshold=0.7,
        ).retrieve([record], "query")

        assert result == (record,)

    def test_multiple_records_are_filtered_by_threshold(self):
        first = make_record("first")
        second = make_record("second")
        third = make_record("third")

        result = SemanticRetrieval(
            similarity=similarity_by_content,
            threshold=0.7,
        ).retrieve(
            [first, second, third],
            "query",
        )

        assert result == (first, second)

    def test_input_order_is_preserved(self):
        first = make_record("first")
        second = make_record("second")
        third = make_record("third")

        result = SemanticRetrieval(
            similarity=similarity_by_content,
            threshold=0.2,
        ).retrieve(
            [third, first, second],
            "query",
        )

        assert result == (third, first, second)

    def test_retrieval_does_not_rank_records(self):
        first = make_record("first")
        second = make_record("second")

        result = SemanticRetrieval(
            similarity=similarity_by_content,
            threshold=0.2,
        ).retrieve(
            [second, first],
            "query",
        )

        assert result == (second, first)

    def test_record_identity_is_preserved(self):
        record = make_record("first")

        result = SemanticRetrieval(
            similarity=similarity_by_content,
        ).retrieve([record], "query")

        assert result[0] is record

    def test_multiple_record_identity_is_preserved(self):
        first = make_record("first")
        second = make_record("second")

        result = SemanticRetrieval(
            similarity=similarity_by_content,
            threshold=0.5,
        ).retrieve(
            [first, second],
            "query",
        )

        assert result[0] is first
        assert result[1] is second

    def test_empty_records_return_empty_tuple(self):
        result = SemanticRetrieval(
            similarity=similarity_by_content,
        ).retrieve([], "query")

        assert result == ()

    def test_empty_query_returns_empty_tuple(self):
        record = make_record("first")

        result = SemanticRetrieval(
            similarity=similarity_by_content,
        ).retrieve([record], "")

        assert result == ()

    def test_whitespace_query_returns_empty_tuple(self):
        record = make_record("first")

        result = SemanticRetrieval(
            similarity=similarity_by_content,
        ).retrieve([record], "   ")

        assert result == ()

    def test_non_string_query_is_rejected(self):
        with pytest.raises(
            TypeError,
            match="query must be a string",
        ):
            SemanticRetrieval(
                similarity=similarity_by_content,
            ).retrieve([], 123)  # type: ignore[arg-type]

    def test_none_query_is_rejected(self):
        with pytest.raises(
            TypeError,
            match="query must be a string",
        ):
            SemanticRetrieval(
                similarity=similarity_by_content,
            ).retrieve([], None)  # type: ignore[arg-type]

    def test_similarity_receives_record_and_query(self):
        calls: list[tuple[MemoryRecord, str]] = []

        def similarity(
            record: MemoryRecord,
            query: str,
        ) -> float:
            calls.append((record, query))
            return 1.0

        record = make_record("memory")

        SemanticRetrieval(
            similarity=similarity,
        ).retrieve([record], "scientific query")

        assert calls == [(record, "scientific query")]

    def test_similarity_is_called_once_per_record(self):
        calls: list[MemoryRecord] = []

        def similarity(
            record: MemoryRecord,
            query: str,
        ) -> float:
            calls.append(record)
            return 1.0

        records = [
            make_record("first"),
            make_record("second"),
            make_record("third"),
        ]

        SemanticRetrieval(
            similarity=similarity,
        ).retrieve(records, "query")

        assert calls == records

    def test_similarity_can_return_zero(self):
        record = make_record("third")

        result = SemanticRetrieval(
            similarity=similarity_by_content,
            threshold=0.0,
        ).retrieve([record], "query")

        assert result == (record,)

    def test_similarity_can_return_negative_score(self):
        def similarity(
            record: MemoryRecord,
            query: str,
        ) -> float:
            return -0.5

        record = make_record("memory")

        result = SemanticRetrieval(
            similarity=similarity,
            threshold=0.0,
        ).retrieve([record], "query")

        assert result == ()

    def test_similarity_result_is_not_modified(self):
        observed: list[float] = []

        def similarity(
            record: MemoryRecord,
            query: str,
        ) -> float:
            score = 0.73
            observed.append(score)
            return score

        record = make_record("memory")

        SemanticRetrieval(
            similarity=similarity,
            threshold=0.5,
        ).retrieve([record], "query")

        assert observed == [0.73]

    def test_duplicate_records_are_preserved(self):
        record = make_record("first")

        result = SemanticRetrieval(
            similarity=similarity_by_content,
        ).retrieve(
            [record, record],
            "query",
        )

        assert result == (record, record)
        assert result[0] is record
        assert result[1] is record

    def test_accepts_any_iterable(self):
        record = make_record("first")

        records = (item for item in [record])

        result = SemanticRetrieval(
            similarity=similarity_by_content,
        ).retrieve(records, "query")

        assert result == (record,)

    def test_records_are_not_mutated(self):
        record = make_record("first")
        before = (
            record.content,
            record.id,
            dict(record.metadata),
            record.created_at,
            record.updated_at,
            record.kind,
        )

        SemanticRetrieval(
            similarity=similarity_by_content,
        ).retrieve([record], "query")

        after = (
            record.content,
            record.id,
            dict(record.metadata),
            record.created_at,
            record.updated_at,
            record.kind,
        )

        assert after == before

    def test_metadata_does_not_implicitly_determine_similarity(self):
        def similarity(
            record: MemoryRecord,
            query: str,
        ) -> float:
            return 0.0

        record = MemoryRecord(
            content="memory",
            metadata={"similarity": 1.0},
        )

        result = SemanticRetrieval(
            similarity=similarity,
            threshold=0.5,
        ).retrieve([record], "query")

        assert result == ()

    def test_retriever_does_not_store_records(self):
        retriever = SemanticRetrieval(
            similarity=similarity_by_content,
        )
        record = make_record("first")

        retriever.retrieve([record], "query")

        assert not hasattr(retriever, "_records")

    def test_repeated_calls_are_independent(self):
        first = make_record("first")
        second = make_record("third")

        retriever = SemanticRetrieval(
            similarity=similarity_by_content,
            threshold=0.5,
        )

        first_result = retriever.retrieve([first], "query")
        second_result = retriever.retrieve([second], "query")

        assert first_result == (first,)
        assert second_result == ()

    def test_retrieval_does_not_require_a_store(self):
        record = make_record("first")

        result = SemanticRetrieval(
            similarity=similarity_by_content,
        ).retrieve((record,), "query")

        assert result == (record,)
