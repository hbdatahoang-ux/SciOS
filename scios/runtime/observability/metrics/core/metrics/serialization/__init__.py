"""
Metrics Serialization Package
=============================

Public API for metrics serialization layer.

Provides:
- Encoder
- Decoder
- Serializer
- Registry
- Schema

Python 3.11+
"""


from __future__ import annotations


# ==============================================================================
# Encoder
# ==============================================================================

from .encoder import (
    MetricEncoder,
)


# ==============================================================================
# Decoder
# ==============================================================================

from .decoder import (
    Decoder,
    DecoderOptions,
    DecodedValue,
)


# ==============================================================================
# Serializer
# ==============================================================================

from .metric_serializer import (
    MetricSerializer,
)


# ==============================================================================
# Registry
# ==============================================================================

from .registry import (
    Registry,
    DEFAULT_REGISTRY_NAME,
    DEFAULT_CASE_SENSITIVE,
)


# ==============================================================================
# Schema
# ==============================================================================

from .schema import (
    Schema,
    DEFAULT_SCHEMA_NAME,
    DEFAULT_VERSION,
    DEFAULT_STRICT as DEFAULT_SCHEMA_STRICT,
    DEFAULT_ALLOW_EXTRA,
)


# ==============================================================================
# Package Constants
# ==============================================================================

# Backward compatibility:
# DEFAULT_STRICT historically exposed by serialization package.
#
# Keep it mapped to schema strictness because schema validation
# is the canonical strict-mode behavior.
DEFAULT_STRICT = DEFAULT_SCHEMA_STRICT



# ==============================================================================
# Public API
# ==============================================================================

__all__ = [

    # ------------------------------------------------------------------
    # Encoder
    # ------------------------------------------------------------------

    "MetricEncoder",


    # ------------------------------------------------------------------
    # Decoder
    # ------------------------------------------------------------------

    "Decoder",
    "DecoderOptions",
    "DecodedValue",


    # ------------------------------------------------------------------
    # Serializer
    # ------------------------------------------------------------------

    "MetricSerializer",


    # ------------------------------------------------------------------
    # Registry
    # ------------------------------------------------------------------

    "Registry",
    "DEFAULT_REGISTRY_NAME",
    "DEFAULT_CASE_SENSITIVE",


    # ------------------------------------------------------------------
    # Schema
    # ------------------------------------------------------------------

    "Schema",
    "DEFAULT_SCHEMA_NAME",
    "DEFAULT_VERSION",
    "DEFAULT_SCHEMA_STRICT",
    "DEFAULT_ALLOW_EXTRA",


    # ------------------------------------------------------------------
    # Compatibility Constants
    # ------------------------------------------------------------------

    "DEFAULT_STRICT",
]