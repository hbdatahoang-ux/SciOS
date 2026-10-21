# New Developer Guide

## Welcome to SciOS

Welcome to the SciOS project.

SciOS is a research-oriented cognitive operating system designed to support intelligent scientific workflows through a modular and extensible architecture.

This guide introduces new developers to the project structure, development workflow, coding standards, and recommended learning path.

Whether you are contributing to the kernel, runtime, cognitive subsystems, or documentation, this guide provides the foundation needed to become productive.

---

# Project Vision

SciOS aims to provide a unified platform for:

* Cognitive computing
* Scientific reasoning
* Autonomous agents
* Research workflow automation
* Knowledge management
* Tool orchestration
* Reproducible scientific computing

The project emphasizes modularity, maintainability, and long-term extensibility.

---

# Recommended Reading Order

New contributors are encouraged to follow this reading sequence.

```text
README
   │
   ▼
architecture.md
   │
   ▼
kernel.md
   │
   ▼
runtime.md
   │
   ▼
pipeline.md
   │
   ▼
perception.md
   │
   ▼
memory.md
   │
   ▼
reasoning.md
   │
   ▼
planning.md
   │
   ▼
tool_use.md
   │
   ▼
reflection.md
```

This progression introduces the system from high-level architecture down to individual cognitive subsystems.

---

# Repository Structure

A simplified view of the project layout is shown below.

```text
SciOS/
│
├── scios/
│   ├── api/
│   ├── kernel/
│   ├── runtime/
│   ├── cognitive_core/
│   ├── agents/
│   ├── substrate/
│   ├── shared/
│   └── interfaces/
│
├── docs/
├── tests/
├── examples/
└── scripts/
```

Developers should become familiar with the responsibilities of each top-level package before implementing new features.

---

# Core Components

The main architectural components include:

## Kernel

Responsible for:

* lifecycle management
* orchestration
* scheduling
* service registration
* runtime coordination

---

## Runtime

Responsible for:

* execution
* task management
* workers
* runtime loop
* resource coordination

---

## Cognitive Pipeline

Responsible for orchestrating cognitive stages.

Typical execution order:

```text
Perception
      │
      ▼
Memory
      │
      ▼
Reasoning
      │
      ▼
Planning
      │
      ▼
Tool Use
      │
      ▼
Reflection
```

The pipeline itself contains orchestration logic only. Domain-specific intelligence belongs within stage handlers.

---

# Development Environment

Recommended tools include:

* Python 3.11 or newer
* Git
* Visual Studio Code
* pytest
* virtual environments

Optional tools:

* Docker
* WSL
* Draw.io
* MkDocs
* GitHub Actions

---

# Getting Started

Clone the repository.

```bash
git clone <repository-url>
cd SciOS
```

Create a virtual environment.

```bash
python -m venv .venv
```

Activate the environment.

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install project dependencies.

```bash
pip install -e .
```

---

# Running Tests

Execute all unit tests.

```bash
python -m unittest
```

or

```bash
pytest
```

Developers should ensure that all relevant tests pass before submitting changes.

---

# Development Workflow

A typical workflow consists of:

```text
Issue
   │
   ▼
Feature Branch
   │
   ▼
Implementation
   │
   ▼
Testing
   │
   ▼
Code Review
   │
   ▼
Merge
```

Each contribution should remain focused on a single logical change whenever practical.

---

# Coding Standards

Follow the project's coding guidelines.

General principles include:

* write readable code
* use descriptive names
* avoid unnecessary complexity
* document public interfaces
* add tests for new functionality
* maintain backward compatibility when appropriate

Refer to:

* coding_guidelines.md

for complete standards.

---

# Documentation

Documentation is treated as part of the source code.

Whenever code changes:

* update documentation
* update diagrams if necessary
* document configuration changes
* document new APIs

Incomplete documentation should not accompany major architectural changes.

---

# Testing Expectations

Every new feature should include appropriate tests.

Testing may include:

* unit tests
* integration tests
* pipeline tests
* runtime tests
* regression tests

The goal is to maintain confidence in long-term project stability.

---

# Branch Naming

Recommended branch names:

```text
feature/runtime-loop

feature/pipeline-builder

feature/memory-cache

bugfix/kernel-bootstrap

hotfix/runtime-crash

docs/architecture
```

Consistent naming improves repository organization.

---

# Commit Messages

Example commit messages:

```text
Add runtime scheduler

Refactor pipeline builder

Improve memory retrieval

Fix kernel initialization

Update developer handbook
```

Commit messages should clearly describe the purpose of the change.

---

# Pull Requests

Before opening a pull request, verify that:

* code builds successfully
* tests pass
* documentation is updated
* formatting is consistent
* unnecessary files are removed

Reviewers should be able to understand the motivation and scope of the change from the pull request description.

---

# Common Development Areas

Developers commonly contribute to:

* Kernel
* Runtime
* Cognitive Pipeline
* Memory
* Reasoning
* Planning
* Tool Use
* Reflection
* Documentation
* Testing
* Developer Tools

Choose an area that aligns with your expertise and interests.

---

# Where to Ask Questions

If you encounter uncertainty:

* review the developer handbook
* inspect existing implementations
* discuss architectural questions before major changes
* keep design decisions consistent with the overall architecture

Collaborative discussion is encouraged before introducing significant architectural modifications.

---

# Best Practices

* Understand the architecture before coding.
* Keep modules cohesive and loosely coupled.
* Prefer composition over inheritance.
* Write tests alongside implementation.
* Keep documentation synchronized with code.
* Make incremental, reviewable changes.
* Prioritize maintainability over short-term convenience.

---

# Summary

This guide serves as the entry point for new SciOS developers. By understanding the project architecture, following the recommended development workflow, adhering to coding standards, and maintaining high-quality documentation and tests, contributors can effectively participate in building a scalable, research-grade cognitive operating system.
