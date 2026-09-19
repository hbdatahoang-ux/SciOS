# ==========================================================
# Part 1. Imports & Fixtures
# ==========================================================

import copy
import inspect
import pickle
import threading

import pytest

from scios.runtime.observability.metrics.core.metrics.exporters.registry import (
    DEFAULT_ALLOW_OVERRIDE,
    DEFAULT_CASE_SENSITIVE,
    DEFAULT_VERSION,
    ExporterRegistry,
    __all__,
)

_RLOCK_TYPE = type(threading.RLock())


# ==========================================================
# Part 2. Dummy Exporters
# ==========================================================

class DummyExporter:

    def __init__(self, value: int = 1):
        self.value = value


class AnotherExporter:

    def __init__(self, value: int = 2):
        self.value = value


# ==========================================================
# Part 3. TestConstruction
# ==========================================================

class TestConstruction:

    def test_create_default(self):

        registry = ExporterRegistry()

        assert isinstance(
            registry,
            ExporterRegistry,
        )

    def test_version(self):

        registry = ExporterRegistry()

        assert registry.version == DEFAULT_VERSION

    def test_case_sensitive(self):

        registry = ExporterRegistry()

        assert registry.case_sensitive is DEFAULT_CASE_SENSITIVE

    def test_allow_override(self):

        registry = ExporterRegistry()

        assert registry.allow_override is DEFAULT_ALLOW_OVERRIDE

    def test_exporters(self):

        registry = ExporterRegistry()

        assert registry.exporters == {}

    def test_names(self):

        registry = ExporterRegistry()

        assert registry.names == []

    def test_size(self):

        registry = ExporterRegistry()

        assert registry.size == 0

    def test_lock(self):

        registry = ExporterRegistry()

        assert isinstance(
            registry.lock,
            _RLOCK_TYPE,
        )

# ==========================================================
# Part 4. TestRegistration
# ==========================================================

class TestRegistration:

    def test_register(self):

        registry = ExporterRegistry()

        registry.register(
            "dummy",
            DummyExporter,
        )

        assert registry.exists(
            "dummy",
        )

        assert registry.size == 1

    def test_unregister(self):

        registry = ExporterRegistry()

        registry.register(
            "dummy",
            DummyExporter,
        )

        registry.unregister(
            "dummy",
        )

        assert not registry.exists(
            "dummy",
        )

        assert registry.size == 0

    def test_replace(self):

        registry = ExporterRegistry()

        registry.register(
            "dummy",
            DummyExporter,
        )

        registry.replace(
            "dummy",
            AnotherExporter,
        )

        assert registry.get(
            "dummy",
        ) is AnotherExporter

    def test_clear(self):

        registry = ExporterRegistry()

        registry.register(
            "a",
            DummyExporter,
        )

        registry.register(
            "b",
            AnotherExporter,
        )

        registry.clear()

        assert registry.size == 0

        assert registry.exporters == {}

    def test_override_allowed(self):

        registry = ExporterRegistry(
            allow_override=True,
        )

        registry.register(
            "dummy",
            DummyExporter,
        )

        registry.register(
            "dummy",
            AnotherExporter,
        )

        assert registry.get(
            "dummy",
        ) is AnotherExporter

    def test_override_disallowed(self):

        registry = ExporterRegistry(
            allow_override=False,
        )

        registry.register(
            "dummy",
            DummyExporter,
        )

        with pytest.raises(
            KeyError,
        ):
            registry.register(
                "dummy",
                AnotherExporter,
            )


# ==========================================================
# Part 5. TestLookup
# ==========================================================

class TestLookup:

    def test_get(self):

        registry = ExporterRegistry()

        registry.register(
            "dummy",
            DummyExporter,
        )

        assert registry.get(
            "dummy",
        ) is DummyExporter

        assert registry.get(
            "missing",
        ) is None

    def test_require(self):

        registry = ExporterRegistry()

        registry.register(
            "dummy",
            DummyExporter,
        )

        assert registry.require(
            "dummy",
        ) is DummyExporter

        with pytest.raises(
            KeyError,
        ):
            registry.require(
                "missing",
            )

    def test_exists(self):

        registry = ExporterRegistry()

        registry.register(
            "dummy",
            DummyExporter,
        )

        assert registry.exists(
            "dummy",
        )

        assert not registry.exists(
            "missing",
        )

    def test_find(self):

        registry = ExporterRegistry()

        registry.register(
            "DummyExporter",
            DummyExporter,
        )

        registry.register(
            "AnotherExporter",
            AnotherExporter,
        )

        result = registry.find(
            "dummy",
        )

        assert "DummyExporter" in result


# ==========================================================
# Part 6. TestListing
# ==========================================================

