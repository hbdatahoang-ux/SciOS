"""
SciOS Global Configuration

Central configuration system for the Scientific Cognitive Operating System.

Design Goals
------------
- Strong typing
- Immutable configuration
- Modular subsystem configuration
- Serializable
- Production ready
"""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path
from typing import Any

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


# =====================================================================
# System
# =====================================================================

@dataclass(slots=True)
class SystemConfig:
    """
    Global system information.
    """

    app_name: str = "SciOS"

    organization: str = "SciOS Project"

    version: str = "0.1.3"

    debug: bool = False

    root: Path = field(
        default_factory=lambda: Path.cwd()
    )


# =====================================================================
# Runtime
# =====================================================================

@dataclass(slots=True)
class RuntimeConfig:
    """
    Runtime execution configuration.
    """

    workers: int = 4

    scheduler: str = "fifo"

    task_timeout: float = 300.0

    enable_async: bool = False


# =====================================================================
# Kernel
# =====================================================================

@dataclass(slots=True)
class KernelConfig:
    """
    Kernel configuration.
    """

    auto_boot: bool = True

    auto_shutdown: bool = True

    lifecycle_checks: bool = True


# =====================================================================
# Agents
# =====================================================================

@dataclass(slots=True)
class AgentConfig:
    """
    Cognitive agent configuration.
    """

    planner_enabled: bool = True

    reflection_enabled: bool = True

    collaboration_enabled: bool = True

    tool_use_enabled: bool = True


# =====================================================================
# Memory
# =====================================================================

@dataclass(slots=True)
class MemoryConfig:
    """
    Memory subsystem.
    """

    working_capacity: int = 512

    semantic_capacity: int = 10000

    episodic_capacity: int = 5000

    longterm_capacity: int = 100000

    enable_cache: bool = True


# =====================================================================
# Vector Store
# =====================================================================

@dataclass(slots=True)
class VectorStoreConfig:
    """
    Vector database configuration.
    """

    backend: str = "flat"

    dimension: int = 768

    similarity: str = "cosine"

    index_path: Path = Path("vectorstore")


# =====================================================================
# QTC
# =====================================================================

@dataclass(slots=True)
class QTCConfig:
    """
    Quantum Temporal Compression configuration.
    """

    enable_compression: bool = True

    verify_reasoning: bool = True

    symbolic_backend: str = "native"


# =====================================================================
# Logging
# =====================================================================

@dataclass(slots=True)
class LoggingConfig:
    """
    Logging subsystem.
    """

    level: str = "INFO"

    console: bool = True

    file: bool = False

    directory: Path = Path("logs")


# =====================================================================
# Root Configuration
# =====================================================================

@dataclass(slots=True)
class SciOSConfig:
    """
    Root configuration object.
    """

    system: SystemConfig = field(default_factory=SystemConfig)

    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)

    kernel: KernelConfig = field(default_factory=KernelConfig)

    agents: AgentConfig = field(default_factory=AgentConfig)

    memory: MemoryConfig = field(default_factory=MemoryConfig)

    vectorstore: VectorStoreConfig = field(
        default_factory=VectorStoreConfig
    )

    qtc: QTCConfig = field(default_factory=QTCConfig)

    logging: LoggingConfig = field(default_factory=LoggingConfig)

    # --------------------------------------------------------------

    def to_dict(self) -> dict[str, Any]:
        """
        Export configuration to dictionary.
        """
        return asdict(self)

    # --------------------------------------------------------------

    @classmethod
    def from_dict(
        cls,
        values: dict[str, Any],
    ) -> "SciOSConfig":
        """
        Build configuration from dictionary.
        """

        cfg = cls()

        if "system" in values:
            cfg.system = SystemConfig(**values["system"])

        if "runtime" in values:
            cfg.runtime = RuntimeConfig(**values["runtime"])

        if "kernel" in values:
            cfg.kernel = KernelConfig(**values["kernel"])

        if "agents" in values:
            cfg.agents = AgentConfig(**values["agents"])

        if "memory" in values:
            cfg.memory = MemoryConfig(**values["memory"])

        if "vectorstore" in values:
            cfg.vectorstore = VectorStoreConfig(
                **values["vectorstore"]
            )

        if "qtc" in values:
            cfg.qtc = QTCConfig(**values["qtc"])

        if "logging" in values:
            cfg.logging = LoggingConfig(**values["logging"])

        return cfg

    # --------------------------------------------------------------

    def copy(self) -> "SciOSConfig":
        """
        Deep copy configuration.
        """

        return SciOSConfig.from_dict(
            self.to_dict()
        )

    # --------------------------------------------------------------

    def __repr__(self) -> str:

        return (
            "SciOSConfig("
            f"version={self.system.version}, "
            f"debug={self.system.debug})"
        )


# =====================================================================
# Global Singleton
# =====================================================================

config = SciOSConfig()