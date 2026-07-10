# Supplementary Information: CEIT Adaptive Control

This document catalogs supplementary figures, datasets, and derivations supporting the CEIT project.

---

## SI-3 — FRG Derivation
- **Content:** Full derivation of Functional Renormalization Group (FRG) truncation scheme.  
- **Figures:** Flow diagrams, regulator independence plots.  
- **Status:** In progress.  
- **Notes:** Reviewer feedback requested explicit regulator discussion.  

---

## SI-4 — Bootstrap Resampling
- **Content:** Robustness test of scaling collapse under subsampling.  
- **Figures:** Bootstrap distribution (N = 5000), error bars.  
- **Status:** Finalized.  
- **Notes:** Added per meeting decision (2026-06-15).  

---

## SI-5 — Synthetic Dataset Validation
- **Content:** Validation of hybrid datasets combining experimental and synthetic data.  
- **Figures:** Noise robustness plots, dataset comparison.  
- **Status:** Draft complete.  
- **Notes:** Supports reproducibility claims.  

---

## SI-6 — Noise Robustness Analysis
- **Content:** Sensitivity of scaling collapse to imaging resolution and noise.  
- **Figures:** Resolution-dependent collapse plots, χ²_red metrics.  
- **Status:** In progress.  
- **Notes:** Minimal dataset size for reproducibility under investigation.  

---

## Code Checklist
- **Repository:** `/code/CEIT/`  
- **Scripts:**  
  - `frg_derivation.py` → SI-3  
  - `bootstrap_resampling.py` → SI-4  
  - `synthetic_validation.py` → SI-5  
  - `noise_analysis.py` → SI-6  
- **License:** CC BY 4.0  

---

## Integration
- Supplementary figures stored in `/figures/supplementary/`.  
- Referenced in [Notes](ca://s?q=Explain_notes.md) and [Roadmap](ca://s?q=Explain_roadmap.md).  
- Linked in [Publications](ca://s?q=Explain_publications.md) and [Citations](ca://s?q=Explain_citations.md).  
