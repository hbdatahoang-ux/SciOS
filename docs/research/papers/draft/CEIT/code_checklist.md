# Code Checklist: CEIT Adaptive Control

This document catalogs scripts and notebooks used in the CEIT project, including purpose, status, and linkage to supplementary information.

---

## Core Scripts

### `frg_derivation.py`
- **Purpose:** Implements FRG truncation scheme derivation.  
- **Linked SI:** SI-3.  
- **Status:** In progress.  
- **Tests:** Symbolic algebra validation.  

### `bootstrap_resampling.py`
- **Purpose:** Performs bootstrap resampling (N = 5000) for robustness analysis.  
- **Linked SI:** SI-4.  
- **Status:** Finalized.  
- **Tests:** Verified reproducibility index RI = 0.92.  

### `synthetic_validation.py`
- **Purpose:** Generates hybrid datasets with synthetic Gaussian noise.  
- **Linked SI:** SI-5.  
- **Status:** Draft complete.  
- **Tests:** Noise robustness plots validated.  

### `noise_analysis.py`
- **Purpose:** Tests sensitivity of scaling collapse to imaging resolution.  
- **Linked SI:** SI-6.  
- **Status:** In progress.  
- **Tests:** Collapse fidelity stable down to 0.5 µm.  

---

## Analysis Notebooks

### `centerline_extraction.ipynb`
- **Purpose:** Extract filament centerlines from fluorescence images.  
- **Linked Dataset:** D-0001.  
- **Status:** Draft complete.  
- **Tests:** Tangent–tangent correlation pipeline validated.  

### `bic_analysis.ipynb`
- **Purpose:** Bayesian Information Criterion comparison CEIT vs WLC.  
- **Linked Benchmark:** B-0002.  
- **Status:** Finalized.  
- **Tests:** CEIT BIC = 210 vs WLC BIC = 480.  

---

## Testing & Validation
- All scripts must pass unit tests before integration.  
- Results logged in [Benchmarks](ca://s?q=Explain_benchmarks.md).  
- Datasets linked in [Datasets](ca://s?q=Explain_datasets.md).  

---

## Integration
- Code checklist linked to [Supplementary](ca://s?q=Explain_supplementary.md).  
- Updates tracked in [Notes](ca://s?q=Explain_notes.md) and [Roadmap](ca://s?q=Explain_roadmap.md).  
- Registered in [Publications](ca://s?q=Explain_publications.md) and [Citations](ca://s?q=Explain_citations.md).  
