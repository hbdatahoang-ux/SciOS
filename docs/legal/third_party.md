# Third-Party Software and License Inventory

Version: 1.0

Project: SciOS (Scientific Cognitive Operating System)

---

# Overview

SciOS depends on a variety of third-party software, libraries,
frameworks, datasets, models, and development tools.

Each third-party component remains the intellectual property of
its respective authors and is governed by its own license.

This document provides an inventory of external dependencies and
their corresponding licenses.

---

# Purpose

This document aims to:

- Maintain license compliance.
- Provide attribution where required.
- Track external dependencies.
- Support legal review.
- Assist reproducible research.
- Support software distribution.

---

# Licensing Policy

SciOS itself is licensed under:

Apache License 2.0

Third-party components are **not relicensed** by SciOS.

Every dependency retains its original license.

Users are responsible for complying with those licenses.

---

# Dependency Categories

SciOS may include dependencies from the following categories:

- Programming Languages
- Python Packages
- JavaScript Packages
- Machine Learning Frameworks
- Scientific Computing Libraries
- Databases
- Visualization Libraries
- Container Platforms
- Cloud SDKs
- Documentation Tools
- Build Systems
- Testing Frameworks
- Fonts
- Icons
- Images
- Datasets
- AI Models

---

# Python Ecosystem

| Package | License | Purpose |
|----------|----------|----------|
| NumPy | BSD-3-Clause | Numerical Computing |
| SciPy | BSD-3-Clause | Scientific Algorithms |
| Pandas | BSD-3-Clause | Data Processing |
| Matplotlib | PSF | Plotting |
| Plotly | MIT | Interactive Visualization |
| PyYAML | MIT | YAML Parsing |
| Requests | Apache-2.0 | HTTP Client |
| FastAPI | MIT | REST API |
| Pydantic | MIT | Data Validation |
| Rich | MIT | Terminal UI |
| Typer | MIT | Command Line Interface |
| Pytest | MIT | Testing |
| Jupyter | BSD-3-Clause | Interactive Computing |

---

# Machine Learning

| Package | License |
|----------|----------|
| PyTorch | BSD-style |
| Transformers | Apache-2.0 |
| Tokenizers | Apache-2.0 |
| Safetensors | Apache-2.0 |
| Sentence Transformers | Apache-2.0 |
| ONNX Runtime | MIT |

---

# Data Infrastructure

| Component | License |
|------------|----------|
| Qdrant | Apache-2.0 |
| PostgreSQL | PostgreSQL License |
| SQLite | Public Domain |
| Redis | BSD-3-Clause |

---

# Container & Infrastructure

| Component | License |
|------------|----------|
| Docker | Apache-2.0 |
| Kubernetes | Apache-2.0 |
| Helm | Apache-2.0 |
| Terraform | MPL-2.0 |

---

# Documentation Tools

| Tool | License |
|------|----------|
| MkDocs | BSD-2-Clause |
| Material for MkDocs | MIT |
| Mermaid | MIT |

---

# Development Tools

| Tool | License |
|------|----------|
| Git | GPL-2.0 |
| Ruff | MIT |
| Black | MIT |
| MyPy | MIT |
| pre-commit | MIT |

---

# AI Models

Large Language Models, embedding models, and pretrained models
may use licenses different from SciOS.

Examples include:

- GGUF Models
- Hugging Face Models
- ONNX Models
- TensorFlow Models
- PyTorch Checkpoints

Always review the original model license before:

- Downloading
- Redistributing
- Fine-tuning
- Commercial deployment

---

# External Datasets

External datasets remain under their original licenses.

Examples include:

- UCI Machine Learning Repository
- Hugging Face Datasets
- Kaggle Datasets
- Zenodo
- OpenML

SciOS does not alter the licensing terms of external datasets.

---

# Fonts

Fonts included with SciOS remain under their original licenses.

Only fonts permitting redistribution should be bundled.

---

# Icons

Icons remain licensed by their original creators.

Typical sources include:

- Material Icons
- Heroicons
- Font Awesome

---

# Images

Images from external sources remain under their original
copyright and license.

Authors should provide attribution where required.

---

# Documentation Assets

Documentation assets originating from third parties must preserve:

- Copyright
- Attribution
- License

---

# Attribution

Whenever required by an upstream license,
SciOS preserves attribution through:

- NOTICE
- Documentation
- Source headers
- Metadata
- License files

---

# Updating This Inventory

Whenever introducing a new dependency:

1. Verify its license.
2. Confirm compatibility with Apache License 2.0.
3. Record it in this document.
4. Update NOTICE if required.
5. Add attribution when necessary.

---

# License Compatibility

Project maintainers should review new dependencies for compatibility.

Potentially incompatible licenses should be evaluated before adoption.

---

# No Warranty

Third-party software is distributed under the terms of its
respective licenses.

SciOS provides no additional warranties for third-party software.

---

# Related Documents

- LICENSE
- NOTICE
- COPYRIGHT
- docs/legal/licensing.md
- docs/legal/intellectual_property.md
- docs/legal/contribution_license.md

---

# References

Apache License 2.0

https://www.apache.org/licenses/LICENSE-2.0

SPDX License List

https://spdx.org/licenses/

Open Source Initiative

https://opensource.org/licenses

---

SciOS Research Platform

Scientific Cognitive Operating System

Version 1.0