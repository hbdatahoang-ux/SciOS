"""
SciOS Serialization Framework
=============================

Unified serialization utilities used throughout the Scientific
Cognitive Operating System (SciOS).

Supported formats
-----------------
- JSON
- YAML
- Pickle

Features
--------
- Automatic directory creation
- UTF-8 support
- Dataclass / object serialization
- to_dict() auto detection
- File and string serialization
- Unified Serializer facade
"""

from __future__ import annotations

import json
import pickle
from dataclasses import asdict
from dataclasses import is_dataclass
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:
    yaml = None


__all__ = [

    "Serializer",

    "save_json",
    "load_json",

    "save_yaml",
    "load_yaml",

    "save_pickle",
    "load_pickle",

    "to_json",
    "from_json",
]


# ==========================================================
# Internal Helpers
# ==========================================================


def _normalize(obj: Any) -> Any:
    """
    Convert supported objects into serializable structures.
    """

    if obj is None:
        return None

    if is_dataclass(obj):
        return asdict(obj)

    if hasattr(obj, "to_dict") and callable(obj.to_dict):
        return obj.to_dict()

    return obj


# ==========================================================
# JSON
# ==========================================================


def save_json(
    data: Any,
    path: str | Path,
    *,
    indent: int = 2,
    sort_keys: bool = False,
    encoding: str = "utf-8",
) -> None:
    """
    Save object to JSON.
    """

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = _normalize(data)

    with path.open(
        "w",
        encoding=encoding,
    ) as f:

        json.dump(
            data,
            f,
            indent=indent,
            ensure_ascii=False,
            sort_keys=sort_keys,
        )


def load_json(
    path: str | Path,
    *,
    encoding: str = "utf-8",
    default: Any = None,
) -> Any:
    """
    Load JSON file.
    """

    path = Path(path)

    if not path.exists():
        return default

    with path.open(
        "r",
        encoding=encoding,
    ) as f:

        return json.load(f)


def to_json(
    data: Any,
    *,
    indent: int = 2,
    sort_keys: bool = False,
) -> str:
    """
    Serialize object into JSON string.
    """

    return json.dumps(
        _normalize(data),
        indent=indent,
        ensure_ascii=False,
        sort_keys=sort_keys,
    )


def from_json(
    text: str,
) -> Any:
    """
    Deserialize JSON string.
    """

    return json.loads(text)


# ==========================================================
# YAML
# ==========================================================


def save_yaml(
    data: Any,
    path: str | Path,
    *,
    encoding: str = "utf-8",
) -> None:
    """
    Save object to YAML.
    """

    if yaml is None:
        raise ImportError(
            "PyYAML is required for YAML serialization."
        )

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    data = _normalize(data)

    with path.open(
        "w",
        encoding=encoding,
    ) as f:

        yaml.safe_dump(
            data,
            f,
            allow_unicode=True,
            sort_keys=False,
        )


def load_yaml(
    path: str | Path,
    *,
    encoding: str = "utf-8",
    default: Any = None,
) -> Any:
    """
    Load YAML file.
    """

    if yaml is None:
        raise ImportError(
            "PyYAML is required for YAML serialization."
        )

    path = Path(path)

    if not path.exists():
        return default

    with path.open(
        "r",
        encoding=encoding,
    ) as f:

        return yaml.safe_load(f)


# ==========================================================
# Pickle
# ==========================================================


def save_pickle(
    obj: Any,
    path: str | Path,
) -> None:
    """
    Save object using pickle.
    """

    path = Path(path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "wb",
    ) as f:

        pickle.dump(
            obj,
            f,
            protocol=pickle.HIGHEST_PROTOCOL,
        )


def load_pickle(
    path: str | Path,
    *,
    default: Any = None,
) -> Any:
    """
    Load pickle file.
    """

    path = Path(path)

    if not path.exists():
        return default

    with path.open(
        "rb",
    ) as f:

        return pickle.load(f)


# ==========================================================
# Serializer Facade
# ==========================================================


class Serializer:
    """
    Unified serialization facade.

    Examples
    --------
    >>> Serializer.save_json(obj, "config.json")
    >>> cfg = Serializer.load_json("config.json")

    >>> text = Serializer.to_json(obj)
    >>> obj = Serializer.from_json(text)
    """

    save_json = staticmethod(save_json)
    load_json = staticmethod(load_json)

    save_yaml = staticmethod(save_yaml)
    load_yaml = staticmethod(load_yaml)

    save_pickle = staticmethod(save_pickle)
    load_pickle = staticmethod(load_pickle)

    to_json = staticmethod(to_json)
    from_json = staticmethod(from_json)