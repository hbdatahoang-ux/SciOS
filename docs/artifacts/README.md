# SciOS Artifact System

This directory contains the specification and templates for the SciOS Artifact System.

---

## Purpose

Artifacts are the fundamental building blocks of SciOS research.  
Every figure, table, equation, dataset, experiment, benchmark, workflow, notebook, model, and supplementary material is treated as a **first-class artifact**.

---

## Contents

- **artifact_specification.md** → Core specification (v1.0)
- **metadata_schema.md** → Schema for artifact metadata
- **lifecycle.md** → Lifecycle states and transitions
- **naming_convention.md** → Rules for artifact IDs and names
- **registry_spec.md** → Format and rules for registry.csv
- **validation_rules.md** → Validation requirements for artifacts
- **dependency_graph.md** → Rules for artifact dependencies
- **versioning.md** → Semantic versioning for artifacts
- **templates/** → Example templates for each artifact type

---

## Artifact Types

| Prefix | Type |
|--------|------|
| F      | [Figure](ca://s?q=Explain_Figure_Artifacts) |
| T      | [Table](ca://s?q=Explain_Table_Artifacts) |
| EQ     | [Equation](ca://s?q=Explain_Equation_Artifacts) |
| DATA   | [Dataset](ca://s?q=Explain_Dataset_Artifacts) |
| EXP    | [Experiment](ca://s?q=Explain_Experiment_Artifacts) |
| BM     | [Benchmark](ca://s?q=Explain_Benchmark_Artifacts) |
| SUP    | [Supplementary](ca://s?q=Explain_Supplementary_Artifacts) |
| WF     | [Workflow](ca://s?q=Explain_Workflow_Artifacts) |
| NB     | [Notebook](ca://s?q=Explain_Notebook_Artifacts) |
| MODEL  | [Model](ca://s?q=Explain_Model_Artifacts) |

---

## Principles

- **Traceability**: Every artifact has a unique ID and metadata.
- **Reproducibility**: Artifacts include source files and dependencies.
- **Automation**: CI/CD validates metadata, registry, and dependencies.
- **Versioning**: Semantic versioning ensures clarity of changes.
- **Preservation**: Artifacts are archived for long-term research integrity.

---

## Lifecycle

Artifacts follow a standardized lifecycle:

Draft → Internal Review → Approved → Published → Archived

---

## Usage

- Each artifact resides in its own folder (`F-0001/`, `T-0001/`, etc.).
- Metadata and caption files are mandatory.
- Registries (`registry.csv`) are authoritative indexes.
- Dependencies must be declared explicitly.
- CI/CD pipelines enforce validation and consistency.

---

## Notes

This system is designed to scale across hundreds of artifacts, ensuring SciOS research remains reproducible, auditable, and extensible.
