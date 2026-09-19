# Integration Map: CEIT Adaptive Control

This document describes how all components of the CEIT project connect into a unified management system.

---

## Notes & Roadmap
- **[Notes](ca://s?q=Explain_notes.md):** Meeting logs, brainstorming, decisions, action items.  
- **[Roadmap](ca://s?q=Explain_roadmap.md):** High-level milestones and timelines.  
- **Integration:** Notes feed into roadmap updates; roadmap milestones reference datasets, figures, and publications.  

---

## Figures & Supplementary
- **[Figures](ca://s?q=Explain_figures.md):** Core and supplementary figures catalog.  
- **[Supplementary](ca://s?q=Explain_supplementary.md):** SI-3 to SI-6 derivations, robustness tests, validation.  
- **Integration:** Figures referenced in notes and publications; supplementary linked to code scripts.  

---

## Datasets & Benchmarks
- **[Datasets](ca://s?q=Explain_datasets.md):** Catalog of experimental, synthetic, and resampled datasets.  
- **[Benchmarks](ca://s?q=Explain_benchmarks.md):** Quantitative metrics (χ²_red, BIC, reproducibility scores).  
- **Integration:** Benchmarks validated against datasets; datasets referenced in supplementary and analysis.  

---

## Experiments & Methods
- **[Experiments](ca://s?q=Explain_experiments.md):** Planned and executed experiments (E-0001, …).  
- **[Methods](ca://s?q=Explain_methods.md):** Detailed protocols for fabrication, imaging, modeling.  
- **Integration:** Methods define experimental design; experiments generate datasets; datasets feed benchmarks.  

---

## Analysis & Code
- **[Analysis](ca://s?q=Explain_analysis.md):** Pipeline from preprocessing → statistical tests → visualization.  
- **[Code Checklist](ca://s?q=Explain_code_checklist.md):** Scripts and notebooks linked to SI-3 to SI-6.  
- **Integration:** Code implements analysis pipeline; analysis validates benchmarks; outputs feed figures.  

---

## Publications & Citations
- **[Publications](ca://s?q=Explain_publications.md):** Registry of drafts, submissions, accepted papers.  
- **[Citations](ca://s?q=Explain_citations.md):** Centralized bibliography.  
- **Integration:** Publications reference figures, datasets, benchmarks; citations linked to metadata.  

---

## Governance
- Weekly sync meetings logged in notes.  
- Major decisions require committee approval.  
- All updates merged into main branch after validation.  

---

## Summary Workflow
1. **Methods** → define protocols.  
2. **Experiments** → generate raw data.  
3. **Datasets** → store processed data.  
4. **Analysis** → run statistical tests.  
5. **Benchmarks** → validate models.  
6. **Figures & Supplementary** → visualize results.  
7. **Notes & Roadmap** → track progress.  
8. **Code Checklist** → ensure reproducibility.  
9. **Publications & Citations** → finalize outputs.  
