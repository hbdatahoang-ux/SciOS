# SciOS Coding Guidelines

## Overview

This document defines the coding standards adopted by the SciOS project.

The goals of these guidelines are to:

* Improve code readability
* Encourage consistency across the codebase
* Simplify maintenance
* Reduce defects
* Support collaborative development
* Facilate long-term evolution of the system

All contributors should follow these conventions unless there is a documented technical reason not to do so.

---

# Design Principles

SciOS follows several fundamental software engineering principles.

## Simplicity

Prefer simple solutions over complex implementations.

Complexity should only be introduced when it provides measurable value.

---

## Readability

Code is written for humans first.

Readable code is easier to review, debug, and extend.

---

## Modularity

Every component should have a clear responsibility.

Large modules should be decomposed into smaller reusable components.

---

## Extensibility

New features should be added by extension rather than by modifying stable components whenever practical.

---

## Testability

Every module should be designed with automated testing in mind.

Dependencies should be easy to replace using dependency injection or interfaces.

---

## Reproducibility

Scientific computations should produce deterministic results whenever possible.

---

# Project Structure

Each package should have a clearly defined purpose.

```text
scios/
│
├── api/
├── kernel/
├── runtime/
├── cognitive_core/
├── agents/
├── tools/
├── artifacts/
├── shared/
└── tests/
```

Avoid mixing unrelated responsibilities within the same package.

---

# Python Style

SciOS follows:

* PEP 8
* PEP 257
* Type hints (PEP 484)

Code should remain compatible with the supported Python version defined by the project.

---

# Naming Conventions

## Classes

Use PascalCase.

Example:

```python
class MemoryManager:
    ...
```

---

## Functions

Use snake_case.

```python
def process_input():
    ...
```

---

## Variables

Use descriptive snake_case names.

Avoid abbreviations unless they are well known.

Good examples:

```python
execution_context
memory_manager
pipeline_stage
```

Avoid:

```python
ctx
obj
tmp
x
```

except for short-lived loop variables.

---

## Constants

Use uppercase.

```python
MAX_PIPELINE_DEPTH = 32
DEFAULT_TIMEOUT = 60
```

---

## Modules

Use lowercase.

```text
memory.py
planner.py
runtime.py
dispatcher.py
```

---

# Imports

Imports should be grouped as:

```python
# Standard library

# Third-party packages

# SciOS modules
```

Avoid wildcard imports.

Instead of:

```python
from module import *
```

use

```python
from module import ClassName
```

---

# Type Hints

Public APIs should include type annotations.

Example:

```python
def execute(task: Task) -> Result:
    ...
```

Avoid untyped public interfaces.

---

# Docstrings

Public modules, classes, and methods should include docstrings.

Use descriptive documentation.

Example:

```python
class Scheduler:
    """
    Coordinates task scheduling within the runtime.
    """
```

---

# Comments

Comments should explain:

* why
* assumptions
* design decisions

Avoid comments that simply repeat the code.

Bad:

```python
# increment x
x += 1
```

Better:

```python
# Advance to the next execution window.
x += 1
```

---

# Error Handling

Raise meaningful exceptions.

Example:

```python
raise ValueError("Pipeline stage name cannot be empty.")
```

Avoid silent failures.

Never suppress exceptions without a documented reason.

---

# Logging

Use the project logging framework.

Avoid:

```python
print(...)
```

Use:

```python
logger.info(...)
logger.warning(...)
logger.error(...)
```

Logging levels should be used consistently.

---

# Dependency Management

Avoid unnecessary dependencies.

Prefer the Python standard library whenever practical.

Every external dependency should have a documented justification.

---

# Object-Oriented Design

Classes should follow the Single Responsibility Principle.

Avoid "God Objects."

Large classes should be decomposed into smaller components.

---

# Functional Design

Pure functions are encouraged when appropriate.

Functions should avoid hidden side effects whenever possible.

---

# Interfaces

Depend on abstractions rather than concrete implementations.

Prefer protocols or abstract base classes for extensible components.

---

# Configuration

Avoid hard-coded configuration values.

Use:

* configuration files
* environment variables
* dependency injection

instead.

---

# Testing

Every new feature should include automated tests.

Recommended test categories include:

* unit tests
* integration tests
* regression tests
* performance tests

Bug fixes should include regression tests whenever feasible.

---

# Performance

Optimize only after measurement.

Prefer readable implementations before micro-optimizations.

Profile first.

Optimize second.

---

# Security

Never:

* expose secrets
* hard-code credentials
* commit API keys
* disable validation checks

Input should always be validated before processing.

---

# Git Workflow

Recommended workflow:

```text
feature branch

↓

implementation

↓

tests

↓

code review

↓

merge
```

Every commit should have a meaningful message.

Example:

```text
Add Runtime Scheduler priority queue

Fix MemoryManager retrieval bug

Improve Pipeline validation
```

---

# Code Review Checklist

Before merging code, verify:

* formatting
* naming
* documentation
* tests
* type hints
* logging
* exception handling
* performance impact
* backward compatibility

---

# Documentation

Every major feature should include:

* architecture updates
* API documentation
* developer documentation
* usage examples

Documentation should evolve alongside the implementation.

---

# Scientific Computing Considerations

Since SciOS targets scientific applications:

* preserve reproducibility
* document assumptions
* record experiment metadata
* avoid non-deterministic behavior unless explicitly required
* support reproducible execution

---

# Design Philosophy

SciOS emphasizes:

* Clarity over cleverness
* Explicitness over implicit behavior
* Composition over inheritance
* Interfaces over implementations
* Modularity over monoliths
* Maintainability over short-term convenience

---

# Summary

These coding guidelines establish a consistent engineering standard across the SciOS project.

By following these conventions, contributors help ensure that the codebase remains readable, extensible, testable, and maintainable as SciOS evolves into a research-grade cognitive operating system.
