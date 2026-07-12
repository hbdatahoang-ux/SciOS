"""
SciOS Event Topics
==================

Canonical event topic definitions for the SciOS Kernel.

Responsibilities
----------------
- Centralize all event topic names.
- Avoid hard-coded strings.
- Enable IDE autocompletion.
- Provide hierarchical topic organization.

Naming Convention
-----------------
domain.action

Examples
--------
kernel.boot
runtime.started
task.completed
agent.finished
memory.updated
"""

from __future__ import annotations

__all__ = [
    # Kernel
    "KERNEL_BOOT",
    "KERNEL_READY",
    "KERNEL_SHUTDOWN",
    "KERNEL_FAILED",

    # Lifecycle
    "LIFECYCLE_INITIALIZED",
    "LIFECYCLE_STARTED",
    "LIFECYCLE_STOPPED",

    # Runtime
    "RUNTIME_CREATED",
    "RUNTIME_STARTED",
    "RUNTIME_COMPLETED",
    "RUNTIME_FAILED",

    # Tasks
    "TASK_CREATED",
    "TASK_QUEUED",
    "TASK_DISPATCHED",
    "TASK_STARTED",
    "TASK_COMPLETED",
    "TASK_FAILED",

    # Scheduler
    "SCHEDULER_ENQUEUE",
    "SCHEDULER_DEQUEUE",
    "SCHEDULER_EMPTY",

    # Dispatcher
    "DISPATCHER_STARTED",
    "DISPATCHER_FINISHED",

    # Pipeline
    "PIPELINE_STARTED",
    "PIPELINE_STAGE_STARTED",
    "PIPELINE_STAGE_COMPLETED",
    "PIPELINE_COMPLETED",
    "PIPELINE_FAILED",

    # Planner
    "PLANNER_STARTED",
    "PLANNER_COMPLETED",

    # Agent
    "AGENT_CREATED",
    "AGENT_STARTED",
    "AGENT_FINISHED",
    "AGENT_FAILED",

    # Memory
    "MEMORY_READ",
    "MEMORY_WRITE",
    "MEMORY_UPDATED",

    # Plugins
    "PLUGIN_REGISTERED",
    "PLUGIN_ENABLED",
    "PLUGIN_DISABLED",
    "PLUGIN_UNREGISTERED",

    # Services
    "SERVICE_REGISTERED",
    "SERVICE_UNREGISTERED",

    # Artifacts
    "ARTIFACT_CREATED",
    "ARTIFACT_SAVED",
    "ARTIFACT_REMOVED",

    # System
    "SYSTEM_INFO",
    "SYSTEM_WARNING",
    "SYSTEM_ERROR",

    # Utilities
    "ALL_TOPICS",
]


# ==========================================================
# Kernel
# ==========================================================

KERNEL_BOOT = "kernel.boot"

KERNEL_READY = "kernel.ready"

KERNEL_SHUTDOWN = "kernel.shutdown"

KERNEL_FAILED = "kernel.failed"


# ==========================================================
# Lifecycle
# ==========================================================

LIFECYCLE_INITIALIZED = "lifecycle.initialized"

LIFECYCLE_STARTED = "lifecycle.started"

LIFECYCLE_STOPPED = "lifecycle.stopped"


# ==========================================================
# Runtime
# ==========================================================

RUNTIME_CREATED = "runtime.created"

RUNTIME_STARTED = "runtime.started"

RUNTIME_COMPLETED = "runtime.completed"

RUNTIME_FAILED = "runtime.failed"


# ==========================================================
# Task
# ==========================================================

TASK_CREATED = "task.created"

TASK_QUEUED = "task.queued"

TASK_DISPATCHED = "task.dispatched"

TASK_STARTED = "task.started"

TASK_COMPLETED = "task.completed"

TASK_FAILED = "task.failed"


# ==========================================================
# Scheduler
# ==========================================================

SCHEDULER_ENQUEUE = "scheduler.enqueue"

