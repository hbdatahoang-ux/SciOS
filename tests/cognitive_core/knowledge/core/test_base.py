"""Tests for Knowledge core base contracts."""

import inspect

import pytest

from scios.cognitive_core.knowledge.core.base import KnowledgeComponent


class ExampleComponent(KnowledgeComponent[str]):
    @property
    def name(self) -> str:
        return "example"

    def validate(self, value: str) -> bool:
        return isinstance(value, str) and bool(value.strip())


def test_knowledge_component_is_abstract():
    assert inspect.isabstract(KnowledgeComponent)


def test_name_is_abstract():
    assert getattr(KnowledgeComponent.name, "__isabstractmethod__", False)


def test_validate_is_abstract():
    assert getattr(KnowledgeComponent.validate, "__isabstractmethod__", False)


def test_concrete_component_can_be_created():
    component = ExampleComponent()

    assert component.name == "example"


def test_concrete_component_validate():
    component = ExampleComponent()

    assert component.validate("hello") is True
    assert component.validate("") is False
    assert component.validate("   ") is False


def test_base_cannot_be_instantiated():
    with pytest.raises(TypeError):
        KnowledgeComponent()


def test_generic_contract_is_preserved():
    component = ExampleComponent()

    assert isinstance(component, KnowledgeComponent)


def test_public_exports():
    from scios.cognitive_core.knowledge.core import base

    assert base.__all__ == ["KnowledgeComponent"]
