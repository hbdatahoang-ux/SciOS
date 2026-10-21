"""
SciOS-NG Metrics Monitor
========================

Runtime monitoring layer for Metrics subsystem.

Responsibilities:
- evaluate collected metrics
- maintain health state
- execute monitoring rules
- trigger monitoring hooks

Does NOT:
- create metrics
- store metrics
- collect raw metrics
- export metrics
"""

from __future__ import annotations

from threading import RLock
from time import time
from typing import Final, Any

from ..collector.metric_collector import MetricCollector


__all__ = [
    "MetricMonitor",
]


class MetricMonitor:
    """
    Thread-safe runtime metric monitor.

    The monitor consumes data from MetricCollector
    and performs evaluation.
    """

    DEFAULT_NAME: Final[str] = "monitor"


    # ======================================================
    # Constructor
    # ======================================================

    def __init__(
        self,
        collector: MetricCollector,
        *,
        name: str = DEFAULT_NAME,
    ) -> None:

        # --------------------------------------------------
        # Identity
        # --------------------------------------------------

        self._name = name


        # --------------------------------------------------
        # Dependency
        # --------------------------------------------------

        self._collector = collector


        # --------------------------------------------------
        # Runtime State
        # --------------------------------------------------

        self._enabled = True

        self._timestamp = 0.0

        self._evaluation_count = 0

        self._last_duration = 0.0


        # --------------------------------------------------
        # Monitoring State
        # --------------------------------------------------

        self._last_result = None

        self._health = "idle"


        # --------------------------------------------------
        # Rule Storage
        # --------------------------------------------------

        self._rules: dict[str, Any] = {}


        # --------------------------------------------------
        # Hook Storage
        # --------------------------------------------------

        self._hooks: dict[str, list] = {}


        # --------------------------------------------------
        # Thread Safety
        # --------------------------------------------------

        self._lock = RLock()



    # ======================================================
    # Basic Properties
    # ======================================================

    @property
    def name(self) -> str:
        """
        Monitor name.
        """

        return self._name


    @property
    def collector(self) -> MetricCollector:
        """
        Attached metric collector.
        """

        return self._collector


    @property
    def enabled(self) -> bool:
        """
        Monitor enabled state.
        """

        return self._enabled


    @property
    def timestamp(self) -> float:
        """
        Last evaluation timestamp.
        """

        return self._timestamp


    @property
    def evaluation_count(self) -> int:
        """
        Number of evaluations.
        """

        return self._evaluation_count


    @property
    def last_duration(self) -> float:
        """
        Last evaluation duration.
        """

        return self._last_duration


    @property
    def health(self) -> str:
        """
        Current monitor health.
        """

        return self._health


    @property
    def lock(self) -> RLock:
        """
        Internal thread lock.
        """

        return self._lock



    # ======================================================
    # Internal Timing Helpers
    # ======================================================

    def _begin_evaluation(self) -> float:
        """
        Start evaluation timer.
        """

        return time()



    def _end_evaluation(
        self,
        started_at: float,
    ) -> None:
        """
        Finish evaluation timer.
        """

        self._timestamp = time()

        self._last_duration = (
            self._timestamp - started_at
        )

        self._evaluation_count += 1
# ======================================================
# Part 2. Monitoring API
# ======================================================


# ------------------------------------------------------
# Evaluate All
# ------------------------------------------------------

def evaluate(
    self,
) -> dict[str, object]:
    """
    Evaluate all collected metrics.

    Returns
    -------
    dict
        Monitoring evaluation result.
    """

    with self._lock:

        if not self._enabled:
            return {
                "status": "disabled",
                "metrics": (),
            }


        started_at = self._begin_evaluation()


        samples = self._collector.collect()


        result = {
            "status": "ok",
            "metrics": samples,
            "count": len(samples),
            "timestamp": time(),
        }


        self._last_result = result


        self._update_health(
            result
        )


        self._end_evaluation(
            started_at
        )


        return result



# ------------------------------------------------------
# Evaluate One
# ------------------------------------------------------

def evaluate_one(
    self,
    key: str,
) -> dict[str, object] | None:
    """
    Evaluate a single metric.
    """

    with self._lock:

        if not self._enabled:
            return None


        started_at = self._begin_evaluation()


        sample = (
            self._collector.collect_one(key)
        )


        if sample is None:

            result = {
                "status": "missing",
                "metric": key,
            }

        else:

            result = {
                "status": "ok",
                "metric": sample,
            }


        self._last_result = result


        self._update_health(
            result
        )


        self._end_evaluation(
            started_at
        )


        return result