SCHEDULER_DEQUEUE = "scheduler.dequeue"

SCHEDULER_EMPTY = "scheduler.empty"


# ==========================================================
# Dispatcher
# ==========================================================

DISPATCHER_STARTED = "dispatcher.started"

DISPATCHER_FINISHED = "dispatcher.finished"


# ==========================================================
# Pipeline
# ==========================================================

PIPELINE_STARTED = "pipeline.started"

PIPELINE_STAGE_STARTED = "pipeline.stage.started"

PIPELINE_STAGE_COMPLETED = "pipeline.stage.completed"

PIPELINE_COMPLETED = "pipeline.completed"

PIPELINE_FAILED = "pipeline.failed"


# ==========================================================
# Planner
# ==========================================================

PLANNER_STARTED = "planner.started"

PLANNER_COMPLETED = "planner.completed"


# ==========================================================
# Agent
# ==========================================================

AGENT_CREATED = "agent.created"

AGENT_STARTED = "agent.started"

AGENT_FINISHED = "agent.finished"

AGENT_FAILED = "agent.failed"


# ==========================================================
# Memory
# ==========================================================

MEMORY_READ = "memory.read"

MEMORY_WRITE = "memory.write"

MEMORY_UPDATED = "memory.updated"


# ==========================================================
# Plugins
# ==========================================================

PLUGIN_REGISTERED = "plugin.registered"

PLUGIN_ENABLED = "plugin.enabled"

PLUGIN_DISABLED = "plugin.disabled"

PLUGIN_UNREGISTERED = "plugin.unregistered"


# ==========================================================
# Services
# ==========================================================

SERVICE_REGISTERED = "service.registered"

SERVICE_UNREGISTERED = "service.unregistered"


# ==========================================================
# Artifacts
# ==========================================================

ARTIFACT_CREATED = "artifact.created"

ARTIFACT_SAVED = "artifact.saved"

ARTIFACT_REMOVED = "artifact.removed"


# ==========================================================
# System
# ==========================================================

SYSTEM_INFO = "system.info"

SYSTEM_WARNING = "system.warning"

SYSTEM_ERROR = "system.error"


# ==========================================================
# Collection
# ==========================================================

ALL_TOPICS = (
    KERNEL_BOOT,
    KERNEL_READY,
    KERNEL_SHUTDOWN,
    KERNEL_FAILED,
    LIFECYCLE_INITIALIZED,
    LIFECYCLE_STARTED,
    LIFECYCLE_STOPPED,
    RUNTIME_CREATED,
    RUNTIME_STARTED,
    RUNTIME_COMPLETED,
    RUNTIME_FAILED,
    TASK_CREATED,
    TASK_QUEUED,
    TASK_DISPATCHED,
    TASK_STARTED,
    TASK_COMPLETED,
    TASK_FAILED,
    SCHEDULER_ENQUEUE,
    SCHEDULER_DEQUEUE,
    SCHEDULER_EMPTY,
    DISPATCHER_STARTED,
    DISPATCHER_FINISHED,
    PIPELINE_STARTED,
    PIPELINE_STAGE_STARTED,
    PIPELINE_STAGE_COMPLETED,
    PIPELINE_COMPLETED,
    PIPELINE_FAILED,
    PLANNER_STARTED,
    PLANNER_COMPLETED,
    AGENT_CREATED,
    AGENT_STARTED,
    AGENT_FINISHED,
    AGENT_FAILED,
    MEMORY_READ,
    MEMORY_WRITE,
    MEMORY_UPDATED,
    PLUGIN_REGISTERED,
    PLUGIN_ENABLED,
    PLUGIN_DISABLED,
    PLUGIN_UNREGISTERED,
    SERVICE_REGISTERED,
    SERVICE_UNREGISTERED,
    ARTIFACT_CREATED,
    ARTIFACT_SAVED,
    ARTIFACT_REMOVED,
    SYSTEM_INFO,
    SYSTEM_WARNING,
    SYSTEM_ERROR,
)