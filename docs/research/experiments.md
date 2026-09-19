# Experiments: CEIT Adaptive Control

This document records experimental design, procedures, parameters, and key results for the CEIT project.  
Experiments validate theoretical predictions and provide reproducible evidence for benchmarks.

---

## Experiment Registry

| ID      | Name                                | Dataset   | Methodology | Status   |
|---------|-------------------------------------|-----------|-------------|----------|
| E-0001  | Hydrogel Confinement Imaging        | D-0001    | Microscopy  | Completed |
| E-0002  | Elastic Fluctuation Spectra         | D-0002    | Curvature Extraction | Completed |
| E-0003  | Synthetic Noise Injection           | D-0003    | Simulation  | Completed |
| E-0004  | FRG Flow Equation Validation        | D-0002    | Functional RG | Ongoing |

---

## Experiment Descriptions

### **[Hydrogel Confinement Imaging](ca://s?q=Explain_hydrogel_confinement_experiment)**
- **Objective:** Capture high-resolution images of hydrogel filaments under geometric confinement.  
- **Setup:** Confocal microscopy, 40x objective, controlled humidity.  
- **Parameters:** 12 geometries, 5000+ samples.  
- **Results:** Imaging dataset (D-0001) used for scaling collapse analysis.  

### **[Elastic Fluctuation Spectra](ca://s?q=Explain_elastic_fluctuation_experiment)**
- **Objective:** Extract curvature spectra from hydrogel filaments.  
- **Setup:** Image processing pipeline (MATLAB/Python).  
- **Parameters:** 2000+ spectra, resolution 0.1 µm.  
- **Results:** Dataset (D-0002) used for FRG fitting and model comparison.  

### **[Synthetic Noise Injection](ca://s?q=Explain_synthetic_noise_experiment)**
- **Objective:** Test robustness of scaling collapse under noise.  
- **Setup:** Simulation pipeline with controlled Gaussian noise.  
- **Parameters:** Noise levels σ = 0.01–0.1.  
- **Results:** Dataset (D-0003) confirms robustness; bootstrap stability index BSI = 0.95.  

### **[FRG Flow Equation Validation](ca://s?q=Explain_FRG_flow_experiment)**
- **Objective:** Validate truncation scheme and regulator independence.  
- **Setup:** Functional Renormalization Group (FRG) solver.  
- **Parameters:** Operator hierarchy up to quartic order.  
- **Results:** Ongoing; preliminary fits consistent with universality class predictions.  

---

## Key Results
- Scaling collapse robust across geometries and noise levels.  
- CEIT framework outperforms WLC and heterogeneous models in χ²_red and BIC metrics.  
- Bootstrap analysis confirms reproducibility with N = 5000 resamples.  

---

## Reproducibility
- Raw imaging data stored in `supplementary/datasets/`.  
- Analysis pipelines available in `supplementary/code/`.  
- Random seeds and environment specifications documented in `experiments/config/`.  

---

## Links
- [Datasets](ca://s?q=Explain_datasets.md)  
- [Benchmarks](ca://s?q=Explain_benchmarks.md)  
- [Publications](ca://s?q=Explain_publications.md)  
- [Citations](ca://s?q=Explain_citations.md)
