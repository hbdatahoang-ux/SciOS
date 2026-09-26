"""
SciOS Global Configuration
==========================

Central configuration system for the Scientific Cognitive Operating
System (SciOS).

Design Goals
------------
- Python 3.11+
- Strong typing
- Explicit subsystem configuration
- Safe default factories
- Serializable configuration
- Deep-copy support
- Stable public API
- Zero runtime dependencies

Notes
-----
Configuration objects are intentionally mutable at runtime so that
applications can construct and reconfigure SciOS programmatically.

Use ``to_dict()`` for a JSON-compatible representation.
Use ``from_dict()`` to reconstruct a configuration object.
"""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    "SystemConfig",
    "RuntimeConfig",
    "KernelConfig",
    "AgentConfig",
    "MemoryConfig",
    "VectorStoreConfig",
    "QTCConfig",
    "LoggingConfig",
    "SciOSConfig",
    "config",
]


# ============================================================================
# System Configuration
# ============================================================================


@dataclass(slots=True)
class SystemConfig:
    """
    Global SciOS system information.
    """

    app_name: str = "SciOS"
    organization: str = "SciOS Project"
    version: str = "0.1.3"
    debug: bool = False
    root: Path = field(default_factory=Path.cwd)


# ============================================================================
# Runtime Configuration
# ============================================================================


@dataclass(slots=True)
class RuntimeConfig:
    """
    Runtime execution configuration.
    """

    workers: int = 4
    scheduler: str = "fifo"
    task_timeout: float = 300.0
    enable_async: bool = False


# ============================================================================
# Kernel Configuration
# ============================================================================


@dataclass(slots=True)
class KernelConfig:
    """
    SciOS kernel lifecycle configuration.
    """

    auto_boot: bool = True
    auto_shutdown: bool = True
    lifecycle_checks: bool = True


# ============================================================================
# Agent Configuration
# ============================================================================


@dataclass(slots=True)
class AgentConfig:
    """
    Cognitive agent configuration.
    """

    planner_enabled: bool = True
    reflection_enabled: bool = True
    collaboration_enabled: bool = True
    tool_use_enabled: bool = True


# ============================================================================
# Memory Configuration
# ============================================================================


@dataclass(slots=True)
class MemoryConfig:
    """
    Memory subsystem configuration.
    """

    working_capacity: int = 512
    semantic_capacity: int = 10_000
    episodic_capacity: int = 5_000
    longterm_capacity: int = 100_000
    enable_cache: bool = True


# ============================================================================
# Vector Store Configuration
# ============================================================================


@dataclass(slots=True)
class VectorStoreConfig:
    """
    Vector store configuration.
    """

    backend: str = "flat"
    dimension: int = 768
    similarity: str = "cosine"
    index_path: Path = field(
        default_factory=lambda: Path("vectorstore")
    )


# ============================================================================
# QTC Configuration
# ============================================================================


@dataclass(slots=True)
class QTCConfig:
    """
    Quantum Temporal Compression configuration.
    """

    enable_compression: bool = True
    verify_reasoning: bool = True
    symbolic_backend: str = "native"


# ============================================================================
# Logging Configuration
# ============================================================================


@dataclass(slots=True)
class LoggingConfig:
    """
    SciOS logging configuration.
    """

    level: str = "INFO"
    console: bool = True
    file: bool = False
    directory: Path = field(
        default_factory=lambda: Path("logs")
    )


# ============================================================================
# Root Configuration
# ============================================================================


@dataclass(slots=True)
class SciOSConfig:
    """
    Root configuration object for the SciOS platform.
    """

    system: SystemConfig = field(
        default_factory=SystemConfig
    )

    runtime: RuntimeConfig = field(
        default_factory=RuntimeConfig
    )

    kernel: KernelConfig = field(
        default_factory=KernelConfig
    )

    agents: AgentConfig = field(
        default_factory=AgentConfig
    )

    memory: MemoryConfig = field(
        default_factory=MemoryConfig
    )

    vectorstore: VectorStoreConfig = field(
        default_factory=VectorStoreConfig
    )

    qtc: QTCConfig = field(
        default_factory=QTCConfig
    )

    logging: LoggingConfig = field(
        default_factory=LoggingConfig
    )

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Export the configuration as a plain dictionary.

        ``Path`` values are converted to strings so the resulting
        structure can be safely passed to JSON serializers.
        """

        values = asdict(self)

        return _serialize_paths(values)

    # ------------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        values: dict[str, Any],
    ) -> SciOSConfig:
        """
        Construct a configuration from a dictionary.

        Missing sections use their default configuration.
        """

        if not isinstance(values, dict):
            raise TypeError(
                "values must be a dictionary"
            )

        cfg = cls()

        if "system" in values:
            cfg.system = SystemConfig(
                **dict(values["system"])
            )

        if "runtime" in values:
            cfg.runtime = RuntimeConfig(
                **dict(values["runtime"])
            )

        if "kernel" in values:
            cfg.kernel = KernelConfig(
                **dict(values["kernel"])
            )

        if "agents" in values:
            cfg.agents = AgentConfig(
                **dict(values["agents"])
            )

        if "memory" in values:
            cfg.memory = MemoryConfig(
                **dict(values["memory"])
            )

        if "vectorstore" in values:
            vectorstore = dict(values["vectorstore"])

            if "index_path" in vectorstore:
                vectorstore["index_path"] = Path(
                    vectorstore["index_path"]
                )

            cfg.vectorstore = VectorStoreConfig(
                **vectorstore
            )

        if "qtc" in values:
            cfg.qtc = QTCConfig(
                **dict(values["qtc"])
            )

        if "logging" in values:
            logging_config = dict(values["logging"])

            if "directory" in logging_config:
                logging_config["directory"] = Path(
                    logging_config["directory"]
                )

            cfg.logging = LoggingConfig(
                **logging_config
            )

        if "system" in values:
            system = dict(values["system"])

            if "root" in system:
                system["root"] = Path(system["root"])

            cfg.system = SystemConfig(**system)

        return cfg

    # ------------------------------------------------------------------

    def copy(self) -> SciOSConfig:
        """
        Return an independent copy of the configuration.

        The returned configuration does not share nested configuration
        objects with the original.
        """

        return type(self).from_dict(
            self.to_dict()
        )

    # ------------------------------------------------------------------

    def __repr__(self) -> str:
        """
        Return a concise diagnostic representation.
        """

        return (
            "SciOSConfig("
            f"version={self.system.version!r}, "
            f"debug={self.system.debug!r}"
            ")"
        )


# ============================================================================
# Internal Serialization Helpers
# ============================================================================


def _serialize_paths(
    value: Any,
) -> Any:
    """
    Recursively convert ``Path`` objects to strings.

    Dictionaries, lists, tuples, and nested structures are traversed.
    """

    if isinstance(value, Path):
        return str(value)

    if isinstance(value, dict):
        return {
            key: _serialize_paths(item)
            for key, item in value.items()
        }

    if isinstance(value, list):
        return [
            _serialize_paths(item)
            for item in value
        ]

    if isinstance(value, tuple):
        return tuple(
            _serialize_paths(item)
            for item in value
        )

    return value


# ============================================================================
# Global Configuration
# ============================================================================

config = SciOSConfig()