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

## What Works Today

SciOS is under active research and development. This section distinguishes capabilities that are implemented and tested from contracts that have been explicitly frozen, and from capabilities that remain planned.

### Runtime

**Implemented**

SciOS provides a modular execution foundation for scientific AI, including runtime execution, execution context, scheduling, registry/event infrastructure, and agent/tool execution boundaries.

**Tested**

Runtime and agent/tool execution behavior is covered by automated tests, including architecture and integration boundaries.

**Frozen**

Selected runtime and agent/tool boundaries have been stabilized through explicit versioned architecture and integration milestones.

**Planned**

Distributed execution, GPU execution, and larger-scale scientific compute orchestration remain future capabilities. They should not be interpreted as fully implemented capabilities of the current public milestone.

### Cognitive Contracts

**Implemented**

SciOS contains cognitive-layer components and contracts covering planning, reflection, inference, and related execution boundaries.

**Tested**

These components are developed with focused contract and architecture tests.

**Frozen**

Selected cognitive architecture boundaries have been explicitly stabilized as versioned milestones.

**Planned**

A complete autonomous scientific-agent loop -- combining planning, inference, reflection, long-term memory, tool use, and end-to-end autonomous research execution -- remains future work.

### Scientific Evidence

**Implemented**

SciOS now includes a model-comparison evidence layer under `scios/domain_science/model_comparison`.

The public contract defines explicit scientific structures for model identity, definitions, datasets, criteria, evaluations, evidence, claims, lineage, and model comparison.

**Tested**

The public model-comparison milestone includes dedicated contract and architecture tests covering:

- model identity
- definitions
- datasets and dataset processing
- criteria
- evaluations
- evidence
- claims
- lineage
- model neutrality
- model comparison
- architecture boundaries

**Frozen**

`domain-science-model-comparison-v0.1` is a frozen scientific evidence-contract milestone.

Its scope is deliberately limited to scientific representation, evidence structures, evaluation states, comparison structures, and scientific invariants.

It does **not** claim to provide a fitting engine, inference algorithm, scientific pipeline, or runtime-coupled autonomous discovery system.

**Planned**

Scientific fitting, inference engines, larger scientific pipelines, and autonomous discovery workflows remain future layers.

### Public Scientific Trial

SciOS currently provides a reproducible CSV analysis public trial.

**Implemented**

The public API exposes CSV analysis through `POST /csv/analyze`, returning analysis results together with:

- `analysis_run_id` -- identifies a particular analysis execution
- `dataset_hash` -- identifies the exact raw CSV input through its SHA-256 hash

**Tested**

The public trial validates reproducibility and public-boundary behavior, including deterministic dataset hashing for identical raw CSV bytes and distinct execution identifiers for repeated analyses.

**Frozen**

The CSV analysis public trial and its reproducibility/provenance boundaries have been released as explicit versioned milestones.

**Planned**

Broader scientific analysis, model fitting, inference, simulation, and autonomous research workflows remain separate future capabilities.

### Frozen Milestones

The repository currently contains explicitly versioned milestones including:

- `csv-analysis-public-trial-v0.1`
- `csv-analysis-public-trial-v0.1.1`
- `csv-analysis-reproducibility-provenance-v0.1`
- `domain-science-model-comparison-v0.1`

Additional architecture and capability milestones exist in the repository history and are developed independently from the scientific evidence layer.

### Status Vocabulary

To keep architectural vision separate from demonstrated capability, SciOS uses the following status vocabulary:

| Status | Meaning |
|---|---|
| **Implemented** | The corresponding code exists in the repository. |
| **Tested** | Automated tests or an explicit validation procedure covers the capability. |
| **Frozen** | The contract or boundary has been intentionally stabilized as a versioned milestone. |
| **Planned** | The capability is part of the future architecture or roadmap and should not be interpreted as currently implemented. |

SciOS therefore distinguishes its long-term research vision from capabilities that can currently be inspected, tested, and reproduced in the public repository.
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
