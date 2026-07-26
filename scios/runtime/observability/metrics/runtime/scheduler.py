"""
SciOS-NG Runtime Metrics Scheduler Engine

File:
    scios/runtime/observability/metrics/runtime/scheduler.py

Description
-----------
Runtime scheduler engine responsible for managing,
executing and coordinating Metric jobs.

SciOS-NG v0.2
"""

from __future__ import annotations

from datetime import datetime
from threading import RLock, Condition
from typing import Any
from uuid import uuid4


# ==================================================================
# Part 1. Foundation
# ==================================================================


class MetricScheduler:
    """
    Runtime Metrics Scheduler Engine.

    Responsibilities
    ----------------
    - Metric job scheduling
    - Runtime execution control
    - Periodic task management
    - Job queue orchestration
    - Scheduler lifecycle management
    """


    VERSION = "0.2.0"


    # ==============================================================
    # Constructor
    # ==============================================================

    def __init__(
        self,
        name: str = "MetricScheduler",
        description: str = "",
    ) -> None:
        """
        Initialize Runtime Metrics Scheduler.
        """


        # ----------------------------------------------------------
        # Identity
        # ----------------------------------------------------------

        self._id: str = str(
            uuid4()
        )

        self._name: str = name

        self._description: str = description



        # ----------------------------------------------------------
        # Scheduling
        # ----------------------------------------------------------

        # Ordered scheduled jobs

        self._jobs: list[Any] = []


        # Named job registry

        self._job_registry: dict[str, Any] = {}


        # Runtime execution queue

        self._queue: list[Any] = []


        # Schedule definitions

        self._schedule_registry: dict[str, Any] = {}



        # ----------------------------------------------------------
        # Runtime State
        # ----------------------------------------------------------

        self._enabled: bool = True

        self._frozen: bool = False

        self._closed: bool = False

        self._running: bool = False



        # ----------------------------------------------------------
        # Synchronization
        # ----------------------------------------------------------

        self._lock = RLock()

        self._condition = Condition(
            self._lock
        )



        # ----------------------------------------------------------
        # Metadata
        # ----------------------------------------------------------

        now = datetime.utcnow()

        self._created_at: datetime = now

        self._updated_at: datetime = now

        self._version: str = self.VERSION



        # ----------------------------------------------------------
        # Internal Components
        # ----------------------------------------------------------

        self._statistics: dict[str, Any] = {

            "scheduled_count": 0,

            "executed_count": 0,

            "success_count": 0,

            "failure_count": 0,

            "cancelled_count": 0,

            "total_latency": 0.0,

        }


        self._hooks: dict[str, list[Any]] = {}


        self._events: list[dict[str, Any]] = []


        self._snapshot: dict[str, Any] | None = None


        self._context: dict[str, Any] = {}



    # ==============================================================
    # Internal Utilities
    # ==============================================================

    def _touch(
        self,
    ) -> None:
        """
        Update runtime timestamp.
        """

        self._updated_at = datetime.utcnow()



    def _ensure_writable(
        self,
    ) -> None:
        """
        Validate scheduler state.
        """

        if self._closed:

            raise RuntimeError(
                "MetricScheduler is closed."
            )


        if self._frozen:

            raise RuntimeError(
                "MetricScheduler is frozen."
            )


        if not self._enabled:

            raise RuntimeError(
                "MetricScheduler is disabled."
            )



    def _ensure_active(
        self,
    ) -> None:
        """
        Validate scheduler execution state.
        """

        self._ensure_writable()


        if not self._running:

            raise RuntimeError(
                "MetricScheduler is not running."
            )
# ==================================================================
# Part 2. Scheduling API
# ==================================================================

import time
from datetime import timedelta


# ------------------------------------------------------------------
# Job Scheduling
# ------------------------------------------------------------------

def schedule(
    self,
    name: str,
    job: Any,
    schedule: Any = None,
) -> Any:
    """
    Register a Runtime Metric Job.
    """

    with self._lock:

        self._ensure_writable()

        self._job_registry[name] = {
            "job": job,
            "schedule": schedule,
            "created_at": datetime.utcnow(),
            "last_run": None,
            "status": "scheduled",
        }

        self._jobs.append(
            name
        )

        self._schedule_registry[name] = schedule


        self._statistics[
            "scheduled_count"
        ] += 1


        self._touch()


        return job



def schedule_once(
    self,
    name: str,
    job: Any,
    delay: float = 0,
) -> Any:
    """
    Schedule one-time execution.
    """

    return self.schedule(
        name,
        job,
        {
            "type": "once",
            "delay": delay,
        },
    )



def schedule_periodic(
    self,
    name: str,
    job: Any,
    interval: float,
) -> Any:
    """
    Schedule periodic execution.
    """

    return self.schedule(
        name,
        job,
        {
            "type": "periodic",
            "interval": interval,
        },
    )



