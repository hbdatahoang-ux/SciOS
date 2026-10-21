# SciOS Artifact Dependency Graph v1.0

Version: 1.0  
Status: Draft  
Authors: SciOS Research Team

---

## Overview
This document defines the rules for modeling dependencies between artifacts in SciOS.  
Artifacts may depend on other artifacts, forming a directed acyclic graph (DAG).  
Dependencies ensure traceability and reproducibility across Figures, Tables, Equations, Datasets, Experiments, Benchmarks, Workflows, Notebooks, Models, and Supplementary materials.

---

## Principles

- **Directed Graph**: Dependencies are directional (A → B).
- **Acyclic**: Circular dependencies are prohibited.
- **Explicit Declaration**: Dependencies must be declared in `metadata.yml`.
- **Granularity**: Dependencies reference artifact IDs, not files.
- **Traceability**: Graph must allow traversal from paper to underlying datasets and experiments.

---

## Dependency Types

| Type | Example |
|------|---------|
| **Figure → Table** | F-0005 depends on T-0002 for data visualization. |
| **Table → Dataset** | T-0002 depends on DATA-0001 for raw data. |
| **Equation → Dataset** | EQ-0003 depends on DATA-0001 for derivation. |
| **Experiment → Workflow** | EXP-0001 depends on WF-0002 for execution steps. |
| **Benchmark → Model** | BM-0001 depends on MODEL-0003 for evaluation. |
| **Supplementary → Equation** | SUP-0001 depends on EQ-0004 for extended proof. |

---

## Example Graph

