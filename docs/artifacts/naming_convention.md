# SciOS Artifact Naming Convention v1.0

Version: 1.0  
Status: Draft  
Authors: SciOS Research Team

---

## Overview
This document defines the naming rules for artifacts in SciOS.  
Every artifact MUST have a unique, immutable ID following a standardized prefix and numeric sequence.

---

## General Rules

- **Prefix**: Indicates artifact type (F, T, EQ, DATA, EXP, BM, SUP, WF, NB, MODEL).
- **Numeric Sequence**: Four digits, zero-padded (0001, 0002, …).
- **Separator**: Hyphen (`-`) between prefix and number.
- **Immutability**: Once assigned, an ID SHALL never be reused or changed.
- **Uniqueness**: IDs must be globally unique across the project.
- **Registry**: All IDs must be recorded in the corresponding `registry.csv`.

---

## Artifact Prefixes

| Prefix | Type |
|--------|------|
| **F** | [Figure](ca://s?q=Explain_Figure_Artifacts) |
| **T** | [Table](ca://s?q=Explain_Table_Artifacts) |
| **EQ** | [Equation](ca://s?q=Explain_Equation_Artifacts) |
| **DATA** | [Dataset](ca://s?q=Explain_Dataset_Artifacts) |
| **EXP** | [Experiment](ca://s?q=Explain_Experiment_Artifacts) |
| **BM** | [Benchmark](ca://s?q=Explain_Benchmark_Artifacts) |
| **SUP** | [Supplementary](ca://s?q=Explain_Supplementary_Artifacts) |
| **WF** | [Workflow](ca://s?q=Explain_Workflow_Artifacts) |
| **NB** | [Notebook](ca://s?q=Explain_Notebook_Artifacts) |
| **MODEL** | [Model](ca://s?q=Explain_Model_Artifacts) |

---

## Examples

- `F-0001` → Kernel Architecture Figure  
- `T-0001` → Kernel Components Table  
- `EQ-0001` → Equation for Runtime Complexity  
- `DATA-0001` → Benchmark Dataset v1  
- `EXP-0001` → Experiment Protocol for Async Execution  
- `BM-0001` → Benchmark Results for Scheduler  
- `SUP-0001` → Supplementary Derivation Notes  
- `WF-0001` → Workflow Diagram for Reproducibility  
- `NB-0001` → Jupyter Notebook for Validation  
- `MODEL-0001` → AI Model for Artifact Classification  

---

## Incrementing IDs

- IDs increment sequentially within each artifact type.
- Example: Figures → F-0001, F-0002, F-0003 …
- No gaps allowed unless explicitly reserved.
- Reserved IDs must be documented in registry.

---

## Reserved IDs

- `F-0000`, `T-0000`, etc. may be reserved for testing or templates.
- Reserved IDs must not appear in published papers.

---

## Compliance

- CI/CD pipelines