# ------------------------------------------------------
# Evaluate Many
# ------------------------------------------------------

def evaluate_many(
    self,
    keys: list[str] | tuple[str, ...],
) -> dict[str, object]:
    """
    Evaluate multiple metrics.
    """

    with self._lock:

        if not self._enabled:
            return {
                "status": "disabled",
                "metrics": (),
            }


        started_at = self._begin_evaluation()


        samples = (
            self._collector.collect_many(keys)
        )


        result = {
            "status": "ok",
            "metrics": samples,
            "count": len(samples),
            "timestamp": time(),
        }


        self._last_result = result


        self._update_health(
            result
        )


        self._end_evaluation(
            started_at
        )


        return result



# ------------------------------------------------------
# Run Cycle
# ------------------------------------------------------

def run_cycle(
    self,
) -> dict[str, object]:
    """
    Execute one monitoring cycle.

    Alias for evaluate().
    """

    return self.evaluate()



# ------------------------------------------------------
# Update Health
# ------------------------------------------------------

def _update_health(
    self,
    result: dict[str, object],
) -> None:
    """
    Update monitor health state.
    """

    status = result.get(
        "status"
    )


    if status == "disabled":

        self._health = "disabled"


    elif status == "missing":

        self._health = "degraded"


    elif status == "ok":

        self._health = "healthy"


    else:

        self._health = "unknown"
# ======================================================
# Part 3. Rule API
# ======================================================


# ------------------------------------------------------
# Add Rule
# ------------------------------------------------------

def add_rule(
    self,
    name: str,
    rule,
) -> None:
    """
    Register a monitoring rule.

    Parameters
    ----------
    name:
        Unique rule name.

    rule:
        Callable evaluation function.
    """

    with self._lock:

        self._rules[name] = rule



# ------------------------------------------------------
# Remove Rule
# ------------------------------------------------------

def remove_rule(
    self,
    name: str,
) -> bool:
    """
    Remove a monitoring rule.

    Returns
    -------
    bool
        True if removed.
    """

    with self._lock:

        if name not in self._rules:
            return False


        del self._rules[name]

        return True



# ------------------------------------------------------
# Has Rule
# ------------------------------------------------------

def has_rule(
    self,
    name: str,
) -> bool:
    """
    Check rule existence.
    """

    with self._lock:

        return name in self._rules



# ------------------------------------------------------
# Get Rule
# ------------------------------------------------------

def get_rule(
    self,
    name: str,
):
    """
    Return rule by name.
    """

    with self._lock:

        return self._rules.get(
            name
        )



# ------------------------------------------------------
# List Rules
# ------------------------------------------------------

def list_rules(
    self,
) -> tuple[str, ...]:
    """
    Return all rule names.
    """

    with self._lock:

        return tuple(
            self._rules.keys()
        )



# ------------------------------------------------------
# Clear Rules
# ------------------------------------------------------

def clear_rules(
    self,
) -> None:
    """
    Remove all rules.
    """

    with self._lock:

        self._rules.clear()



# ------------------------------------------------------
# Rule Count
# ------------------------------------------------------

@property
def rule_count(
    self,
) -> int:
    """
    Number of registered rules.
    """

    return len(
        self._rules
    )



# ------------------------------------------------------
# Evaluate Rules
# ------------------------------------------------------

def evaluate_rules(
    self,
    samples,
) -> dict[str, object]:
    """
    Execute all rules against samples.

    Returns
    -------
    dict
        Rule evaluation results.
    """

    results = {}


    with self._lock:

        for name, rule in self._rules.items():

            try:

                results[name] = rule(
                    samples
                )


            except Exception as exc:

                results[name] = {
                    "error": str(exc)
                }


    return results
# ======================================================
# Part 4. Threshold API
# ======================================================


# ------------------------------------------------------
# Add Threshold
# ------------------------------------------------------

def add_threshold(
    self,
    name: str,
    metric: str,
    operator: str,
    value,
) -> None:
    """
    Add a threshold monitoring rule.

    Example
    -------
    add_threshold(
        "cpu_high",
        "cpu",
        ">",
        90,
    )
    """

    with self._lock:

        self._rules[name] = {
            "type": "threshold",
            "metric": metric,
            "operator": operator,
            "value": value,
        }



