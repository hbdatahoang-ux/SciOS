"""
Public API tests for metric registry.
"""

# ==============================================================================
# Part 1. Imports
# ==============================================================================

from __future__ import annotations

import inspect

import scios.runtime.observability.metrics.core.metrics.registry as registry

from scios.runtime.observability.metrics.core.metrics.registry import __all__


# ==============================================================================
# Part 2. Package Metadata
# ==============================================================================


def test_package_exists():

    assert registry is not None


def test_public_api_exists():

    assert hasattr(
        registry,
        "__all__",
    )


def test_public_api_type():

    assert isinstance(
        __all__,
        (
            list,
            tuple,
        ),
    )


def test_public_api_not_empty():

    assert len(__all__) > 0


# ==============================================================================
# Part 3. Exported Classes
# ==============================================================================


def test_metric_statistics_export():

    assert hasattr(
        registry,
        "MetricStatistics",
    )

    assert "MetricStatistics" in __all__


def test_metric_utils_export():

    assert hasattr(
        registry,
        "MetricUtils",
    )

    assert "MetricUtils" in __all__


def test_exported_classes_are_classes():

    assert inspect.isclass(
        registry.MetricStatistics,
    )

    assert inspect.isclass(
        registry.MetricUtils,
    )


# ==============================================================================
# Part 4. Exported Constants
# ==============================================================================


def test_statistics_constants():

    names = (
        "DEFAULT_NAME",
        "DEFAULT_COUNT",
        "DEFAULT_SUM",
        "DEFAULT_MINIMUM",
        "DEFAULT_MAXIMUM",
        "DEFAULT_AVERAGE",
    )

    for name in names:

        assert hasattr(
            registry,
            name,
        )

        assert name in __all__


def test_utils_constants():

    names = (
        "DEFAULT_ENCODING",
        "DEFAULT_HASH",
        "DEFAULT_INDENT",
    )

    for name in names:

        assert hasattr(
            registry,
            name,
        )

        assert name in __all__


def test_constant_values():

    assert registry.DEFAULT_NAME == ""

    assert registry.DEFAULT_COUNT == 0

    assert registry.DEFAULT_SUM == 0.0

    assert registry.DEFAULT_MINIMUM is None

    assert registry.DEFAULT_MAXIMUM is None

    assert registry.DEFAULT_AVERAGE == 0.0

    assert registry.DEFAULT_ENCODING == "utf-8"

    assert registry.DEFAULT_HASH == "sha256"

    assert registry.DEFAULT_INDENT == 2

# ==============================================================================
# Part 5. Exported Functions
# ==============================================================================


def test_normalization_exports():

    names = (
        "normalize_name",
        "normalize_tags",
        "normalize_labels",
    )

    for name in names:

        assert hasattr(registry, name)
        assert callable(getattr(registry, name))
        assert name in __all__


def test_conversion_exports():

    names = (
        "to_dict",
        "from_dict",
        "to_tuple",
        "from_tuple",
        "to_json",
        "from_json",
    )

    for name in names:

        assert hasattr(registry, name)
        assert callable(getattr(registry, name))
        assert name in __all__


def test_hash_exports():

    names = (
        "compute_hash",
        "stable_hash",
        "object_hash",
        "compare_hash",
    )

    for name in names:

        assert hasattr(registry, name)
        assert callable(getattr(registry, name))
        assert name in __all__


def test_merge_exports():

    names = (
        "merge_dicts",
        "merge_states",
        "merge_labels",
        "merge_tags",
        "merge_statistics",
    )

    for name in names:

        assert hasattr(registry, name)
        assert callable(getattr(registry, name))
        assert name in __all__


def test_validation_exports():

    names = (
        "validate_name",
        "validate_mapping",
        "validate_sequence",
        "validate_number",
        "validate_json",
    )

    for name in names:

        assert hasattr(registry, name)
        assert callable(getattr(registry, name))
        assert name in __all__


def test_diagnostic_exports():

    names = (
        "diagnostics",
        "health",
        "status",
        "summary",
    )

    for name in names:

        assert hasattr(registry, name)
        assert callable(getattr(registry, name))
        assert name in __all__


