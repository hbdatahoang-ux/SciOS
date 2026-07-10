# SciOS Licensing Policy

Version: 1.0

Project: SciOS (Scientific Cognitive Operating System)

---

# Purpose

This document defines the licensing framework for the SciOS Research Platform.

SciOS combines:

- Open-source software
- Scientific research artifacts
- Technical documentation
- Research publications
- Datasets
- Benchmarks
- Experimental workflows
- Machine learning models

This policy establishes how these assets are licensed, distributed,
modified, and reused.

---

# Primary License

SciOS is primarily licensed under:

Apache License 2.0

The authoritative license text is located at:

```text
/LICENSE
```

All contributors and users must comply with the Apache License 2.0.

---

# Licensing Principles

SciOS follows five core principles:

1. Openness
2. Reproducibility
3. Attribution
4. Transparency
5. Scientific Integrity

---

# Licensing Scope

This policy applies to:

| Component | Covered |
|------------|----------|
| Source Code | Yes |
| Documentation | Yes |
| Research Artifacts | Yes |
| Research Papers | Yes |
| Benchmarks | Yes |
| Workflows | Yes |
| Datasets | Yes |
| Models | Yes |
| Supplementary Materials | Yes |

---

# Source Code

All original source code developed within SciOS is released under:

Apache License 2.0

Examples:

- Python
- Rust
- C++
- TypeScript
- JavaScript
- Shell Scripts
- Configuration Files

Unless explicitly noted otherwise.

---

# Documentation

Documentation is licensed under Apache License 2.0.

Examples:

- README files
- Specifications
- Tutorials
- Design documents
- API references
- Governance documents

---

# Artifact Licensing

SciOS treats artifacts as first-class research objects.

Artifacts include:

- Figures
- Tables
- Equations
- Datasets
- Experiments
- Benchmarks
- Models
- Notebooks
- Workflows
- Supplementary Materials

Every artifact should include:

```text
metadata.yml
```

with explicit licensing information.

---

# Artifact Metadata

Recommended field:

```yaml
License: Apache-2.0
```

Alternative licenses may be used when required.

---

# Figures

Figure artifacts may contain:

- PNG
- SVG
- Draw.io
- Source diagrams

Figures inherit Apache License 2.0 unless explicitly overridden.

---

# Tables

Tables inherit the project license unless:

- Generated from external datasets
- Subject to publisher restrictions

---

# Equations

Mathematical derivations and proofs are considered documentation.

They inherit the project license unless otherwise specified.

---

# Datasets

Datasets are divided into:

## Original Datasets

Created by the SciOS project.

Default license:

Apache License 2.0

## External Datasets

Retain their original license.

Examples:

- Kaggle
- UCI Repository
- Hugging Face Datasets

SciOS does not alter third-party licensing.

---

# Research Papers

Research papers are located under:

```text
docs/research/papers/
```

Drafts and preprints are generally licensed under Apache License 2.0.

Published versions may be subject to:

- Publisher copyright
- Journal policies
- Conference policies

Always verify publication-specific terms.

---

# Supplementary Materials

Supplementary artifacts inherit the parent paper license unless
specified otherwise.

Examples:

- Derivations
- Appendices
- Videos
- Raw Images
- Extended Methods

---

# Machine Learning Models

Models may have separate licenses.

Each model artifact should include:

```text
metadata.yml
model_card.md
license information
```

before distribution.

---

# Benchmark Data

Benchmark definitions created by SciOS are Apache-2.0 licensed.

Benchmark results belong to the entity that generated them unless
contractually specified otherwise.

---

# Third-Party Components

SciOS uses external software.

Examples include:

- NumPy
- Pandas
- PyTorch
- FastAPI
- Qdrant
- Docker
- Kubernetes

See:

```text
docs/legal/third_party.md
```

for details.

---

# Contributor Licensing

By contributing to SciOS, contributors agree that:

- Their contribution may be distributed under Apache License 2.0.
- They have the right to contribute the submitted material.
- The contribution does not knowingly violate third-party rights.

---

# Copyright

Copyright remains with the original author(s).

Contributors retain copyright to their own contributions.

SciOS does not require copyright assignment.

---

# Patent Grant

Apache License 2.0 includes an explicit patent grant.

Users should review the LICENSE file for details.

---

# Redistribution Requirements

Redistributors must:

- Include LICENSE
- Preserve NOTICE
- Preserve copyright notices
- Mark modified files

as required by Apache License 2.0.

---

# Citation Requirements

Use:

```text
CITATION.cff
```

when citing SciOS.

Academic publications should properly reference:

- Software
- Papers
- Datasets
- Benchmarks

when applicable.

---

# License Compatibility

Before introducing a new dependency:

- Verify license compatibility.
- Record it in third_party.md.
- Update NOTICE if required.

---

# Legal Hierarchy

In case of conflict:

1. LICENSE
2. NOTICE
3. COPYRIGHT
4. licensing.md
5. metadata.yml
6. file headers

Higher-level documents take precedence.

---

# Review Policy

This document should be reviewed:

- Before every major release
- When introducing new licenses
- When adding third-party dependencies
- When publishing new research artifacts

---

# Related Documents

```text
LICENSE
NOTICE
COPYRIGHT

docs/legal/README.md
docs/legal/third_party.md
docs/legal/intellectual_property.md
docs/legal/citation_policy.md

docs/artifacts/artifact_specification.md
```

---

# Contact

For licensing questions:

- Review LICENSE
- Review NOTICE
- Contact the SciOS maintainers

---

SciOS Research Platform

Scientific Cognitive Operating System

Apache License 2.0
Version 1.0