# ------------------------------------------------------
# Remove Threshold
# ------------------------------------------------------

def remove_threshold(
    self,
    name: str,
) -> bool:
    """
    Remove threshold rule.
    """

    with self._lock:

        rule = self._rules.get(name)


        if (
            rule is None
            or rule.get("type") != "threshold"
        ):
            return False


        del self._rules[name]

        return True



# ------------------------------------------------------
# Get Threshold
# ------------------------------------------------------

def get_threshold(
    self,
    name: str,
):
    """
    Return threshold configuration.
    """

    with self._lock:

        rule = self._rules.get(name)


        if (
            rule is None
            or rule.get("type") != "threshold"
        ):
            return None


        return rule



# ------------------------------------------------------
# List Thresholds
# ------------------------------------------------------

def list_thresholds(
    self,
) -> tuple[str, ...]:
    """
    Return all threshold rules.
    """

    with self._lock:

        return tuple(
            name
            for name, rule
            in self._rules.items()
            if rule.get("type")
            == "threshold"
        )



# ------------------------------------------------------
# Compare Helper
# ------------------------------------------------------

def _compare_threshold(
    self,
    current,
    operator: str,
    target,
) -> bool:
    """
    Compare current value with threshold.
    """

    if operator == ">":
        return current > target


    if operator == ">=":
        return current >= target


    if operator == "<":
        return current < target


    if operator == "<=":
        return current <= target


    if operator == "==":
        return current == target


    if operator == "!=":
        return current != target


    raise ValueError(
        f"Unsupported operator: {operator}"
    )



# ------------------------------------------------------
# Evaluate Threshold
# ------------------------------------------------------

def evaluate_threshold(
    self,
    samples,
) -> dict[str, bool]:
    """
    Evaluate all threshold rules.
    """

    results = {}


    with self._lock:

        for name, rule in self._rules.items():

            if rule.get("type") != "threshold":
                continue


            metric_name = rule["metric"]


            operator = rule["operator"]


            target = rule["value"]


            matched = False


            for sample in samples:

                if sample.get(
                    "key"
                ) != metric_name:
                    continue


                current = sample.get(
                    "value"
                )


                matched = self._compare_threshold(
                    current,
                    operator,
                    target,
                )


                break


            results[name] = matched


    return results
# ======================================================
# Part 5. Evaluation API
# ======================================================


# ------------------------------------------------------
# Evaluate Samples
# ------------------------------------------------------

def evaluate_samples(
    self,
    samples,
) -> dict[str, object]:
    """
    Evaluate a collected metric sample set.
    """

    with self._lock:

        if not self._enabled:

            return {
                "status": "disabled",
                "rules": {},
                "thresholds": {},
            }


        started_at = self._begin_evaluation()


        #
        # Custom rules
        #
        rule_results = (
            self.evaluate_rules(samples)
        )


        #
        # Threshold rules
        #
        threshold_results = (
            self.evaluate_threshold(samples)
        )


        #
        # Combine results
        #
        failures = []


        for name, result in rule_results.items():

            if result is False:

                failures.append(name)


            if isinstance(result, dict):

                if "error" in result:
                    failures.append(name)



        for name, result in threshold_results.items():

            if result is True:

                failures.append(name)



        #
        # Final result
        #
        status = (
            "warning"
            if failures
            else "healthy"
        )


        result = {

            "status": status,

            "rules": rule_results,

            "thresholds": threshold_results,

            "failures": tuple(
                failures
            ),

            "count": len(samples),

            "timestamp": time(),

        }


        self._last_result = result


        self._health = status


        self._end_evaluation(
            started_at
        )


        return result



# ------------------------------------------------------
# Evaluate Collector
# ------------------------------------------------------

def evaluate_collector(
    self,
) -> dict[str, object]:
    """
    Collect metrics and evaluate them.
    """

    samples = (
        self._collector.collect()
    )


    return self.evaluate_samples(
        samples
    )



# ------------------------------------------------------
# Evaluate One Metric
# ------------------------------------------------------

def evaluate_metric(
    self,
    key: str,
) -> dict[str, object]:
    """
    Evaluate one metric.
    """

    sample = (
        self._collector.collect_one(key)
    )


    if sample is None:

        return {
            "status": "missing",
            "metric": key,
        }


    return self.evaluate_samples(
        (sample,)
    )