# ==============================================================================
# Part 6. __all__ Contract
# ==============================================================================


def test_every_export_exists():

    for name in __all__:

        assert hasattr(
            registry,
            name,
        )


def test_every_all_symbol_accessible():

    for name in __all__:

        getattr(
            registry,
            name,
        )


def test_no_duplicate_exports():

    assert len(__all__) == len(set(__all__))


def test_expected_exports_present():

    expected = {
        "MetricStatistics",
        "MetricUtils",
        "DEFAULT_NAME",
        "DEFAULT_COUNT",
        "DEFAULT_SUM",
        "DEFAULT_MINIMUM",
        "DEFAULT_MAXIMUM",
        "DEFAULT_AVERAGE",
        "DEFAULT_ENCODING",
        "DEFAULT_HASH",
        "DEFAULT_INDENT",
        "normalize_name",
        "normalize_tags",
        "normalize_labels",
        "ensure_mapping",
        "ensure_sequence",
        "ensure_number",
        "to_dict",
        "from_dict",
        "to_tuple",
        "from_tuple",
        "to_json",
        "from_json",
        "compute_hash",
        "stable_hash",
        "object_hash",
        "compare_hash",
        "merge_dicts",
        "merge_states",
        "merge_labels",
        "merge_tags",
        "merge_statistics",
        "validate_name",
        "validate_mapping",
        "validate_sequence",
        "validate_number",
        "validate_json",
        "diagnostics",
        "health",
        "status",
        "summary",
    }

    assert expected.issubset(set(__all__))


def test_no_missing_exports():

    missing = [
        name
        for name in __all__
        if not hasattr(registry, name)
    ]

    assert missing == []


def test_all_entries_are_strings():

    assert all(
        isinstance(name, str)
        for name in __all__
    )


# ==============================================================================
# Part 7. Wildcard Import Contract
# ==============================================================================


def test_star_import_contract():

    namespace = {
        name: getattr(registry, name)
        for name in __all__
    }

    assert len(namespace) == len(__all__)


def test_all_symbols_importable():

    for name in __all__:

        assert name in registry.__dict__


def test_package_namespace():

    exported = {
        name
        for name in registry.__dict__
        if not name.startswith("_")
    }

    assert set(__all__).issubset(exported)


# ==============================================================================
# Part 8. API Consistency
# ==============================================================================


def test_class_names():

    assert registry.MetricStatistics.__name__ == "MetricStatistics"
    assert registry.MetricUtils.__name__ == "MetricUtils"


def test_function_names():

    names = (
        "normalize_name",
        "to_dict",
        "compute_hash",
        "merge_dicts",
        "validate_name",
        "diagnostics",
    )

    for name in names:

        assert getattr(
            registry,
            name,
        ).__name__ == name


def test_constant_names():

    constants = (
        "DEFAULT_NAME",
        "DEFAULT_COUNT",
        "DEFAULT_SUM",
        "DEFAULT_MINIMUM",
        "DEFAULT_MAXIMUM",
        "DEFAULT_AVERAGE",
        "DEFAULT_ENCODING",
        "DEFAULT_HASH",
        "DEFAULT_INDENT",
    )

    for name in constants:

        assert hasattr(registry, name)


def test_callable_exports():

    for name in __all__:

        value = getattr(registry, name)

        if inspect.isclass(value):
            continue

        if name.startswith("DEFAULT_"):
            continue

        assert callable(value)


def test_public_api_complete():

    for name in __all__:

        assert hasattr(registry, name)

        getattr(registry, name)


# ==============================================================================
# Part 9. Public API Summary
# ==============================================================================


def test_registry_public_surface():

    assert len(__all__) >= 40


def test_registry_export_count():

    assert len(__all__) == len(set(__all__))


def test_registry_api_stable():

    assert "MetricStatistics" in __all__
    assert "MetricUtils" in __all__
    assert "normalize_name" in __all__
    assert "compute_hash" in __all__
    assert "diagnostics" in __all__    