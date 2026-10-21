# SciOS Artifact Registry Specification v1.0

Version: 1.0  
Status: Draft  
Authors: SciOS Research Team

---

## Overview
This document defines the structure and rules for artifact registries in SciOS.  
Each artifact collection (Figures, Tables, Equations, Datasets, Experiments, Benchmarks, Workflows, Notebooks, Models, Supplementary) SHALL maintain a `registry.csv` file.

---

## Goals
- Provide authoritative index of artifacts.  
- Ensure consistency between metadata and registry.  
- Enable automated validation in CI/CD.  
- Support traceability across papers and artifacts.  

---

## Registry Format

### Required Columns

| Column | Description |
|--------|-------------|
| **ID** | Unique artifact identifier (e.g., F-0001, T-0002). |
| **Title** | Short descriptive title. |
| **Version** | Semantic version (v1.0.0). |
| **Status** | Lifecycle state (Draft, Review, Approved, Published, Archived). |
| **Paper** | Associated paper/project (e.g., SciOS). |
| **Section** | Paper section referencing artifact. |
| **Folder** | Directory name containing artifact files. |

### Optional Columns

| Column | Description |
|--------|-------------|
| **Author** | Primary author. |
| **Reviewer** | Assigned reviewer. |
| **ApprovedBy** | Person/team approving artifact. |
| **DOI** | Digital Object Identifier if published. |
| **License** | License (default CC-BY-4.0). |
| **Notes** | Additional notes. |

---

## Example Registry

```csv
ID,Title,Version,Status,Paper,Section,Folder
F-0001,SciOS Kernel Architecture,v1.0,Approved,SciOS,Architecture,F-0001
F-0002,Runtime Workflow,v0.1,Draft,SciOS,Methods,F-0002
T-0001,Kernel Components,v1.0,Approved,SciOS,Architecture,T-0001
EQ-0001,Runtime Complexity Equation,v0.2,Review,SciOS,Methods,EQ-0001
DATA-0001,Benchmark Dataset,v1.0,Published,SciOS,Results,DATA-0001