def schedule_interval(
    self,
    name: str,
    job: Any,
    seconds: float,
) -> Any:
    """
    Schedule interval execution.
    """

    return self.schedule_periodic(
        name,
        job,
        seconds,
    )



def schedule_cron(
    self,
    name: str,
    job: Any,
    expression: str,
) -> Any:
    """
    Schedule cron-like execution.
    """

    return self.schedule(
        name,
        job,
        {
            "type": "cron",
            "expression": expression,
        },
    )



# ------------------------------------------------------------------
# Job Execution
# ------------------------------------------------------------------

def run(
    self,
    name: str,
    *args,
    **kwargs,
) -> Any:
    """
    Run scheduled job immediately.
    """

    with self._lock:

        self._ensure_writable()


        if name not in self._job_registry:

            raise KeyError(
                f"Unknown job: {name}"
            )


        entry = self._job_registry[name]

        job = entry["job"]


    start = time.perf_counter()


    try:

        self.before_execute(
            name
        )


        result = self.execute(
            job,
            *args,
            **kwargs,
        )


        elapsed = (
            time.perf_counter()
            -
            start
        )


        with self._lock:

            entry["last_run"] = datetime.utcnow()

            entry["status"] = "completed"


            self._statistics[
                "executed_count"
            ] += 1


            self._statistics[
                "success_count"
            ] += 1


            self._statistics[
                "total_latency"
            ] += elapsed


            self._touch()


        self.after_execute(
            name,
            result,
        )


        return result


    except Exception:

        with self._lock:

            self._statistics[
                "failure_count"
            ] += 1


            entry["status"] = "failed"


        raise



def execute(
    self,
    job: Any,
    *args,
    **kwargs,
) -> Any:
    """
    Execute job callable.
    """

    if hasattr(
        job,
        "execute",
    ):

        return job.execute(
            *args,
            **kwargs,
        )


    if callable(job):

        return job(
            *args,
            **kwargs,
        )


    raise TypeError(
        "Job is not executable."
    )



def trigger(
    self,
    name: str,
) -> Any:
    """
    Trigger job execution.
    """

    return self.run(
        name
    )



def cancel(
    self,
    name: str,
) -> Any:
    """
    Cancel scheduled job.
    """

    with self._lock:

        job = self._job_registry.get(
            name
        )


        if job is None:

            return None


        job["status"] = "cancelled"


        self._statistics[
            "cancelled_count"
        ] += 1


        self._touch()


        return job



# ------------------------------------------------------------------
# Batch
# ------------------------------------------------------------------

def schedule_many(
    self,
    jobs: dict[str, Any],
) -> list[Any]:
    """
    Register multiple jobs.
    """

    results = []

    for name, job in jobs.items():

        results.append(
            self.schedule(
                name,
                job,
            )
        )

    return results



def cancel_many(
    self,
    names: list[str],
) -> list[Any]:
    """
    Cancel multiple jobs.
    """

    results = []

    for name in names:

        results.append(
            self.cancel(
                name
            )
        )

    return results



# ------------------------------------------------------------------
# Runtime
# ------------------------------------------------------------------

def update(
    self,
    context: dict[str, Any] | None = None,
) -> "MetricScheduler":
    """
    Update scheduler context.
    """

    with self._lock:

        self._ensure_writable()


        if context:

            self._context.update(
                context
            )


        self._touch()


    return self



def flush(
    self,
) -> "MetricScheduler":
    """
    Flush runtime queue.
    """

    with self._lock:

        self._queue.clear()

        self._touch()


    return self



def reset(
    self,
) -> "MetricScheduler":
    """
    Reset scheduler runtime state.
    """

    with self._lock:

        self._queue.clear()

        self._statistics.update(
            {
                "executed_count": 0,
                "success_count": 0,
                "failure_count": 0,
                "cancelled_count": 0,
            }
        )


        self._touch()


    return self
# ==================================================================
# Part 3. Job Registry API
# ==================================================================


# ------------------------------------------------------------------
# Registration
# ------------------------------------------------------------------

def register_job(
    self,
    name: str,
    job: Any,
    schedule: Any = None,
) -> Any:
    """
    Register Runtime Metric Job.
    """

    with self._lock:

        self._ensure_writable()


        self._job_registry[name] = {

            "job": job,

            "schedule": schedule,

            "created_at": datetime.utcnow(),

            "last_run": None,

            "status": "registered",

        }


        if name not in self._jobs:

            self._jobs.append(
                name
            )


        if schedule is not None:

            self._schedule_registry[name] = schedule


        self._statistics[
            "scheduled_count"
        ] = len(
            self._job_registry
        )


        self._touch()


        return job