# ------------------------------------------------------
# Last Result
# ------------------------------------------------------

@property
def last_result(
    self,
):
    """
    Return last evaluation result.
    """

    return self._last_result



# ------------------------------------------------------
# Is Healthy
# ------------------------------------------------------

@property
def is_healthy(
    self,
) -> bool:
    """
    Check evaluation health.
    """

    return (
        self._health
        == "healthy"
    )



# ------------------------------------------------------
# Has Failure
# ------------------------------------------------------

@property
def has_failure(
    self,
) -> bool:
    """
    Check if last evaluation failed.
    """

    if self._last_result is None:

        return False


    return bool(
        self._last_result.get(
            "failures",
            ()
        )
    )
# ======================================================
# Part 6. Hook API
# ======================================================


# ------------------------------------------------------
# Register Hook
# ------------------------------------------------------

def register_hook(
    self,
    event: str,
    callback,
) -> None:
    """
    Register monitoring hook.

    Supported events:

    - before_evaluation
    - after_evaluation
    - on_failure
    """

    with self._lock:

        self._hooks.setdefault(
            event,
            []
        ).append(
            callback
        )



# ------------------------------------------------------
# Remove Hook
# ------------------------------------------------------

def remove_hook(
    self,
    event: str,
    callback,
) -> bool:
    """
    Remove registered hook.
    """

    with self._lock:

        callbacks = (
            self._hooks.get(event)
        )


        if not callbacks:

            return False


        if callback not in callbacks:

            return False


        callbacks.remove(
            callback
        )

        return True



# ------------------------------------------------------
# Clear Hooks
# ------------------------------------------------------

def clear_hooks(
    self,
) -> None:
    """
    Remove all hooks.
    """

    with self._lock:

        self._hooks.clear()



# ------------------------------------------------------
# List Hooks
# ------------------------------------------------------

def list_hooks(
    self,
) -> dict[str, int]:
    """
    Return hook statistics.
    """

    with self._lock:

        return {
            name: len(callbacks)

            for name, callbacks
            in self._hooks.items()
        }



# ------------------------------------------------------
# Dispatch Hook
# ------------------------------------------------------

def dispatch_hook(
    self,
    event: str,
    *args,
    **kwargs,
) -> None:
    """
    Execute hooks.
    """

    callbacks = (
        self._hooks.get(
            event,
            ()
        )
    )


    for callback in callbacks:

        try:

            callback(
                *args,
                **kwargs,
            )


        except Exception:

            #
            # Hooks must never break
            # monitoring pipeline
            #
            continue



# ------------------------------------------------------
# Before Evaluation
# ------------------------------------------------------

def _before_evaluation(
    self,
    samples,
) -> None:
    """
    Internal pre-evaluation hook.
    """

    self.dispatch_hook(
        "before_evaluation",
        self,
        samples,
    )



# ------------------------------------------------------
# After Evaluation
# ------------------------------------------------------

def _after_evaluation(
    self,
    result,
) -> None:
    """
    Internal post-evaluation hook.
    """

    self.dispatch_hook(
        "after_evaluation",
        self,
        result,
    )



# ------------------------------------------------------
# Failure Hook
# ------------------------------------------------------

def _on_failure(
    self,
    result,
) -> None:
    """
    Internal failure hook.
    """

    self.dispatch_hook(
        "on_failure",
        self,
        result,
    )
# ======================================================
# Part 7. Snapshot API
# ======================================================


# ------------------------------------------------------
# Snapshot
# ------------------------------------------------------

def snapshot(
    self,
) -> dict[str, object]:
    """
    Create monitor runtime snapshot.

    Returns
    -------
    dict
        Serializable monitor state.
    """

    with self._lock:

        return {

            "name": self._name,

            "enabled": self._enabled,

            "timestamp": self._timestamp,

            "evaluation_count": (
                self._evaluation_count
            ),

            "last_duration": (
                self._last_duration
            ),

            "health": self._health,

            "rules": dict(
                self._rules
            ),

            "last_result": (
                self._last_result
            ),

        }



# ------------------------------------------------------
# Restore
# ------------------------------------------------------

