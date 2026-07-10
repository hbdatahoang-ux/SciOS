"""
SciOS Global Constants
======================

Global constants shared across the Scientific Cognitive Operating System.

This module contains immutable definitions used by every subsystem.

Modules
-------
- System
- Runtime
- Kernel
- Agents
- Memory
- Vector Store
- QTC
- Events
- Logging
"""

from __future__ import annotations

from pathlib import Path

__all__ = [

    # Version
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

    # Kernel
    "KERNEL_STATE_CREATED",
    "KERNEL_STATE_BOOTING",
    "KERNEL_STATE_RUNNING",
    "KERNEL_STATE_STOPPING",
    "KERNEL_STATE_STOPPED",
    "KERNEL_STATE_FAILED",

    # Agent
    "AGENT_IDLE",
    "AGENT_RUNNING",
    "AGENT_WAITING",
    "AGENT_FINISHED",
    "AGENT_FAILED",

    # Memory
    "MEMORY_WORKING",
    "MEMORY_EPISODIC",
    "MEMORY_SEMANTIC",
    "MEMORY_LONGTERM",

    # Vector Store
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


# ==========================================================
# System
# ==========================================================

SCIOS_NAME = "SciOS"

SCIOS_VERSION = "0.1.3"

SCIOS_ORGANIZATION = "SciOS Project"


# ==========================================================
# Directories
# ==========================================================

ROOT_DIRECTORY = Path(".")

LOG_DIRECTORY = Path("logs")

CACHE_DIRECTORY = Path("cache")

DATA_DIRECTORY = Path("data")

MODEL_DIRECTORY = Path("models")


# ==========================================================
# Runtime
# ==========================================================

DEFAULT_WORKERS = 4

DEFAULT_TIMEOUT = 300.0

DEFAULT_SCHEDULER = "fifo"


# ==========================================================
# Kernel States
# ==========================================================

KERNEL_STATE_CREATED = "created"

KERNEL_STATE_BOOTING = "booting"

KERNEL_STATE_RUNNING = "running"

KERNEL_STATE_STOPPING = "stopping"

KERNEL_STATE_STOPPED = "stopped"

KERNEL_STATE_FAILED = "failed"


# ==========================================================
# Agent States
# ==========================================================

AGENT_IDLE = "idle"

AGENT_RUNNING = "running"

AGENT_WAITING = "waiting"

AGENT_FINISHED = "finished"

AGENT_FAILED = "failed"


# ==========================================================
# Memory Types
# ==========================================================

MEMORY_WORKING = "working"

MEMORY_EPISODIC = "episodic"

MEMORY_SEMANTIC = "semantic"

MEMORY_LONGTERM = "longterm"


# ==========================================================
# Vector Store
# ==========================================================

VECTOR_BACKEND_FLAT = "flat"

VECTOR_BACKEND_HNSW = "hnsw"

VECTOR_BACKEND_FAISS = "faiss"

SIMILARITY_COSINE = "cosine"

SIMILARITY_L2 = "l2"

SIMILARITY_INNER_PRODUCT = "inner_product"


# ==========================================================
# QTC
# ==========================================================

QTC_BACKEND_NATIVE = "native"

QTC_BACKEND_SYMBOLIC = "symbolic"


# ==========================================================
# Events
# ==========================================================

EVENT_BOOT = "kernel.boot"

EVENT_SHUTDOWN = "kernel.shutdown"

EVENT_TASK_STARTED = "runtime.task.started"

EVENT_TASK_COMPLETED = "runtime.task.completed"

EVENT_TASK_FAILED = "runtime.task.failed"


# ==========================================================
# Logging
# ==========================================================

LOG_DEBUG = "DEBUG"

LOG_INFO = "INFO"

LOG_WARNING = "WARNING"

LOG_ERROR = "ERROR"

LOG_CRITICAL = "CRITICAL"