def unregister_job(
    self,
    name: str,
) -> Any:
    """
    Remove Runtime Metric Job.
    """

    with self._lock:

        job = self._job_registry.pop(
            name,
            None,
        )


        self._schedule_registry.pop(
            name,
            None,
        )


        if name in self._jobs:

            self._jobs.remove(
                name
            )


        self._touch()


        return job



# ------------------------------------------------------------------
# Lookup
# ------------------------------------------------------------------

def contains_job(
    self,
    name: str,
) -> bool:
    """
    Check job existence.
    """

    return name in self._job_registry



def exists_job(
    self,
    name: str,
) -> bool:
    """
    Alias for contains_job().
    """

    return self.contains_job(
        name
    )



def get_job(
    self,
    name: str,
    default=None,
):
    """
    Get registered job.
    """

    return self._job_registry.get(
        name,
        default,
    )



def find_job(
    self,
    name: str,
):
    """
    Find job or raise error.
    """

    job = self.get_job(
        name
    )


    if job is None:

        raise KeyError(
            f"Unknown job: {name}"
        )


    return job



# ------------------------------------------------------------------
# Enumeration
# ------------------------------------------------------------------

def jobs(
    self,
) -> list[Any]:
    """
    Return registered jobs.
    """

    return list(
        self._job_registry.values()
    )



def keys(
    self,
):
    """
    Return job names.
    """

    return self._job_registry.keys()



def values(
    self,
):
    """
    Return job entries.
    """

    return self._job_registry.values()



def items(
    self,
):
    """
    Return job registry items.
    """

    return self._job_registry.items()



# ------------------------------------------------------------------
# Information
# ------------------------------------------------------------------

def job_count(
    self,
) -> int:
    """
    Number of registered jobs.
    """

    return len(
        self._job_registry
    )



def job_names(
    self,
) -> list[str]:
    """
    Return job names.
    """

    return list(
        self._job_registry.keys()
    )



# ------------------------------------------------------------------
# Maintenance
# ------------------------------------------------------------------

def clear_jobs(
    self,
) -> "MetricScheduler":
    """
    Clear all registered jobs.
    """

    with self._lock:

        self._ensure_writable()


        self._job_registry.clear()

        self._schedule_registry.clear()

        self._jobs.clear()


        self._statistics[
            "scheduled_count"
        ] = 0


        self._touch()


    return self
# ==================================================================
# Part 4. Scheduling Strategy API
# ==================================================================

import asyncio
from concurrent.futures import ThreadPoolExecutor


# ------------------------------------------------------------------
# Built-in Strategies
# ------------------------------------------------------------------

def fifo(
    self,
) -> list[str]:
    """
    First-In First-Out scheduling.
    """

    return list(
        self._jobs
    )



def priority(
    self,
) -> list[str]:
    """
    Priority based scheduling.

    Job priority is read from:
        job["priority"]
    """

    jobs = list(
        self._job_registry.items()
    )


    jobs.sort(
        key=lambda item:
            item[1].get(
                "priority",
                0,
            ),
        reverse=True,
    )


    return [
        name
        for name, _
        in jobs
    ]



def round_robin(
    self,
) -> list[str]:
    """
    Round robin scheduling.
    """

    if not self._jobs:

        return []


    queue = list(
        self._jobs
    )


    first = queue.pop(
        0
    )


    queue.append(
        first
    )


    self._jobs = queue


    return queue



def fair(
    self,
) -> list[str]:
    """
    Fair scheduling based on execution count.
    """

    jobs = list(
        self._job_registry.items()
    )


    jobs.sort(
        key=lambda item:
            item[1].get(
                "executed",
                0,
            )
    )


    return [
        name
        for name, _
        in jobs
    ]



# ------------------------------------------------------------------
# Timing Strategies
# ------------------------------------------------------------------

def delay(
    self,
    seconds: float,
) -> None:
    """
    Delay scheduler execution.
    """

    import time

    time.sleep(
        seconds
    )



def interval(
    self,
    seconds: float,
) -> dict[str, Any]:
    """
    Interval timing strategy.
    """

    return {
        "type": "interval",
        "seconds": seconds,
    }



def periodic(
    self,
    interval: float,
) -> dict[str, Any]:
    """
    Periodic execution strategy.
    """

    return {

        "type": "periodic",

        "interval": interval,

        "enabled": True,

    }



def cron(
    self,
    expression: str,
) -> dict[str, Any]:
    """
    Cron timing strategy.
    """

    return {

        "type": "cron",

        "expression": expression,

    }



# ------------------------------------------------------------------
# Execution Strategies
# ------------------------------------------------------------------

def sync(
    self,
    job: Any,
    *args,
    **kwargs,
):
    """
    Synchronous execution.
    """

    return self.execute(
        job,
        *args,
        **kwargs,
    )