def restore(
    self,
    snapshot: dict[str, object],
) -> None:
    """
    Restore monitor state.
    """

    with self._lock:

        self._name = snapshot.get(
            "name",
            self._name,
        )

        self._enabled = snapshot.get(
            "enabled",
            True,
        )

        self._timestamp = snapshot.get(
            "timestamp",
            0.0,
        )

        self._evaluation_count = snapshot.get(
            "evaluation_count",
            0,
        )

        self._last_duration = snapshot.get(
            "last_duration",
            0.0,
        )

        self._health = snapshot.get(
            "health",
            "idle",
        )

        self._rules = dict(
            snapshot.get(
                "rules",
                {},
            )
        )

        self._last_result = snapshot.get(
            "last_result"
        )



# ------------------------------------------------------
# Clone
# ------------------------------------------------------

def clone(
    self,
    *,
    name: str | None = None,
):
    """
    Create independent monitor copy.

    Collector reference is shared.
    """

    with self._lock:

        new_monitor = self.__class__(
            collector=self._collector,
            name=(
                name
                or self._name
            ),
        )


        new_monitor.restore(
            self.snapshot()
        )


        return new_monitor



# ------------------------------------------------------
# Copy
# ------------------------------------------------------

def copy(
    self,
):
    """
    Shallow copy wrapper.
    """

    return self.clone()
# ======================================================
# Part 8. Serialization API
# ======================================================


import json



# ------------------------------------------------------
# To Dict
# ------------------------------------------------------

def to_dict(
    self,
) -> dict[str, object]:
    """
    Convert monitor state to dictionary.
    """

    return self.snapshot()



# ------------------------------------------------------
# From Dict
# ------------------------------------------------------

def from_dict(
    self,
    data: dict[str, object],
) -> None:
    """
    Restore monitor from dictionary.
    """

    self.restore(
        data
    )



# ------------------------------------------------------
# To JSON
# ------------------------------------------------------

def to_json(
    self,
    *,
    indent: int = 2,
) -> str:
    """
    Serialize monitor state to JSON.
    """

    return json.dumps(
        self.to_dict(),
        indent=indent,
        default=str,
    )



# ------------------------------------------------------
# From JSON
# ------------------------------------------------------

def from_json(
    self,
    text: str,
) -> None:
    """
    Restore monitor from JSON.
    """

    data = json.loads(
        text
    )


    self.from_dict(
        data
    )



# ------------------------------------------------------
# Save
# ------------------------------------------------------

def save(
    self,
    path: str,
) -> None:
    """
    Save monitor state to file.
    """

    with open(
        path,
        "w",
        encoding="utf-8",
    ) as file:

        file.write(
            self.to_json()
        )



# ------------------------------------------------------
# Load
# ------------------------------------------------------

def load(
    self,
    path: str,
) -> None:
    """
    Load monitor state from file.
    """

    with open(
        path,
        "r",
        encoding="utf-8",
    ) as file:

        self.from_json(
            file.read()
        )



# ------------------------------------------------------
# Export
# ------------------------------------------------------

def export_state(
    self,
) -> str:
    """
    Export runtime state.

    Alias for to_json().
    """

    return self.to_json()



# ------------------------------------------------------
# Import
# ------------------------------------------------------

def import_state(
    self,
    text: str,
) -> None:
    """
    Import runtime state.

    Alias for from_json().
    """

    self.from_json(
        text
    )
# ======================================================
# Part 9. Debug Helpers
# ======================================================


# ------------------------------------------------------
# State
# ------------------------------------------------------

@property
def state(
    self,
) -> dict[str, object]:
    """
    Return current monitor runtime state.
    """

    with self._lock:

        return {

            "name": self._name,

            "enabled": self._enabled,

            "health": self._health,

            "timestamp": self._timestamp,

            "evaluation_count":
                self._evaluation_count,

            "last_duration":
                self._last_duration,

            "rule_count":
                len(self._rules),

            "hook_count":
                sum(
                    len(v)
                    for v in self._hooks.values()
                ),

        }



# ------------------------------------------------------
# Age
# ------------------------------------------------------

@property
def age(
    self,
) -> float | None:
    """
    Seconds since last evaluation.

    None means never evaluated.
    """

    if self._timestamp == 0:

        return None


    return (
        time()
        -
        self._timestamp
    )



# ------------------------------------------------------
# Is Empty
# ------------------------------------------------------

@property
def is_empty(
    self,
) -> bool:
    """
    Check whether monitor has no rules.
    """

    return (
        len(self._rules)
        == 0
    )



