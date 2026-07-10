# SciOS Artifact Validation Rules v1.0

Version: 1.0  
Status: Draft  
Authors: SciOS Research Team

---

## Overview
This document defines the validation rules applied to all artifacts in SciOS.  
Validation ensures consistency, traceability, reproducibility, and compliance with the Artifact Specification.

---

## Validation Categories

1. **Metadata Validation**
   - `metadata.yml` must exist.
   - All required fields present (ID, Title, Version, Status, Author, Created, LastUpdated).
   - Field types must match schema ([metadata_schema.md](ca://s?q=Explain_Metadata_Schema)).
   - Lifecycle state must be valid ([lifecycle.md](ca://s?q=Explain_Artifact_Lifecycle)).

2. **Naming Validation**
   - Artifact ID must follow [naming convention](ca://s?q=Explain_Artifact_Naming_Convention).
   - Folder name must match artifact ID.
   - File names must match metadata references.

3. **Registry Validation**
   - Artifact must appear in `registry.csv`.
   - Registry entry must match metadata fields.
   - No duplicate IDs.
   - Status and version consistent.

4. **Dependency Validation**
   - Dependencies declared in metadata.
   - No circular dependencies.
   - All referenced artifacts must exist and be valid.

5. **File Validation**
   - Required files must exist (PNG/SVG for figures, CSV/XLSX for tables, equation.md for equations, etc.).
   - Source file present (draw.io, notebook.ipynb, etc.).
   - Caption file present (`caption.md`).
   - Files accessible and non-empty.

6. **Lifecycle Validation**
   - Transitions must follow lifecycle rules.
   - Artifacts cannot skip states.
   - Archived artifacts immutable.

7. **Versioning Validation**
   - Version must follow semantic versioning (Major.Minor.Patch).
   - Increment rules enforced (no rollback without archival).

---

## CI/CD Enforcement

- Automated checks run on every commit:
  - Metadata schema validation.
  - Registry consistency.
  - Dependency graph analysis.
  - File existence and integrity.
  - Lifecycle compliance.
  - Versioning rules.

- Artifacts failing validation cannot transition to **Approved** or **Published**.

---

## Compliance Checklist

- ✅ Metadata complete and valid.  
- ✅ Registry entry exists and matches metadata.  
- ✅ Dependencies declared and resolved.  
- ✅ Files present and accessible.  
- ✅ Lifecycle state updated consistently.  
- ✅ Versioning follows semantic rules.  

---

## Notes

Validation rules apply to all artifact types: Figures, Tables, Equations, Datasets, Experiments, Benchmarks, Workflows, Notebooks, Models, Supplementary.  
Artifacts not passing validation SHALL be rejected by the CI/CD pipeline.