async def async_execute(
    self,
    job: Any,
    *args,
    **kwargs,
):
    """
    Async execution strategy.
    """

    loop = asyncio.get_running_loop()


    return await loop.run_in_executor(
        None,
        lambda:
            self.execute(
                job,
                *args,
                **kwargs,
            )
    )



def parallel(
    self,
    jobs: list[Any],
):
    """
    Parallel execution strategy.
    """

    results = []


    with ThreadPoolExecutor() as executor:

        futures = [

            executor.submit(
                self.execute,
                job,
            )

            for job in jobs

        ]


        for future in futures:

            results.append(
                future.result()
            )


    return results



# ------------------------------------------------------------------
# Strategy Management
# ------------------------------------------------------------------

def register_strategy(
    self,
    name: str,
    strategy: Any,
) -> "MetricScheduler":
    """
    Register custom scheduling strategy.
    """

    if not hasattr(
        self,
        "_strategy_registry",
    ):

        self._strategy_registry = {}


    self._strategy_registry[name] = strategy


    self._touch()


    return self



def remove_strategy(
    self,
    name: str,
) -> Any:
    """
    Remove strategy.
    """

    if not hasattr(
        self,
        "_strategy_registry",
    ):

        return None


    strategy = self._strategy_registry.pop(
        name,
        None,
    )


    self._touch()


    return strategy



def strategy(
    self,
    name: str,
):
    """
    Retrieve strategy.
    """

    builtin = {

        "fifo": self.fifo,

        "priority": self.priority,

        "round_robin": self.round_robin,

        "fair": self.fair,

        "sync": self.sync,

        "parallel": self.parallel,

        "interval": self.interval,

        "periodic": self.periodic,

        "cron": self.cron,

    }


    if name in builtin:

        return builtin[name]


    registry = getattr(
        self,
        "_strategy_registry",
        {},
    )


    if name not in registry:

        raise KeyError(
            f"Unknown strategy: {name}"
        )


    return registry[name]
# ==================================================================
# Part 5. Lifecycle Management
# ==================================================================


# ------------------------------------------------------------------
# Lifecycle
# ------------------------------------------------------------------

def enable(
    self,
) -> "MetricScheduler":
    """
    Enable scheduler.
    """

    with self._lock:

        if self._closed:

            raise RuntimeError(
                "Cannot enable closed scheduler."
            )


        self._enabled = True

        self._touch()


    return self



def disable(
    self,
) -> "MetricScheduler":
    """
    Disable scheduler.
    """

    with self._lock:

        self._enabled = False

        self._running = False

        self._touch()


    return self



def freeze(
    self,
) -> "MetricScheduler":
    """
    Freeze scheduler mutations.
    """

    with self._lock:

        self._frozen = True

        self._running = False

        self._touch()


    return self



def unfreeze(
    self,
) -> "MetricScheduler":
    """
    Unfreeze scheduler.
    """

    with self._lock:

        if self._closed:

            raise RuntimeError(
                "Cannot unfreeze closed scheduler."
            )


        self._frozen = False

        self._touch()


    return self



def close(
    self,
) -> "MetricScheduler":
    """
    Close scheduler permanently.
    """

    with self._lock:

        if self._closed:

            return self


        self._running = False

        self._enabled = False

        self._closed = True


        self._queue.clear()


        self._touch()


    self.after_close()


    return self



def reopen(
    self,
) -> "MetricScheduler":
    """
    Reopen closed scheduler.
    """

    with self._lock:

        self._closed = False

        self._enabled = True

        self._frozen = False

        self._running = False


        self._touch()


    return self



# ------------------------------------------------------------------
# Properties
# ------------------------------------------------------------------

@property
def enabled(
    self,
) -> bool:
    """
    Scheduler enabled state.
    """

    return self._enabled



@property
def disabled(
    self,
) -> bool:
    """
    Scheduler disabled state.
    """

    return not self._enabled



@property
def frozen(
    self,
) -> bool:
    """
    Scheduler frozen state.
    """

    return self._frozen



@property
def closed(
    self,
) -> bool:
    """
    Scheduler closed state.
    """

    return self._closed



@property
def running(
    self,
) -> bool:
    """
    Scheduler running state.
    """

    return self._running



@property
def active(
    self,
) -> bool:
    """
    Scheduler active state.

    Active means:
        enabled
        not frozen
        not closed
        running
    """

    return (
        self._enabled
        and
        not self._frozen
        and
        not self._closed
        and
        self._running
    )
# ==================================================================
# Part 6. Runtime Operations
# ==================================================================

from copy import copy as _copy
from copy import deepcopy


# ------------------------------------------------------------------
# Snapshot
# ------------------------------------------------------------------

