"""
SciOS Global Constants
======================

Canonical constants shared across the Scientific Cognitive
Operating System (SciOS).

Design goals
------------
- Python 3.11+
- Zero runtime dependencies
- Stable public values
- Centralized subsystem constants
- Backward-compatible primitive values
- Suitable for runtime and static analysis

This module intentionally contains constants only.  Runtime state,
configuration objects, and behavior belong to their respective
modules.
"""

from __future__ import annotations

from pathlib import Path


# ============================================================================
# Public API
# ============================================================================

__all__ = [
    # System
    "SCIOS_NAME",
    "SCIOS_VERSION",
    "SCIOS_ORGANIZATION",

    # Directories
    "ROOT_DIRECTORY",
    "LOG_DIRECTORY",
    "CACHE_DIRECTORY",
    "DATA_DIRECTORY",
    "MODEL_DIRECTORY",

    # Runtime
    "DEFAULT_WORKERS",
    "DEFAULT_TIMEOUT",
    "DEFAULT_SCHEDULER",

    # Kernel states
    "KERNEL_STATE_CREATED",
    "KERNEL_STATE_BOOTING",
    "KERNEL_STATE_RUNNING",
    "KERNEL_STATE_STOPPING",
    "KERNEL_STATE_STOPPED",
    "KERNEL_STATE_FAILED",

    # Agent states
    "AGENT_IDLE",
    "AGENT_RUNNING",
    "AGENT_WAITING",
    "AGENT_FINISHED",
    "AGENT_FAILED",

    # Memory types
    "MEMORY_WORKING",
    "MEMORY_EPISODIC",
    "MEMORY_SEMANTIC",
    "MEMORY_LONGTERM",

    # Vector store
    "VECTOR_BACKEND_FLAT",
    "VECTOR_BACKEND_HNSW",
    "VECTOR_BACKEND_FAISS",
    "SIMILARITY_COSINE",
    "SIMILARITY_L2",
    "SIMILARITY_INNER_PRODUCT",

    # QTC
    "QTC_BACKEND_NATIVE",
    "QTC_BACKEND_SYMBOLIC",

    # Events
    "EVENT_BOOT",
    "EVENT_SHUTDOWN",
    "EVENT_TASK_STARTED",
    "EVENT_TASK_COMPLETED",
    "EVENT_TASK_FAILED",

    # Logging
    "LOG_DEBUG",
    "LOG_INFO",
    "LOG_WARNING",
    "LOG_ERROR",
    "LOG_CRITICAL",
]


# ============================================================================
# System
# ============================================================================

SCIOS_NAME: str = "SciOS"

SCIOS_VERSION: str = "0.1.3"

SCIOS_ORGANIZATION: str = "SciOS Project"


# ============================================================================
# Directories
# ============================================================================

ROOT_DIRECTORY: Path = Path(".")

LOG_DIRECTORY: Path = Path("logs")

CACHE_DIRECTORY: Path = Path("cache")

DATA_DIRECTORY: Path = Path("data")

MODEL_DIRECTORY: Path = Path("models")


# ============================================================================
# Runtime
# ============================================================================

DEFAULT_WORKERS: int = 4

DEFAULT_TIMEOUT: float = 300.0

DEFAULT_SCHEDULER: str = "fifo"


# ============================================================================
# Kernel States
# ============================================================================

KERNEL_STATE_CREATED: str = "created"

KERNEL_STATE_BOOTING: str = "booting"

KERNEL_STATE_RUNNING: str = "running"

KERNEL_STATE_STOPPING: str = "stopping"

KERNEL_STATE_STOPPED: str = "stopped"

KERNEL_STATE_FAILED: str = "failed"


# ============================================================================
# Agent States
# ============================================================================

AGENT_IDLE: str = "idle"

AGENT_RUNNING: str = "running"

AGENT_WAITING: str = "waiting"

AGENT_FINISHED: str = "finished"

AGENT_FAILED: str = "failed"


# ============================================================================
# Memory Types
# ============================================================================

MEMORY_WORKING: str = "working"

MEMORY_EPISODIC: str = "episodic"

MEMORY_SEMANTIC: str = "semantic"

MEMORY_LONGTERM: str = "longterm"


# ============================================================================
# Vector Store
# ============================================================================

VECTOR_BACKEND_FLAT: str = "flat"

VECTOR_BACKEND_HNSW: str = "hnsw"

VECTOR_BACKEND_FAISS: str = "faiss"

SIMILARITY_COSINE: str = "cosine"

SIMILARITY_L2: str = "l2"

SIMILARITY_INNER_PRODUCT: str = "inner_product"


# ============================================================================
# QTC
# ============================================================================

QTC_BACKEND_NATIVE: str = "native"

QTC_BACKEND_SYMBOLIC: str = "symbolic"


# ============================================================================
# Events
# ============================================================================

EVENT_BOOT: str = "kernel.boot"

EVENT_SHUTDOWN: str = "kernel.shutdown"

EVENT_TASK_STARTED: str = "runtime.task.started"

EVENT_TASK_COMPLETED: str = "runtime.task.completed"

EVENT_TASK_FAILED: str = "runtime.task.failed"


# ============================================================================
# Logging
# ============================================================================

LOG_DEBUG: str = "DEBUG"

LOG_INFO: str = "INFO"

LOG_WARNING: str = "WARNING"

LOG_ERROR: str = "ERROR"

LOG_CRITICAL: str = "CRITICAL"
