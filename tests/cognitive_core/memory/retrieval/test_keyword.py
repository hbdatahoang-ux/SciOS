from __future__ import annotations

from dataclasses import replace

import pytest

from scios.cognitive_core.memory.core import MemoryRecord
from scios.cognitive_core.memory.retrieval.keyword import KeywordRetrieval
from scios.cognitive_core.memory.retrieval.base import RetrievalStrategy


def make_record(content: str) -> MemoryRecord:
    return MemoryRecord(content=content)


class TestKeywordRetrieval:
    def test_is_retrieval_strategy(self):
        assert issubclass(KeywordRetrieval, RetrievalStrategy)

    def test_default_name(self):
        retriever = KeywordRetrieval()
        assert retriever.name == "KeywordRetrieval"

    def test_custom_name(self):
        retriever = KeywordRetrieval(name="CustomKeyword")
        assert retriever.name == "CustomKeyword"

    def test_valid_name_is_preserved(self):
        retriever = KeywordRetrieval(name="  Keyword  ")
        assert retriever.name == "  Keyword  "

    def test_empty_name_rejected(self):
        with pytest.raises(ValueError, match="name must be a non-empty string"):
            KeywordRetrieval(name="")

    def test_whitespace_name_rejected(self):
        with pytest.raises(ValueError, match="name must be a non-empty string"):
            KeywordRetrieval(name="   ")

    def test_non_string_name_rejected(self):
        with pytest.raises(ValueError, match="name must be a non-empty string"):
            KeywordRetrieval(name=123)  # type: ignore[arg-type]

    def test_retrieve_returns_tuple(self):
        records = [make_record("Python memory")]
        result = KeywordRetrieval().retrieve(records, "memory")

        assert isinstance(result, tuple)

    def test_matching_content_is_returned(self):
        record = make_record("Python memory system")

        result = KeywordRetrieval().retrieve([record], "memory")

        assert result == (record,)

    def test_non_matching_content_is_excluded(self):
        matching = make_record("Python memory system")
        other = make_record("Distributed runtime")

        result = KeywordRetrieval().retrieve(
            [matching, other],
            "memory",
        )

        assert result == (matching,)

    def test_matching_is_case_insensitive(self):
        record = make_record("Scientific MEMORY System")

        result = KeywordRetrieval().retrieve([record], "memory")

        assert result == (record,)

    def test_query_case_does_not_matter(self):
        record = make_record("Scientific memory system")

        result = KeywordRetrieval().retrieve([record], "MEMORY")

        assert result == (record,)

    def test_substring_matching(self):
        record = make_record("observability metrics")

        result = KeywordRetrieval().retrieve([record], "serv")

        assert result == (record,)

    def test_input_order_is_preserved(self):
        first = make_record("memory first")
        second = make_record("memory second")
        third = make_record("memory third")

        result = KeywordRetrieval().retrieve(
            [first, second, third],
            "memory",
        )

        assert result == (first, second, third)

    def test_non_matching_records_do_not_change_order(self):
        first = make_record("memory first")
        other = make_record("runtime")
        third = make_record("memory third")

        result = KeywordRetrieval().retrieve(
            [first, other, third],
            "memory",
        )

        assert result == (first, third)

    def test_record_identity_is_preserved(self):
        record = make_record("memory")

        result = KeywordRetrieval().retrieve([record], "memory")

        assert result[0] is record

    def test_multiple_records_preserve_identity(self):
        first = make_record("memory first")
        second = make_record("memory second")

        result = KeywordRetrieval().retrieve(
            [first, second],
            "memory",
        )

        assert result[0] is first
        assert result[1] is second

    def test_empty_records_return_empty_tuple(self):
        result = KeywordRetrieval().retrieve([], "memory")

        assert result == ()

    def test_no_match_returns_empty_tuple(self):
        record = make_record("Python runtime")

        result = KeywordRetrieval().retrieve([record], "memory")

        assert result == ()

    def test_empty_query_returns_empty_tuple(self):
        record = make_record("Python runtime")

        result = KeywordRetrieval().retrieve([record], "")

        assert result == ()

    def test_whitespace_query_returns_empty_tuple(self):
        record = make_record("Python runtime")

        result = KeywordRetrieval().retrieve([record], "   ")

        assert result == ()

    def test_non_string_query_rejected(self):
        with pytest.raises(TypeError, match="query must be a string"):
            KeywordRetrieval().retrieve([], 123)  # type: ignore[arg-type]

    def test_accepts_any_iterable(self):
        first = make_record("memory first")
        second = make_record("runtime")

        records = (record for record in [first, second])

        result = KeywordRetrieval().retrieve(records, "memory")

        assert result == (first,)

    def test_duplicate_input_records_are_preserved(self):
        record = make_record("memory")

        result = KeywordRetrieval().retrieve(
            [record, record],
            "memory",
        )

        assert result == (record, record)
        assert result[0] is record
        assert result[1] is record

    def test_retrieve_does_not_mutate_records(self):
        record = make_record("Original memory")

        before = (
            record.content,
            record.id,
            record.metadata,
            record.created_at,
            record.updated_at,
            record.kind,
        )

        KeywordRetrieval().retrieve([record], "memory")

        after = (
            record.content,
            record.id,
            record.metadata,
            record.created_at,
            record.updated_at,
            record.kind,
        )

        assert after == before

    def test_retrieve_does_not_mutate_metadata(self):
        record = make_record("memory")
        record.metadata["source"] = "test"

        before = dict(record.metadata)

        KeywordRetrieval().retrieve([record], "memory")

        assert record.metadata == before

    def test_matching_uses_content_only(self):
        record = MemoryRecord(
            content="Python runtime",
            metadata={"topic": "memory"},
        )

        result = KeywordRetrieval().retrieve([record], "memory")

        assert result == ()

    def test_retrieval_does_not_store_records(self):
        retriever = KeywordRetrieval()
        record = make_record("memory")

        retriever.retrieve([record], "memory")

        assert not hasattr(retriever, "_records")

    def test_repeated_calls_are_independent(self):
        first = make_record("memory")
        second = make_record("runtime")

        retriever = KeywordRetrieval()

        first_result = retriever.retrieve([first], "memory")
        second_result = retriever.retrieve([second], "memory")

        assert first_result == (first,)
        assert second_result == ()

    def test_unicode_case_insensitive_matching(self):
        record = make_record("SCIÖS Memory")

        result = KeywordRetrieval().retrieve([record], "sciös")

        assert result == (record,)

    def test_query_is_not_modified(self):
        retriever = KeywordRetrieval()
        query = "MEMORY"

        retriever.retrieve([make_record("memory")], query)

        assert query == "MEMORY"