def snapshot(
    self,
) -> dict[str, Any]:
    """
    Create scheduler runtime snapshot.
    """

    with self._lock:

        snapshot = {

            "id": self._id,

            "name": self._name,

            "description": self._description,


            "jobs": deepcopy(
                self._jobs
            ),

            "job_registry": deepcopy(
                self._job_registry
            ),

            "queue": deepcopy(
                self._queue
            ),

            "schedule_registry": deepcopy(
                self._schedule_registry
            ),


            "enabled": self._enabled,

            "frozen": self._frozen,

            "closed": self._closed,

            "running": self._running,


            "statistics": deepcopy(
                self._statistics
            ),

            "context": deepcopy(
                self._context
            ),


            "created_at": self._created_at,

            "updated_at": self._updated_at,

            "version": self._version,

        }


        self._snapshot = deepcopy(
            snapshot
        )


        return snapshot



def restore(
    self,
    snapshot: dict[str, Any] | None = None,
) -> "MetricScheduler":
    """
    Restore scheduler state.
    """

    with self._lock:

        data = (
            snapshot
            or self._snapshot
        )


        if data is None:

            raise RuntimeError(
                "No scheduler snapshot available."
            )


        self._id = data["id"]

        self._name = data["name"]

        self._description = data[
            "description"
        ]


        self._jobs = deepcopy(
            data["jobs"]
        )


        self._job_registry = deepcopy(
            data["job_registry"]
        )


        self._queue = deepcopy(
            data["queue"]
        )


        self._schedule_registry = deepcopy(
            data["schedule_registry"]
        )


        self._enabled = data[
            "enabled"
        ]

        self._frozen = data[
            "frozen"
        ]

        self._closed = data[
            "closed"
        ]

        self._running = data[
            "running"
        ]


        self._statistics = deepcopy(
            data["statistics"]
        )


        self._context = deepcopy(
            data["context"]
        )


        self._created_at = data[
            "created_at"
        ]

        self._updated_at = data[
            "updated_at"
        ]

        self._version = data[
            "version"
        ]


        self._touch()


    return self



# ------------------------------------------------------------------
# Object Management
# ------------------------------------------------------------------

def clone(
    self,
) -> "MetricScheduler":
    """
    Deep clone scheduler.
    """

    return deepcopy(
        self
    )



def copy(
    self,
) -> "MetricScheduler":
    """
    Shallow copy scheduler.
    """

    return _copy(
        self
    )



# ------------------------------------------------------------------
# Cleanup
# ------------------------------------------------------------------

def clear(
    self,
) -> "MetricScheduler":
    """
    Clear runtime execution state.
    """

    with self._lock:

        self._ensure_writable()


        self._queue.clear()


        self._context.clear()


        self._events.clear()


        self._touch()


    return self



def compact(
    self,
) -> "MetricScheduler":
    """
    Compact scheduler registries.
    """

    with self._lock:

        self._ensure_writable()


        self._jobs = [

            name

            for name in self._jobs

            if name in self._job_registry

        ]


        self._schedule_registry = {

            name: schedule

            for name, schedule
            in self._schedule_registry.items()

            if name in self._job_registry

        }


        self._touch()


    return self



def cleanup(
    self,
) -> "MetricScheduler":
    """
    Full scheduler cleanup.
    """

    with self._lock:

        self.compact()

        self.clear()


        self._queue.clear()


        self._touch()


    return self
# ==================================================================
# Part 7. Statistics & Diagnostics
# ==================================================================

from datetime import datetime


# ------------------------------------------------------------------
# Runtime Metrics
# ------------------------------------------------------------------

@property
def job_count(
    self,
) -> int:
    """
    Number of registered jobs.
    """

    return len(
        self._job_registry
    )



@property
def scheduled_count(
    self,
) -> int:
    """
    Total scheduled jobs.
    """

    return self._statistics.get(
        "scheduled_count",
        0,
    )



@property
def executed_count(
    self,
) -> int:
    """
    Total executed jobs.
    """

    return self._statistics.get(
        "executed_count",
        0,
    )



@property
def success_count(
    self,
) -> int:
    """
    Successful executions.
    """

    return self._statistics.get(
        "success_count",
        0,
    )



@property
def failure_count(
    self,
) -> int:
    """
    Failed executions.
    """

    return self._statistics.get(
        "failure_count",
        0,
    )



@property
def cancelled_count(
    self,
) -> int:
    """
    Cancelled jobs.
    """

    return self._statistics.get(
        "cancelled_count",
        0,
    )



@property
def latency(
    self,
) -> float:
    """
    Average execution latency.

    Unit:
        seconds
    """

    count = self.executed_count


    if count == 0:

        return 0.0


    return (
        self._statistics.get(
            "total_latency",
            0.0,
        )
        /
        count
    )



@property
def throughput(
    self,
) -> float:
    """
    Scheduler throughput.

    Unit:
        jobs / second
    """

    uptime = self.uptime


    if uptime <= 0:

        return 0.0


    return (
        self.executed_count
        /
        uptime
    )