# ------------------------------------------------------
# Statistics
# ------------------------------------------------------

@property
def statistics(
    self,
) -> dict[str, object]:
    """
    Monitoring statistics.
    """

    with self._lock:

        return {

            "evaluations":
                self._evaluation_count,

            "last_duration":
                self._last_duration,

            "last_timestamp":
                self._timestamp,

            "rules":
                len(self._rules),

            "hooks":
                sum(
                    len(v)
                    for v in self._hooks.values()
                ),

            "health":
                self._health,

        }



# ------------------------------------------------------
# Health
# ------------------------------------------------------

@property
def health_status(
    self,
) -> str:
    """
    Return monitor health.
    """

    return self._health



# ------------------------------------------------------
# Summary
# ------------------------------------------------------

@property
def summary(
    self,
) -> dict[str, object]:
    """
    Human-readable monitor summary.
    """

    return {

        "name":
            self._name,

        "health":
            self._health,

        "enabled":
            self._enabled,

        "evaluations":
            self._evaluation_count,

        "rules":
            len(self._rules),

    }



# ------------------------------------------------------
# Dump
# ------------------------------------------------------

def dump(
    self,
) -> dict[str, object]:
    """
    Full diagnostic dump.
    """

    with self._lock:

        return {

            "state":
                self.state,

            "statistics":
                self.statistics,

            "summary":
                self.summary,

            "last_result":
                self._last_result,

            "rules":
                list(
                    self._rules.keys()
                ),

            "hooks":
                self.list_hooks(),

        }
# ======================================================
# Part 10. Thread Safety
# ======================================================


# ------------------------------------------------------
# Acquire Lock
# ------------------------------------------------------

def acquire(
    self,
    blocking: bool = True,
    timeout: float = -1,
) -> bool:
    """
    Acquire monitor lock.
    """

    return self._lock.acquire(
        blocking,
        timeout,
    )



# ------------------------------------------------------
# Release Lock
# ------------------------------------------------------

def release(
    self,
) -> None:
    """
    Release monitor lock.
    """

    self._lock.release()



# ------------------------------------------------------
# Locked State
# ------------------------------------------------------

@property
def locked(
    self,
) -> bool:
    """
    Return lock ownership status.

    Mainly for debugging.
    """

    checker = getattr(
        self._lock,
        "_is_owned",
        None,
    )


    if checker is None:

        return False


    return checker()



# ------------------------------------------------------
# Context Manager
# ------------------------------------------------------

def __enter__(
    self,
):
    """
    Enter synchronized section.
    """

    self.acquire()

    return self



def __exit__(
    self,
    exc_type,
    exc_value,
    traceback,
) -> bool:
    """
    Exit synchronized section.
    """

    self.release()

    return False



# ------------------------------------------------------
# Thread Safe Enable
# ------------------------------------------------------

def enable(
    self,
) -> None:
    """
    Enable monitor safely.
    """

    with self._lock:

        self._enabled = True



# ------------------------------------------------------
# Thread Safe Disable
# ------------------------------------------------------

def disable(
    self,
) -> None:
    """
    Disable monitor safely.
    """

    with self._lock:

        self._enabled = False



# ------------------------------------------------------
# Thread Safe Status
# ------------------------------------------------------

def is_enabled(
    self,
) -> bool:
    """
    Return enabled state safely.
    """

    with self._lock:

        return self._enabled



# ------------------------------------------------------
# Execute Locked
# ------------------------------------------------------

def synchronized(
    self,
    func,
    *args,
    **kwargs,
):
    """
    Execute callable under monitor lock.
    """

    with self._lock:

        return func(
            *args,
            **kwargs,
        )



# ------------------------------------------------------
# Safe Update
# ------------------------------------------------------

def update_state(
    self,
    **kwargs,
) -> None:
    """
    Safely update internal state.

    Intended for runtime extensions.
    """

    with self._lock:

        for key, value in kwargs.items():

            if hasattr(
                self,
                f"_{key}",
            ):

                setattr(
                    self,
                    f"_{key}",
                    value,
                )



# ------------------------------------------------------
# Safe Read
# ------------------------------------------------------

def read_state(
    self,
    key: str,
):
    """
    Safely read internal state.
    """

    with self._lock:

        return getattr(
            self,
            f"_{key}",
            None,
        )                                                