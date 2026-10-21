# SciOS Research Notes

Project:
Scientific Operating System (SciOS)

Status:
Draft

---

## 2026-07-08

### Literature
- Reviewed reproducibility challenges in scientific software.
- Compared SciOS approach with CEIT artifact registries.

### Ideas
- Introduce containerized runtime for reproducible workflows.
- Add entropy‑based scheduling model.
- Explore integration with CI/CD pipelines.

### Theory
Derived preliminary scheduling function (EQ‑0001).  
Drafted kernel skeleton with modular scheduler.

### Figures
Need schematic for **F‑0001** (Kernel Architecture).  
Plan runtime workflow diagram for **F‑0002**.

### Experiments
Initial benchmarks of reproducible execution across environments.  
Structured logging module under review.

### Questions
- How to ensure artifact registry scales across multiple papers?  
- Should runtime include built‑in versioning for datasets?

### Next Actions
- Refine public API draft.  
- Validate scheduler refactor.  
- Update supplementary derivation (SUP‑DER‑0001).