@property
def uptime(
    self,
) -> float:
    """
    Scheduler uptime.

    Unit:
        seconds
    """

    return (
        datetime.utcnow()
        -
        self._created_at
    ).total_seconds()



# ------------------------------------------------------------------
# Statistics
# ------------------------------------------------------------------

def summary(
    self,
) -> dict[str, Any]:
    """
    Return scheduler summary.
    """

    return {

        "id": self._id,

        "name": self._name,

        "jobs": self.job_count,

        "scheduled": self.scheduled_count,

        "executed": self.executed_count,

        "success": self.success_count,

        "failure": self.failure_count,

        "cancelled": self.cancelled_count,

        "running": self.running,

        "active": self.active,

    }



def statistics(
    self,
) -> dict[str, Any]:
    """
    Detailed scheduler statistics.
    """

    return {

        **self.summary(),

        "latency": self.latency,

        "throughput": self.throughput,

        "uptime": self.uptime,


        "runtime": dict(
            self._statistics
        ),

    }



def report(
    self,
) -> dict[str, Any]:
    """
    Generate scheduler report.
    """

    return {

        "summary": self.summary(),

        "statistics": self.statistics(),

        "status": self.status(),

        "health": self.health(),

        "performance": self.performance(),

    }



# ------------------------------------------------------------------
# Diagnostics
# ------------------------------------------------------------------

def health(
    self,
) -> str:
    """
    Scheduler health state.
    """

    if self.closed:

        return "closed"



    if self.frozen:

        return "frozen"



    if self.disabled:

        return "disabled"



    if self.failure_count > 0:

        return "degraded"



    return "healthy"



def status(
    self,
) -> dict[str, Any]:
    """
    Scheduler runtime status.
    """

    return {

        "health": self.health(),

        "enabled": self.enabled,

        "disabled": self.disabled,

        "frozen": self.frozen,

        "closed": self.closed,

        "running": self.running,

        "active": self.active,

    }



def performance(
    self,
) -> dict[str, Any]:
    """
    Performance metrics.
    """

    return {

        "job_count": self.job_count,

        "executed_count": self.executed_count,

        "success_count": self.success_count,

        "failure_count": self.failure_count,

        "latency": self.latency,

        "throughput": self.throughput,

        "uptime": self.uptime,

    }
# ==================================================================
# Part 8. Serialization
# ==================================================================

import json
import pickle

try:
    import yaml
except ImportError:
    yaml = None


try:
    import msgpack
except ImportError:
    msgpack = None



# ------------------------------------------------------------------
# Serialization
# ------------------------------------------------------------------

def to_dict(
    self,
) -> dict[str, Any]:
    """
    Serialize scheduler state into dictionary.
    """

    return {

        "id": self._id,

        "name": self._name,

        "description": self._description,


        "jobs": self._jobs,

        "job_registry": self._job_registry,

        "queue": self._queue,

        "schedule_registry":
            self._schedule_registry,


        "enabled": self._enabled,

        "frozen": self._frozen,

        "closed": self._closed,

        "running": self._running,


        "statistics":
            self._statistics,


        "context":
            self._context,


        "created_at":
            self._created_at.isoformat(),


        "updated_at":
            self._updated_at.isoformat(),


        "version":
            self._version,

    }



@classmethod
def from_dict(
    cls,
    data: dict[str, Any],
) -> "MetricScheduler":
    """
    Restore scheduler from dictionary.
    """

    scheduler = cls(
        name=data.get(
            "name",
            "MetricScheduler",
        ),
        description=data.get(
            "description",
            "",
        ),
    )


    scheduler._id = data.get(
        "id",
        scheduler._id,
    )


    scheduler._jobs = data.get(
        "jobs",
        [],
    )


    scheduler._job_registry = data.get(
        "job_registry",
        {},
    )


    scheduler._queue = data.get(
        "queue",
        [],
    )


    scheduler._schedule_registry = data.get(
        "schedule_registry",
        {},
    )


    scheduler._enabled = data.get(
        "enabled",
        True,
    )


    scheduler._frozen = data.get(
        "frozen",
        False,
    )


    scheduler._closed = data.get(
        "closed",
        False,
    )


    scheduler._running = data.get(
        "running",
        False,
    )


    scheduler._statistics = data.get(
        "statistics",
        {},
    )


    scheduler._context = data.get(
        "context",
        {},
    )


    scheduler._version = data.get(
        "version",
        cls.VERSION,
    )


    if "created_at" in data:

        scheduler._created_at = datetime.fromisoformat(
            data["created_at"]
        )


    if "updated_at" in data:

        scheduler._updated_at = datetime.fromisoformat(
            data["updated_at"]
        )


    return scheduler



