# Benchmarks Catalog: CEIT Adaptive Control

This document catalogs benchmark tests and performance metrics used to validate CEIT against classical models.

---

## B-0001 — χ²_red Comparison
- **Description:** Reduced chi-squared analysis comparing CEIT vs WLC fits.  
- **Metric:** χ²_red (lower is better).  
- **Result:** CEIT = 1.02, WLC = 5.47.  
- **Status:** Finalized.  
- **Notes:** Referenced in Figure 6 (Residual plots).  

---

## B-0002 — Bayesian Information Criterion (BIC)
- **Description:** Model selection criterion comparing CEIT vs WLC.  
- **Metric:** BIC (lower is better).  
- **Result:** CEIT = 210, WLC = 480.  
- **Status:** Finalized.  
- **Notes:** Referenced in Figure 6 (Comparison metrics).  

---

## B-0003 — Fluctuation Spectra Deviation
- **Description:** Mode-dependent distortion analysis across geometries.  
- **Metric:** Deviation region q > 4.  
- **Result:** CEIT residual error ~5× lower than WLC.  
- **Status:** Finalized.  
- **Notes:** Referenced in Figure 2 (Fluctuation spectra).  

---

## B-0004 — Reproducibility Score
- **Description:** Bootstrap resampling robustness test.  
- **Metric:** Reproducibility index (RI).  
- **Result:** RI = 0.92 (CEIT), RI = 0.65 (WLC).  
- **Status:** Draft complete.  
- **Notes:** Linked to SI-4.  

---

## B-0005 — Resolution Sensitivity
- **Description:** Sensitivity of scaling collapse to imaging resolution.  
- **Metric:** Collapse fidelity score.  
- **Result:** CEIT stable down to 0.5 µm resolution.  
- **Status:** In progress.  
- **Notes:** Linked to SI-6.  

---

## Integration
- Benchmarks referenced in [Notes](ca://s?q=Explain_notes.md) and [Roadmap](ca://s?q=Explain_roadmap.md).  
- Linked to [Datasets](ca://s?q=Explain_datasets.md) and [Supplementary](ca://s?q=Explain_supplementary.md).  
- Registered in [Publications](ca://s?q=Explain_publications.md) and [Citations](ca://s?q=Explain_citations.md).  
