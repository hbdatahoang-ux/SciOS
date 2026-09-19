"""
Tests for MetricMetadata.
"""

from __future__ import annotations

# ==============================================================================
# Part 1. Imports
# ==============================================================================

import pytest

from scios.runtime.observability.metrics.core.metadata import (
    MetricMetadata,
)


# ==============================================================================
# Part 2. Construction
# ==============================================================================


def test_default_metadata():
    meta = MetricMetadata()

    assert isinstance(meta, MetricMetadata)
    assert meta.annotations == {}
    assert meta.tags == set()


def test_custom_annotations():
    meta = MetricMetadata(
        annotations={
            "owner": "team-a",
            "env": "prod",
        }
    )

    assert meta.annotations["owner"] == "team-a"
    assert meta.annotations["env"] == "prod"


def test_custom_tags():
    meta = MetricMetadata(
        tags={"cpu", "system", "runtime"}
    )

    assert meta.tags == {
        "cpu",
        "system",
        "runtime",
    }


# ==============================================================================
# Part 3. Defaults
# ==============================================================================


def test_empty_annotations():
    meta = MetricMetadata()

    assert meta.annotations == {}
    assert len(meta.annotations) == 0


def test_empty_tags():
    meta = MetricMetadata()

    assert meta.tags == set()
    assert len(meta.tags) == 0


# ==============================================================================
# Part 4. Validation
# ==============================================================================


def test_invalid_annotations():
    with pytest.raises(TypeError):
        MetricMetadata(
            annotations=["invalid"]
        )


def test_invalid_tags():
    with pytest.raises(TypeError):
        MetricMetadata(
            tags="invalid"
        )


# ==============================================================================
# Part 5. Properties
# ==============================================================================


def test_annotations():
    meta = MetricMetadata(
        annotations={
            "version": "1.0",
        }
    )

    assert meta.annotations == {
        "version": "1.0",
    }


def test_tags():
    meta = MetricMetadata(
        tags={"core"}
    )

    assert meta.tags == {"core"}

# ==============================================================================
# Part 6. Annotation Operations
# ==============================================================================


def test_add_annotation():
    meta = MetricMetadata()

    meta.add_annotation("owner", "runtime")

    assert meta.annotations["owner"] == "runtime"


def test_replace_annotation():
    meta = MetricMetadata()

    meta.add_annotation("owner", "core")
    meta.add_annotation("owner", "runtime")

    assert meta.annotations["owner"] == "runtime"


def test_remove_annotation():
    meta = MetricMetadata(
        annotations={"owner": "runtime"}
    )

    meta.remove_annotation("owner")

    assert "owner" not in meta.annotations


def test_has_annotation():
    meta = MetricMetadata(
        annotations={"team": "AI"}
    )

    assert meta.has_annotation("team")
    assert not meta.has_annotation("missing")


def test_get_annotation():
    meta = MetricMetadata(
        annotations={"env": "prod"}
    )

    assert meta.get_annotation("env") == "prod"
    assert meta.get_annotation("missing") is None
    assert meta.get_annotation("missing", "dev") == "dev"


def test_clear_annotations():
    meta = MetricMetadata(
        annotations={
            "a": 1,
            "b": 2,
        }
    )

    meta.clear_annotations()

    assert meta.annotations == {}


# ==============================================================================
# Part 7. Tag Operations
# ==============================================================================


def test_add_tag():
    meta = MetricMetadata()

    meta.add_tag("runtime")

    assert "runtime" in meta.tags


def test_remove_tag():
    meta = MetricMetadata(
        tags={"runtime"}
    )

    meta.remove_tag("runtime")

    assert "runtime" not in meta.tags


def test_has_tag():
    meta = MetricMetadata(
        tags={"metrics"}
    )

    assert meta.has_tag("metrics")
    assert not meta.has_tag("logging")


def test_clear_tags():
    meta = MetricMetadata(
        tags={
            "a",
            "b",
        }
    )

    meta.clear_tags()

    assert meta.tags == set()


# ==============================================================================
# Part 8. Serialization
# ==============================================================================


def test_to_dict():
    meta = MetricMetadata(
        annotations={"owner": "runtime"},
        tags={"core"},
    )

    data = meta.to_dict()

    assert data["annotations"]["owner"] == "runtime"
    assert "core" in data["tags"]


def test_from_dict():
    data = {
        "annotations": {
            "owner": "runtime",
        },
        "tags": [
            "core",
        ],
    }

    meta = MetricMetadata.from_dict(data)

    assert meta.annotations["owner"] == "runtime"
    assert "core" in meta.tags


def test_to_json():
    meta = MetricMetadata(
        annotations={"a": 1},
        tags={"core"},
    )

    text = meta.to_json()

    assert isinstance(text, str)
    assert '"annotations"' in text


def test_from_json():
    text = (
        '{"annotations":{"owner":"runtime"},'
        '"tags":["core"]}'
    )

    meta = MetricMetadata.from_json(text)

    assert meta.annotations["owner"] == "runtime"
    assert "core" in meta.tags


# ==============================================================================
# Part 9. Copy
# ==============================================================================


def test_copy():
    meta = MetricMetadata(
        annotations={"a": 1},
        tags={"core"},
    )

    copied = meta.copy()

    assert copied == meta
    assert copied is not meta


def test_clone():
    meta = MetricMetadata(
        annotations={"a": 1},
        tags={"core"},
    )

    cloned = meta.clone()

    assert cloned == meta
    assert cloned is not meta


# ==============================================================================
# Part 10. Equality
# ==============================================================================


def test_eq():
    a = MetricMetadata(
        annotations={"a": 1},
        tags={"core"},
    )

    b = MetricMetadata(
        annotations={"a": 1},
        tags={"core"},
    )

    assert a == b


def test_hash():
    meta = MetricMetadata(
        annotations={"a": 1},
        tags={"core"},
    )

    assert isinstance(hash(meta), int)


# ==============================================================================
# Part 11. Representation
# ==============================================================================


def test_repr():
    meta = MetricMetadata()

    assert "MetricMetadata" in repr(meta)


def test_str():
    meta = MetricMetadata()

    assert "MetricMetadata" in str(meta)


# ==============================================================================
# Part 12. Public API
# ==============================================================================


def test_all():
    from scios.runtime.observability.metrics.core.metadata import __all__

    assert "MetricMetadata" in __all__


def test_version():
    from scios.runtime.observability.metrics.core import metadata

    assert hasattr(metadata, "__version__")


# ==============================================================================
# Part 13. Regression
# ==============================================================================


def test_annotations_are_copied():
    annotations = {"owner": "runtime"}

    meta = MetricMetadata(
        annotations=annotations,
    )

    annotations["owner"] = "changed"

    assert meta.annotations["owner"] == "runtime"


def test_tags_are_unique():
    meta = MetricMetadata()

    meta.add_tag("runtime")
    meta.add_tag("runtime")
    meta.add_tag("runtime")

    assert len(meta.tags) == 1


def test_json_roundtrip():
    original = MetricMetadata(
        annotations={"owner": "runtime"},
        tags={"core"},
    )

    restored = MetricMetadata.from_json(
        original.to_json()
    )

    assert restored == original


def test_dict_roundtrip():
    original = MetricMetadata(
        annotations={"owner": "runtime"},
        tags={"core"},
    )

    restored = MetricMetadata.from_dict(
        original.to_dict()
    )

    assert restored == original    