def to_json(
    self,
    **kwargs,
) -> str:
    """
    Serialize scheduler to JSON.
    """

    return json.dumps(
        self.to_dict(),
        default=str,
        **kwargs,
    )



@classmethod
def from_json(
    cls,
    data: str,
) -> "MetricScheduler":
    """
    Restore scheduler from JSON.
    """

    return cls.from_dict(
        json.loads(
            data
        )
    )



def serialize(
    self,
    fmt: str = "json",
):
    """
    Generic serialization.

    Supported:
        json
        yaml
        pickle
        msgpack
    """

    fmt = fmt.lower()


    if fmt == "json":

        return self.to_json(
            indent=2
        )


    if fmt == "yaml":

        if yaml is None:

            raise RuntimeError(
                "PyYAML is not installed."
            )


        return yaml.safe_dump(
            self.to_dict(),
            sort_keys=False,
        )


    if fmt == "pickle":

        return pickle.dumps(
            self.to_dict()
        )


    if fmt == "msgpack":

        if msgpack is None:

            raise RuntimeError(
                "msgpack is not installed."
            )


        return msgpack.packb(
            self.to_dict(),
            use_bin_type=True,
        )


    raise ValueError(
        f"Unsupported format: {fmt}"
    )



@classmethod
def deserialize(
    cls,
    data,
    fmt: str = "json",
) -> "MetricScheduler":
    """
    Deserialize scheduler.
    """

    fmt = fmt.lower()


    if fmt == "json":

        return cls.from_json(
            data
        )


    if fmt == "yaml":

        if yaml is None:

            raise RuntimeError(
                "PyYAML is not installed."
            )


        return cls.from_dict(
            yaml.safe_load(
                data
            )
        )


    if fmt == "pickle":

        return cls.from_dict(
            pickle.loads(
                data
            )
        )


    if fmt == "msgpack":

        if msgpack is None:

            raise RuntimeError(
                "msgpack is not installed."
            )


        return cls.from_dict(
            msgpack.unpackb(
                data,
                raw=False,
            )
        )


    raise ValueError(
        f"Unsupported format: {fmt}"
    )



# ------------------------------------------------------------------
# Import / Export
# ------------------------------------------------------------------

def export(
    self,
    path: str,
    fmt: str = "json",
) -> None:
    """
    Export scheduler state to file.
    """

    data = self.serialize(
        fmt
    )


    binary = fmt.lower() in {
        "pickle",
        "msgpack",
    }


    mode = (
        "wb"
        if binary
        else "w"
    )


    with open(
        path,
        mode,
    ) as file:

        file.write(
            data
        )



@classmethod
def import_data(
    cls,
    path: str,
    fmt: str = "json",
) -> "MetricScheduler":
    """
    Import scheduler state from file.
    """

    binary = fmt.lower() in {
        "pickle",
        "msgpack",
    }


    mode = (
        "rb"
        if binary
        else "r"
    )


    with open(
        path,
        mode,
    ) as file:

        data = file.read()


    return cls.deserialize(
        data,
        fmt,
    )
# ==================================================================
# Part 9. Events & Hooks
# ==================================================================

from uuid import uuid4
from datetime import datetime
from typing import Callable



# ------------------------------------------------------------------
# Scheduler Events
# ------------------------------------------------------------------

def before_schedule(
    self,
    name: str,
    job: Any = None,
) -> None:
    """
    Trigger before_schedule event.
    """

    self.emit(
        "before_schedule",
        name=name,
        job=job,
    )



def after_schedule(
    self,
    name: str,
    job: Any = None,
) -> None:
    """
    Trigger after_schedule event.
    """

    self.emit(
        "after_schedule",
        name=name,
        job=job,
    )



def before_execute(
    self,
    name: str,
) -> None:
    """
    Trigger before_execute event.
    """

    self.emit(
        "before_execute",
        name=name,
    )



def after_execute(
    self,
    name: str,
    result: Any = None,
) -> None:
    """
    Trigger after_execute event.
    """

    self.emit(
        "after_execute",
        name=name,
        result=result,
    )



def before_cancel(
    self,
    name: str,
) -> None:
    """
    Trigger before_cancel event.
    """

    self.emit(
        "before_cancel",
        name=name,
    )



def after_cancel(
    self,
    name: str,
) -> None:
    """
    Trigger after_cancel event.
    """

    self.emit(
        "after_cancel",
        name=name,
    )



def before_flush(
    self,
) -> None:
    """
    Trigger before_flush event.
    """

    self.emit(
        "before_flush"
    )



def after_flush(
    self,
) -> None:
    """
    Trigger after_flush event.
    """

    self.emit(
        "after_flush"
    )



def before_close(
    self,
) -> None:
    """
    Trigger before_close event.
    """

    self.emit(
        "before_close"
    )



