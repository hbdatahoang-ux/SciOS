"""Tests for Knowledge retrieval base contracts."""

import inspect

import pytest

from scios.cognitive_core.knowledge.retrieval.base import RetrievalStrategy


class ExampleStrategy(RetrievalStrategy[str, str]):
    def __init__(self, name: str = "example"):
        super().__init__(name)

    def retrieve(
        self,
        items,
        query,
    ) -> list[str]:
        return [
            item
            for item in items
            if query.casefold() in item.casefold()
        ]


def test_retrieval_strategy_is_abstract():
    assert inspect.isabstract(RetrievalStrategy)


def test_retrieve_is_abstract():
    assert getattr(
        RetrievalStrategy.retrieve,
        "__isabstractmethod__",
        False,
    )


def test_name_property_is_not_abstract():
    assert not getattr(
        RetrievalStrategy.name,
        "__isabstractmethod__",
        False,
    )


def test_concrete_strategy_can_be_created():
    strategy = ExampleStrategy()

    assert strategy.name == "example"


def test_retrieve_contract():
    strategy = ExampleStrategy()

    assert strategy.retrieve(
        ["Python", "Rust", "PyTorch"],
        "py",
    ) == ["Python", "PyTorch"]


def test_empty_retrieval():
    strategy = ExampleStrategy()

    assert strategy.retrieve([], "query") == []


def test_base_cannot_be_instantiated():
    with pytest.raises(TypeError):
        RetrievalStrategy("base")


def test_name_requires_non_empty_string():
    with pytest.raises(ValueError):
        ExampleStrategy("")


def test_name_rejects_whitespace():
    with pytest.raises(ValueError):
        ExampleStrategy("   ")


def test_name_rejects_non_string():
    with pytest.raises(ValueError):
        ExampleStrategy(None)


def test_name_is_read_only():
    strategy = ExampleStrategy()

    with pytest.raises(AttributeError):
        strategy.name = "changed"


def test_generic_contract_is_preserved():
    strategy = ExampleStrategy()

    assert isinstance(strategy, RetrievalStrategy)


def test_public_export():
    from scios.cognitive_core.knowledge.retrieval import base

    assert base.__all__ == ["RetrievalStrategy"]