class TestListing:

    def test_list_exporters(self):

        registry = ExporterRegistry()

        registry.register(
            "a",
            DummyExporter,
        )

        registry.register(
            "b",
            AnotherExporter,
        )

        exporters = registry.list_exporters()

        assert len(
            exporters,
        ) == 2

        assert DummyExporter in exporters

        assert AnotherExporter in exporters

    def test_list_names(self):

        registry = ExporterRegistry()

        registry.register(
            "a",
            DummyExporter,
        )

        registry.register(
            "b",
            AnotherExporter,
        )

        names = registry.list_names()

        assert "a" in names

        assert "b" in names

    def test_items(self):

        registry = ExporterRegistry()

        registry.register(
            "dummy",
            DummyExporter,
        )

        items = list(
            registry.items(),
        )

        assert len(
            items,
        ) == 1

        assert items[0][0] == "dummy"

        assert items[0][1] is DummyExporter

    def test_values(self):

        registry = ExporterRegistry()

        registry.register(
            "dummy",
            DummyExporter,
        )

        values = list(
            registry.values(),
        )

        assert values == [
            DummyExporter,
        ]

    def test_keys(self):

        registry = ExporterRegistry()

        registry.register(
            "dummy",
            DummyExporter,
        )

        keys = list(
            registry.keys(),
        )

        assert keys == [
            "dummy",
        ]

# ==========================================================
# Part 7. TestCreation
# ==========================================================

class TestCreation:

    def test_create(self):

        registry = ExporterRegistry()

        registry.register(
            "dummy",
            DummyExporter,
        )

        exporter = registry.create(
            "dummy",
        )

        assert isinstance(
            exporter,
            DummyExporter,
        )

    def test_create_all(self):

        registry = ExporterRegistry()

        registry.register(
            "a",
            DummyExporter,
        )

        registry.register(
            "b",
            AnotherExporter,
        )

        exporters = registry.create_all()

        assert len(
            exporters,
        ) == 2

        assert isinstance(
            exporters[0],
            (DummyExporter, AnotherExporter),
        )

        assert isinstance(
            exporters[1],
            (DummyExporter, AnotherExporter),
        )


# ==========================================================
# Part 8. TestValidation
# ==========================================================

class TestValidation:

    def test_validate(self):

        registry = ExporterRegistry()

        registry.register(
            "dummy",
            DummyExporter,
        )

        assert registry.validate()

    def test_is_valid(self):

        registry = ExporterRegistry()

        registry.register(
            "dummy",
            DummyExporter,
        )

        assert registry.is_valid()


# ==========================================================
# Part 9. TestPythonProtocols
# ==========================================================

class TestPythonProtocols:

    def test_repr(self):

        registry = ExporterRegistry()

        assert "ExporterRegistry" in repr(
            registry,
        )

    def test_str(self):

        registry = ExporterRegistry()

        assert "ExporterRegistry" in str(
            registry,
        )

    def test_len(self):

        registry = ExporterRegistry()

        registry.register(
            "dummy",
            DummyExporter,
        )

        assert len(
            registry,
        ) == 1

    def test_iter(self):

        registry = ExporterRegistry()

        registry.register(
            "dummy",
            DummyExporter,
        )

        keys = list(
            iter(registry),
        )

        assert "dummy" in keys

    def test_contains(self):

        registry = ExporterRegistry()

        registry.register(
            "dummy",
            DummyExporter,
        )

        assert "dummy" in registry

    def test_getitem(self):

        registry = ExporterRegistry()

        registry.register(
            "dummy",
            DummyExporter,
        )

        assert registry["dummy"] is DummyExporter

    def test_setitem(self):

        registry = ExporterRegistry()

        registry["dummy"] = DummyExporter

        assert registry["dummy"] is DummyExporter

    def test_delitem(self):

        registry = ExporterRegistry()

        registry["dummy"] = DummyExporter

        del registry["dummy"]

        assert "dummy" not in registry

    def test_copy(self):

        registry = ExporterRegistry()

        registry.register(
            "dummy",
            DummyExporter,
        )

        copied = copy.copy(
            registry,
        )

        assert copied == registry

    def test_deepcopy(self):

        registry = ExporterRegistry()

        registry.register(
            "dummy",
            DummyExporter,
        )

        copied = copy.deepcopy(
            registry,
        )

        assert copied == registry

    def test_eq(self):

        a = ExporterRegistry()

        b = ExporterRegistry()

        a.register(
            "dummy",
            DummyExporter,
        )

        b.register(
            "dummy",
            DummyExporter,
        )

        assert a == b

    def test_hash(self):

        registry = ExporterRegistry()

        assert isinstance(
            hash(registry),
            int,
        )

    def test_pickle(self):

        registry = ExporterRegistry()

        registry.register(
            "dummy",
            DummyExporter,
        )

        restored = pickle.loads(
            pickle.dumps(
                registry,
            ),
        )

        assert restored == registry


# ==========================================================
# Part 10. TestAPIFreeze
# ==========================================================

class TestAPIFreeze:

    def test_public_api(self):

        assert "ExporterRegistry" in __all__

    def test_annotations(self):

        assert isinstance(
            ExporterRegistry.__annotations__,
            dict,
        )

    def test_slots(self):

        assert hasattr(
            ExporterRegistry,
            "__slots__",
        )

    def test_signature(self):

        signature = inspect.signature(
            ExporterRegistry,
        )

        assert signature is not None                