def after_close(
    self,
) -> None:
    """
    Trigger after_close event.
    """

    self.emit(
        "after_close"
    )



# ------------------------------------------------------------------
# Hook Management
# ------------------------------------------------------------------

def add_hook(
    self,
    event: str,
    callback: Callable,
) -> "MetricScheduler":
    """
    Add scheduler event hook.
    """

    if event not in self._hooks:

        self._hooks[event] = []


    self._hooks[event].append(
        callback
    )


    return self



def remove_hook(
    self,
    event: str,
    callback: Callable,
) -> "MetricScheduler":
    """
    Remove scheduler hook.
    """

    hooks = self._hooks.get(
        event,
        [],
    )


    if callback in hooks:

        hooks.remove(
            callback
        )


    return self



def clear_hooks(
    self,
    event: str | None = None,
) -> "MetricScheduler":
    """
    Clear scheduler hooks.
    """

    if event is None:

        self._hooks.clear()

    else:

        self._hooks.pop(
            event,
            None,
        )


    return self



# ------------------------------------------------------------------
# Event Dispatcher
# ------------------------------------------------------------------

def emit(
    self,
    event: str,
    **payload,
) -> None:
    """
    Emit scheduler event.
    """

    record = {

        "id": str(
            uuid4()
        ),

        "event": event,

        "timestamp":
            datetime.utcnow(),

        "payload": payload,

    }


    self._events.append(
        record
    )


    self.notify(
        event,
        **payload,
    )



def notify(
    self,
    event: str,
    **payload,
) -> None:
    """
    Notify event subscribers.
    """

    callbacks = self._hooks.get(
        event,
        [],
    )


    for callback in callbacks:

        callback(
            **payload
        )



def subscribe(
    self,
    event: str,
    callback: Callable,
) -> "MetricScheduler":
    """
    Subscribe callback to scheduler event.
    """

    return self.add_hook(
        event,
        callback,
    )



def unsubscribe(
    self,
    event: str,
    callback: Callable,
) -> "MetricScheduler":
    """
    Remove event subscription.
    """

    return self.remove_hook(
        event,
        callback,
    )
# ==================================================================
# Part 10. Python Protocols
# ==================================================================

from copy import copy as _copy
from copy import deepcopy



# ------------------------------------------------------------------
# Representation
# ------------------------------------------------------------------

def __repr__(
    self,
) -> str:
    """
    Developer representation.
    """

    return (
        f"{self.__class__.__name__}("
        f"id={self._id!r}, "
        f"name={self._name!r}, "
        f"jobs={self.job_count}, "
        f"running={self.running}, "
        f"active={self.active}"
        f")"
    )



def __str__(
    self,
) -> str:
    """
    Human readable representation.
    """

    return (
        f"{self._name} "
        f"[jobs={self.job_count}, "
        f"executed={self.executed_count}, "
        f"active={self.active}]"
    )



# ------------------------------------------------------------------
# Container
# ------------------------------------------------------------------

def __len__(
    self,
) -> int:
    """
    Number of scheduled jobs.
    """

    return self.job_count



def __iter__(
    self,
):
    """
    Iterate job registry.
    """

    return iter(
        self._job_registry
    )



def __contains__(
    self,
    name: str,
) -> bool:
    """
    Job existence check.
    """

    return self.contains_job(
        name
    )



# ------------------------------------------------------------------
# Mapping
# ------------------------------------------------------------------

def __getitem__(
    self,
    name: str,
):
    """
    Dictionary style job access.
    """

    return self.get_job(
        name
    )



def __setitem__(
    self,
    name: str,
    job: Any,
) -> None:
    """
    Dictionary style job registration.
    """

    self.register_job(
        name,
        job,
    )



def __delitem__(
    self,
    name: str,
) -> None:
    """
    Dictionary style job removal.
    """

    self.unregister_job(
        name
    )



# ------------------------------------------------------------------
# Context Manager
# ------------------------------------------------------------------

def __enter__(
    self,
) -> "MetricScheduler":
    """
    Enter scheduler context.
    """

    self.enable()

    self._running = True

    return self



def __exit__(
    self,
    exc_type,
    exc_value,
    traceback,
) -> bool:
    """
    Exit scheduler context.
    """

    self.close()

    return False



# ------------------------------------------------------------------
# Callable
# ------------------------------------------------------------------

def __call__(
    self,
    name: str,
    *args,
    **kwargs,
):
    """
    Execute scheduler job by calling instance.
    """

    return self.run(
        name,
        *args,
        **kwargs,
    )



# ------------------------------------------------------------------
# Copy
# ------------------------------------------------------------------

def __copy__(
    self,
):
    """
    Shallow copy protocol.
    """

    return self.copy()



def __deepcopy__(
    self,
    memo,
):
    """
    Deep copy protocol.
    """

    return self.clone()                                            