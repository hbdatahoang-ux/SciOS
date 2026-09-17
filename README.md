# SciOS

> Scientific Cognitive Operating System
>
> A research-grade cognitive operating system for autonomous scientific discovery.

---

## Overview

SciOS is an open, modular, and extensible operating system for scientific AI.

The project integrates:

- Cognitive Kernel
- Runtime Engine
- Memory System
- Reasoning Engine
- Planning
- Reflection
- Tool Use
- Artifact Management
- Research Workflow

SciOS is designed to support reproducible research, autonomous scientific agents, and large-scale cognitive systems.

---

# Features

- Modular Cognitive Architecture
- Research-grade Artifact Management
- Reproducible Scientific Workflow
- Plugin-based Runtime
- Distributed Execution
- Experiment Tracking
- Benchmark Framework
- Dataset Registry
- Built-in Documentation System

---

# Project Structure

```
SciOS/

.github/
docs/
governance/

scios/

tests/

examples/

scripts/

README.md
```

---

# Documentation

## Architecture

- docs/architecture/

## API

- docs/api/

## Contracts

- docs/contracts/

## Artifact Specification

- docs/artifacts/

## Research Papers

- docs/research/papers/

---

# Research

Current research projects include

- SciOS
- CEIT
- QTC
- MUSES

See

```
docs/research/
```

---

# Artifact System

SciOS treats every scientific object as an independent artifact.

Supported artifacts

- Figures
- Tables
- Equations
- Datasets
- Benchmarks
- Experiments
- Models
- Workflows
- Supplementary Materials

See

```
docs/artifacts/
```

---

# Getting Started

Clone

```bash
git clone https://github.com/...
```

Install

```bash
pip install -e .
```

Run

```bash
python -m scios
```

---

# SciOS Public Trial — CSV Analysis v0.1

SciOS Public Trial v0.1 provides a reproducible CSV analysis API for inspecting
tabular datasets and identifying anomalous values.

The public trial exposes scientific analysis results together with two
reproducibility identifiers:

- `analysis_run_id` — unique identifier for each analysis run.
- `dataset_hash` — SHA-256 hash of the exact raw CSV bytes analyzed.

## Start the API

Install the project dependencies:

    pip install -e .

Start the API:

    python -m uvicorn scios.api.server:app --reload

The API is available at:

    http://127.0.0.1:8000

## CSV Analysis

### Endpoint

    POST /csv/analyze

### Request

    {
      "file_path": "data/dataset.csv",
      "query": "Analyze the CSV dataset and explain anomalous values."
    }

### Response

The public response is a flat contract containing:

- `goal`
- `rows`
- `columns`
- `column_names`
- `missing`
- `outliers`
- `reasoning`
- `explanation`
- `analysis_run_id`
- `dataset_hash`

`analysis_run_id` uniquely identifies an analysis run.

`dataset_hash` is the SHA-256 hash of the exact raw CSV bytes analyzed.

### Reproducibility Contract

The public trial guarantees:

1. `analysis_run_id` is unique for each analysis run.
2. The same exact raw CSV bytes produce the same `dataset_hash`.
3. Different raw CSV bytes produce a different `dataset_hash`.
4. Repeating an analysis with the same input produces a new `analysis_run_id`.

Therefore, `dataset_hash` identifies the analyzed input while
`analysis_run_id` identifies a particular execution of the analysis.

### Error Behavior

Common CSV input failures are reported using HTTP status codes:

| Condition | HTTP status |
|-----------|-------------|
| CSV file not found | 404 |
| Empty CSV file | 400 |
| Malformed CSV file | 400 |
| Other CSV analysis failure | 500 |

### Public Boundary

The public response intentionally exposes the scientific result and the two
reproducibility identifiers only.

Internal execution objects such as plans, execution graphs, tool results, and
provenance records are not part of the public CSV Analysis response contract.

### Acceptance

The Public Trial has been validated through the real HTTP API.

Repeated analysis of the same raw CSV has been verified to produce:

    same dataset_hash
    different analysis_run_id

---
# Development

Developer Guide

```
docs/developer/
```

Contribution Guide

```
.github/CONTRIBUTING.md
```

Coding Standards

```
docs/design/
```

---

# Governance

Project governance

```
governance/
```

Includes

- roadmap
- release policy
- decision process
- maintainers

---

# Documentation Index

| Area | Location |
|------|----------|
| Architecture | docs/architecture |
| API | docs/api |
| Design | docs/design |
| Contracts | docs/contracts |
| Tutorials | docs/tutorials |
| Examples | docs/examples |
| Research | docs/research |
| Artifact Specification | docs/artifacts |
| Benchmarks | docs/benchmarks |
| Developer Guide | docs/developer |

---

# Roadmap

See

```
ROADMAP.md
```

---

# Citation

```
CITATION.cff
```

---

# License

See

```
LICENSE
```

---

# Version

Current version

```
VERSION
```

---

# Community

- Issues
- Discussions
- Pull Requests
- Research Proposals
- Architecture RFCs

---

# SciOS Philosophy

Everything is modular.

Everything is reproducible.

Everything is traceable.

Everything is versioned.

Everything is an artifact.
