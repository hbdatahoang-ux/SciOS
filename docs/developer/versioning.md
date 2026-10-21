# SciOS Versioning Policy

## Overview

This document defines the versioning policy used throughout the SciOS project.

A consistent versioning strategy provides stability for developers, contributors, researchers, and downstream users while enabling predictable evolution of the platform.

The objectives are to:

* Communicate compatibility expectations
* Manage software evolution
* Support reproducible research
* Enable stable releases
* Simplify dependency management

SciOS follows Semantic Versioning with additional conventions for research and experimental development.

---

# Versioning Principles

The versioning policy is based on the following principles:

* Every release is uniquely identifiable.
* Stable releases preserve backward compatibility whenever practical.
* Breaking changes are communicated through major version increments.
* Experimental features are clearly labeled.
* Releases are reproducible.

---

# Semantic Versioning

SciOS uses the format:

```text
MAJOR.MINOR.PATCH
```

Example:

```text
0.1.0
0.2.3
1.0.0
2.4.1
```

Each component has a specific meaning.

---

# Major Version

The major version changes when:

* incompatible API changes occur
* architectural redesigns are introduced
* kernel interfaces change
* runtime contracts are modified

Examples:

```text
0.x.x → 1.0.0
1.x.x → 2.0.0
```

Major releases may require migration.

---

# Minor Version

The minor version changes when:

* new functionality is added
* new cognitive subsystems are introduced
* new APIs are added without breaking compatibility
* performance improvements introduce new capabilities

Examples:

```text
0.2.0
0.3.0
1.4.0
```

Minor releases remain backward compatible whenever possible.

---

# Patch Version

The patch version changes for:

* bug fixes
* documentation improvements
* internal optimizations
* security fixes
* performance improvements without API changes

Examples:

```text
0.2.1
0.2.2
0.2.3
```

Patch releases should not introduce breaking changes.

---

# Development Stages

SciOS progresses through several development stages.

```text
Prototype
      │
      ▼
Experimental
      │
      ▼
Alpha
      │
      ▼
Beta
      │
      ▼
Release Candidate
      │
      ▼
Stable
```

Each stage represents increasing maturity and stability.

---

# Pre-release Identifiers

Pre-release builds use descriptive suffixes.

Examples:

```text
0.2.0-alpha.1
0.2.0-alpha.2

0.2.0-beta.1
0.2.0-beta.2

0.2.0-rc.1

1.0.0
```

These identifiers communicate development status without changing the underlying version semantics.

---

# Research Versions

Research prototypes may use experimental identifiers.

Examples:

```text
0.4.0-exp

0.5.0-lab

0.6.0-prototype
```

Experimental releases are intended for research and evaluation rather than production deployment.

---

# Internal Milestones

During active development, milestones may be tagged to mark significant architectural progress.

Examples include:

* Kernel foundation
* Runtime integration
* Cognitive Pipeline
* Memory subsystem
* Planning subsystem
* Reflection subsystem

Milestones provide historical reference points for project evolution.

---

# Repository Tags

Every official release should be tagged in version control.

Examples:

```text
v0.1.0
v0.2.0
v0.2.1
v1.0.0
```

Tags should correspond exactly to released versions.

---

# Compatibility Policy

SciOS aims to preserve compatibility according to the following guidelines.

Patch releases:

* compatible

Minor releases:

* compatible whenever practical

Major releases:

* compatibility may change
* migration documentation should be provided

Users should be informed of compatibility expectations before upgrading.

---

# Deprecation Policy

Deprecated features should follow a gradual removal process.

```text
Introduced
      │
      ▼
Deprecated
      │
      ▼
Warning Period
      │
      ▼
Removal
```

Deprecation notices should include:

* affected component
* recommended replacement
* planned removal version

This approach allows downstream users time to migrate.

---

# Documentation Versioning

Developer documentation should evolve alongside software releases.

Each release should include updates for:

* architecture
* APIs
* runtime behavior
* pipeline changes
* migration notes

Documentation and implementation should remain synchronized.

---

# Artifact Versioning

Research artifacts should include version information.

Examples:

* experiment specifications
* datasets
* benchmark reports
* generated outputs
* scientific workflows

Artifact versions improve traceability and reproducibility.

---

# Configuration Versioning

Configuration schemas should evolve in a controlled manner.

When configuration formats change:

* schema versions should be updated
* migration paths should be documented
* legacy formats should remain supported where feasible

Configuration compatibility contributes to long-term system stability.

---

# Branch Strategy

A typical development workflow consists of:

```text
main
   │
   ├── release/*
   ├── feature/*
   ├── bugfix/*
   └── hotfix/*
```

Recommended branch purposes:

* **main** — stable development
* **feature/** — new functionality
* **bugfix/** — defect resolution
* **hotfix/** — urgent production fixes
* **release/** — release preparation

---

# Release History

Each release should include:

* version number
* release date
* summary of changes
* compatibility notes
* migration guidance
* known limitations

Maintaining a clear release history improves transparency.

---

# Roadmap Alignment

Version increments should reflect architectural progress.

Example progression:

```text
0.1.x
Kernel Foundation

↓

0.2.x
Cognitive Pipeline

↓

0.3.x
Runtime Expansion

↓

0.4.x
Distributed Runtime

↓

0.5.x
Scientific Workflow

↓

1.0.0
Stable Research Platform
```

Actual milestones may evolve as development progresses.

---

# Best Practices

* Follow Semantic Versioning consistently.
* Tag every official release.
* Document breaking changes clearly.
* Deprecate features before removal.
* Maintain migration documentation.
* Keep documentation synchronized with releases.
* Preserve reproducibility across versions.

---

# Summary

The SciOS Versioning Policy establishes a consistent and transparent framework for managing software evolution. By combining Semantic Versioning with structured release stages, compatibility guidelines, and research-oriented conventions, SciOS provides a stable foundation for long-term development, collaboration, and reproducible scientific computing.
