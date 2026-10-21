# Quality Standards: CEIT Adaptive Control

This document defines quality assurance criteria for the CEIT project, covering code, data, benchmarks, and figures.

---

## Code Quality
- **Code Review:**  
  - All scripts listed in [Code Checklist](ca://s?q=Explain_code_checklist.md) must pass peer review.  
  - Unit tests required before integration.  
  - Version control enforced with changelog entries in [CHANGELOG](ca://s?q=Explain_CHANGELOG.md).  

- **Reproducibility:**  
  - Scripts must produce identical results across runs.  
  - Random seeds documented in [Analysis](ca://s?q=Explain_analysis.md).  

---

## Data Quality
- **Validation:**  
  - Raw datasets stored in [Datasets](ca://s?q=Explain_datasets.md) must be complete and unmodified.  
  - Preprocessing steps documented in [Analysis](ca://s?q=Explain_analysis.md).  

- **Integrity:**  
  - Synthetic datasets clearly labeled.  
  - Metadata logged in [metadata.yml](ca://s?q=Explain_metadata.yml).  

---

## Benchmark Standards
- **Thresholds:**  
  - χ²_red ≤ 1.5 for acceptable fits.  
  - BIC difference ≥ 100 for model preference.  
  - Reproducibility Index (RI) ≥ 0.9.  

- **Validation:**  
  - Benchmarks cataloged in [Benchmarks](ca://s?q=Explain_benchmarks.md).  
  - Results cross-checked with datasets.  

---

## Figure Standards
- **Clarity:**  
  - Figures cataloged in [Figures](ca://s?q=Explain_figures.md).  
  - Captions must describe methods and results.  

- **Format:**  
  - Resolution ≥ 300 dpi.  
  - Journal-ready formatting for [Publications](ca://s?q=Explain_publications.md).  

---

## Governance
- Quality checks logged in [Notes](ca://s?q=Explain_notes.md).  
- Committee approval required for major deliverables ([Governance](ca://s?q=Explain_governance.md)).  
- Updates tracked in [Registry](ca://s?q=Explain_registry.md).  
