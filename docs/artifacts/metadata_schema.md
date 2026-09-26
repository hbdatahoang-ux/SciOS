# SciOS Artifact Metadata Schema v1.0

Version: 1.0  
Status: Draft  
Authors: SciOS Research Team

---

## Overview
This document defines the metadata schema for all artifact types in SciOS.  
Every artifact MUST include a `metadata.yml` file conforming to this schema.

---

## Required Fields

| Field | Type | Description |
|-------|------|-------------|
| **ID** | String | Unique identifier (e.g., F-0001, T-0002, EQ-0003). |
| **Title** | String | Human-readable title of the artifact. |
| **Paper** | String | Associated paper/project (e.g., SciOS). |
| **Section** | String | Section in the paper where artifact is referenced. |
| **Version** | String | Semantic version (e.g., v1.0.0). |
| **Status** | Enum | Lifecycle state: Draft, Review, Approved, Published, Archived. |
| **Author** | String | Primary author/creator. |
| **Created** | Date | Creation date (YYYY-MM-DD). |
| **LastUpdated** | Date | Last modification date. |

---

## Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| **Reviewer** | String | Assigned reviewer. |
| **ApprovedBy** | String | Person/team approving artifact. |
| **Keywords** | List | Tags for search and indexing. |
| **Description** | Text | Detailed description of artifact. |
| **Purpose** | Text | Purpose or rationale. |
| **Caption** | File | Path to caption.md. |
| **Files** | Map | Paths to associated files (PNG, SVG, CSV, source). |
| **Dependencies** | Map | Related artifacts (Figures, Tables, Equations, Datasets, etc.). |
| **RelatedSections** | List | Paper sections referencing artifact. |
| **License** | String | License (default CC-BY-4.0). |
| **DOI** | String | Digital Object Identifier if published. |
| **Notes** | Text | Additional notes. |

---

## Example

```yaml
ID: F-0001
Title: SciOS Kernel Architecture
Paper: SciOS
Section: Architecture
Version