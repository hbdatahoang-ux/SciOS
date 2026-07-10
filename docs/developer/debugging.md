# SciOS Debugging Guide

## Overview

This document describes the recommended debugging practices for the SciOS project.

The objectives are to:

* Diagnose defects efficiently
* Reduce debugging time
* Improve system reliability
* Standardize debugging workflows
* Support reproducible issue investigation

Debugging should be systematic, data-driven, and reproducible.

---

# Debugging Philosophy

SciOS adopts the following principles when investigating issues.

* Reproduce before fixing.
* Collect evidence before making assumptions.
* Isolate the smallest failing component.
* Fix the root cause rather than symptoms.
* Verify that the fix does not introduce regressions.

---

# Common Debugging Workflow

```text
Issue Report
      │
      ▼
Reproduce Problem
      │
      ▼
Collect Logs
      │
      ▼
Inspect Runtime State
      │
      ▼
Isolate Component
      │
      ▼
Identify Root Cause
      │
      ▼
Implement Fix
      │
      ▼
Run Regression Tests
      │
      ▼
Document Resolution
```

---

# Debugging Levels

SciOS debugging can occur at several layers.

## Application Layer

Typical issues include:

* incorrect API usage
* invalid configuration
* malformed requests
* unexpected outputs

Recommended tools:

* unit tests
* integration tests
* structured logging

---

## Kernel Layer

Typical issues include:

* lifecycle failures
* scheduler deadlocks
* dispatcher errors
* service registration failures
* event routing problems

Recommended inspection:

* kernel state
* scheduler queue
* service registry
* event bus
* runtime status

---

## Cognitive Pipeline

Typical issues include:

* missing stages
* incorrect execution order
* invalid pipeline contracts
* context propagation failures
* pipeline interruption

Verify:

* registered stages
* execution graph
* stage outputs
* pipeline configuration

---

## Cognitive Subsystems

Each subsystem should be debugged independently before investigating interactions.

Subsystems include:

* Perception
* Memory
* Reasoning
* Planning
* Tool Use
* Reflection

Each subsystem should expose diagnostic information through status or debug interfaces.

---

# Logging

Structured logging is preferred.

Log entries should include:

* timestamp
* log level
* component
* operation
* execution identifier
* message

Example:

```text
INFO Kernel Scheduler Task queued id=42
```

Avoid excessive logging in performance-critical paths.

---

# Exception Handling

Exceptions should never be silently ignored.

Capture:

* exception type
* message
* stack trace
* relevant execution context

Example:

```python
try:
    pipeline.run(context)
except Exception:
    logger.exception("Pipeline execution failed.")
```

---

# Runtime Inspection

Useful runtime information includes:

* runtime status
* scheduler queue length
* active workers
* pipeline state
* lifecycle state
* registered services

Runtime inspection should not modify execution state.

---

# Pipeline Debugging Checklist

Verify:

* pipeline initialized successfully
* stage registration completed
* execution graph is valid
* context propagated correctly
* stage outputs are valid
* reflection completed
* memory update executed

If one stage fails, inspect its input and output before continuing.

---

# Kernel Debugging Checklist

Verify:

* kernel boot completed
* lifecycle state is correct
* scheduler operational
* runtime active
* dispatcher connected
* services registered

Kernel initialization failures should be resolved before debugging higher layers.

---

# Memory Debugging

Inspect:

* working memory contents
* semantic retrieval results
* episodic history
* memory update operations
* cache consistency

Confirm that retrieved knowledge matches expectations.

---

# Reasoning Debugging

Verify:

* reasoning input
* intermediate reasoning state
* generated conclusions
* confidence scores
* execution time

Reasoning should produce deterministic results for identical inputs unless stochastic behavior is explicitly enabled.

---

# Planning Debugging

Inspect:

* goals
* generated tasks
* execution order
* dependencies
* planner output

Check for missing or cyclic task dependencies.

---

# Tool Use Debugging

Verify:

* selected tool
* tool parameters
* execution status
* returned artifacts
* error messages

External tool failures should be isolated from pipeline failures whenever possible.

---

# Reflection Debugging

Inspect:

* evaluation metrics
* detected issues
* generated feedback
* confidence adjustments
* memory update requests

Reflection should improve future execution without corrupting historical knowledge.

---

# Configuration Debugging

Verify:

* YAML syntax
* environment variables
* runtime overrides
* plugin configuration
* pipeline settings

Configuration changes should be version controlled whenever possible.

---

# Reproducibility

Every reported issue should include:

* software version
* operating system
* Python version
* configuration
* input data
* expected behavior
* observed behavior
* logs
* stack trace

A reproducible issue is significantly easier to resolve.

---

# Performance-Related Issues

When investigating slow execution:

* measure before optimizing
* inspect scheduler
* profile CPU usage
* inspect memory consumption
* identify blocking operations
* analyze pipeline latency

Avoid premature optimization.

---

# Regression Prevention

After fixing an issue:

* add a regression test
* rerun the complete test suite
* verify backward compatibility
* update documentation if behavior changed

Every resolved defect should reduce the likelihood of future regressions.

---

# Useful Debugging Commands

Typical development workflow:

```bash
python -m unittest

pytest

pytest -v

pytest --maxfail=1

python -m scios.apps.cli.main
```

For coverage reporting:

```bash
coverage run -m pytest

coverage report

coverage html
```

---

# Debugging Best Practices

* Reproduce consistently before modifying code.
* Change one variable at a time.
* Keep debugging sessions focused on a single issue.
* Use meaningful log messages.
* Preserve evidence until the investigation is complete.
* Prefer automated verification over manual testing.
* Document the root cause and the final resolution.

---

# Summary

Effective debugging in SciOS is based on reproducibility, structured diagnostics, and careful isolation of components. By following a consistent debugging workflow and maintaining high-quality logs, tests, and documentation, contributors can resolve issues more efficiently and improve the long-term stability of the cognitive operating system.
