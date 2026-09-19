# Methods: CEIT Adaptive Control

This document outlines planned experimental and analytical methods for the CEIT project.  
Currently, methods are proposed but not yet executed.

---

## Microfluidic Fabrication
- **Planned Approach:** Soft lithography in PDMS with straight, serpentine, and pillar array geometries.  
- **Parameters:** Channel depth = 1 µm, width = 5 µm, pillar spacing = 2 µm.  
- **Purpose:** Confinement of DNA filaments under controlled geometries.  

---

## Fluorescence Imaging
- **Planned Approach:** Single-molecule fluorescence microscopy.  
- **Setup:** Confocal microscope, λ = 488 nm excitation, EMCCD detection.  
- **Purpose:** Capture filament trajectories and curvature under confinement.  

---

## Data Extraction
- **Planned Approach:** Image analysis pipeline for centerline extraction.  
- **Tools:** Python scripts (`centerline_extraction.py`), tangent–tangent correlation analysis.  
- **Purpose:** Quantify local persistence length Lₚ(s).  

---

## Theoretical Modeling
- **Planned Approach:** CEIT framework with spatially varying κ(s).  
- **Tools:** Symbolic algebra (SymPy), numerical simulation (NumPy/SciPy).  
- **Purpose:** Compare CEIT predictions vs WLC baseline.  

---

## Statistical Analysis
- **Planned Approach:** χ²_red, Bayesian Information Criterion (BIC), bootstrap resampling (N = 5000).  
- **Tools:** `bootstrap_resampling.py`, `bic_analysis.py`.  
- **Purpose:** Validate reproducibility and robustness.  

---

## Integration
- Methods linked to [Experiments](ca://s?q=Explain_experiments.md), [Datasets](ca://s?q=Explain_datasets.md), and [Benchmarks](ca://s?q=Explain_benchmarks.md).  
- Updates tracked in [Notes](ca://s?q=Explain_notes.md) and [Roadmap](ca://s?q=Explain_roadmap.md).  
