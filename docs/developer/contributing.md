# Contributing Guide

## Welcome

Thank you for your interest in contributing to SciOS.

SciOS is a research-oriented cognitive operating system that welcomes contributions from software engineers, researchers, students, and the open-source community.

Every contribution—whether code, documentation, testing, design, or research—helps improve the project.

---

# Ways to Contribute

There are many ways to contribute.

## Software Development

Examples include:

* Kernel improvements
* Runtime enhancements
* Cognitive Pipeline
* Memory subsystem
* Reasoning engine
* Planning framework
* Tool integration
* Reflection engine

---

## Documentation

Documentation contributions are highly encouraged.

Examples:

* Architecture improvements
* API documentation
* Tutorials
* Diagrams
* Developer handbook
* Usage examples

---

## Testing

Testing contributions include:

* Unit tests
* Integration tests
* Regression tests
* Performance benchmarks
* Runtime validation
* Pipeline validation

Reliable testing improves long-term project quality.

---

## Research

Research contributions may include:

* Experimental workflows
* Scientific benchmarks
* Algorithm evaluations
* Reproducibility studies
* Technical reports
* Design proposals

Research artifacts should be reproducible and clearly documented.

---

# Before You Start

Before beginning a contribution:

* Read the Developer Handbook.
* Understand the overall architecture.
* Review existing implementations.
* Search for related issues or discussions.
* Confirm that your proposed change aligns with project goals.

For large architectural changes, discussion before implementation is strongly recommended.

---

# Development Workflow

A typical contribution follows this workflow.

```text id="9xkh4t"
Issue
   │
   ▼
Discussion
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
Documentation
   │
   ▼
Code Review
   │
   ▼
Merge
```

Each stage helps maintain project quality and consistency.

---

# Setting Up the Development Environment

Typical setup steps include:

1. Clone the repository.
2. Create a virtual environment.
3. Install project dependencies.
4. Run the test suite.
5. Verify the development environment before making changes.

Refer to **onboarding.md** for detailed setup instructions.

---

# Branch Naming

Recommended branch names:

```text id="4shwne"
feature/runtime-loop

feature/memory-index

feature/pipeline-builder

bugfix/kernel-bootstrap

hotfix/runtime-crash

docs/developer-handbook
```

Branch names should clearly describe the intended change.

---

# Commit Messages

Commit messages should be concise and descriptive.

Examples:

```text id="s1m4n9"
Add runtime scheduler

Refactor pipeline builder

Improve memory retrieval

Fix kernel initialization

Update developer handbook
```

A good commit message explains *what* changed rather than *how* it was implemented.

---

# Pull Requests

Before submitting a pull request, verify that:

* The project builds successfully.
* Relevant tests pass.
* Documentation has been updated.
* Code follows project standards.
* Unrelated changes have been removed.

The pull request description should include:

* purpose
* summary of changes
* testing performed
* compatibility considerations
* related issues (if applicable)

---

# Coding Standards

All contributions should follow the project's coding standards.

General principles include:

* readability
* simplicity
* consistency
* modularity
* documentation
* maintainability

Refer to **coding_guidelines.md** for complete standards.

---

# Testing Requirements

New functionality should include appropriate automated tests.

Depending on the scope, tests may include:

* unit tests
* integration tests
* pipeline tests
* runtime tests
* regression tests
* performance tests

Changes that reduce test coverage should be justified and reviewed carefully.

---

# Documentation Requirements

Documentation should accompany architectural or user-facing changes.

Update documentation when modifying:

* APIs
* configuration
* architecture
* runtime behavior
* pipeline composition
* developer workflows

Documentation is considered part of the deliverable.

---

# Code Review

All significant contributions should undergo review.

Reviewers typically evaluate:

* correctness
* readability
* maintainability
* architectural consistency
* testing
* documentation

Constructive feedback is encouraged throughout the review process.

---

# Design Principles

Contributors should strive to preserve the architectural principles of SciOS.

These include:

* modular design
* loose coupling
* clear interfaces
* separation of concerns
* composition over inheritance
* extensibility
* reproducibility

Architectural consistency is often more valuable than introducing additional complexity.

---

# Reporting Issues

When reporting a bug, include as much relevant information as possible.

Useful information includes:

* operating system
* Python version
* SciOS version
* reproduction steps
* expected behavior
* observed behavior
* error messages
* relevant logs

Well-structured issue reports help accelerate investigation and resolution.

---

# Feature Requests

When proposing a new feature, consider including:

* motivation
* use case
* expected benefits
* architectural impact
* compatibility considerations
* possible implementation approach

Early discussion helps align proposals with the project's long-term direction.

---

# Research Contributions

Research-oriented submissions should aim to include:

* reproducible methodology
* datasets (where appropriate)
* evaluation procedures
* benchmark results
* references
* implementation details

Scientific transparency is an important goal of the project.

---

# Community Expectations

The SciOS community values:

* respectful communication
* constructive discussion
* evidence-based decision making
* openness to feedback
* collaborative problem solving

A welcoming and professional environment benefits both contributors and users.

---

# Recognition

Every contribution is valuable.

Examples include:

* source code
* documentation
* testing
* architecture reviews
* bug reports
* performance improvements
* research artifacts
* educational materials

Recognition is based on meaningful participation rather than contribution size.

---

# Best Practices

* Keep changes focused.
* Prefer small, reviewable pull requests.
* Write tests alongside implementation.
* Update documentation promptly.
* Preserve backward compatibility whenever practical.
* Discuss major architectural changes before implementation.
* Prioritize long-term maintainability.

---

# Summary

SciOS is built through collaborative engineering and research. By following the contribution workflow, adhering to coding and documentation standards, and maintaining the project's architectural principles, contributors help ensure that SciOS continues to evolve as a reliable, extensible, and research-grade cognitive operating system.
