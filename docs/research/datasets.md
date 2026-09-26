# Datasets: CEIT Adaptive Control

This document describes datasets used in the CEIT project.  
Datasets are essential for reproducibility, benchmarking, and transparency.

---

## Dataset Registry

| ID      | Name                                | Size     | Format   | Source | Notes |
|---------|-------------------------------------|----------|----------|--------|-------|
| D-0001  | Hydrogel Microfluidics Dataset      | 12 GB    | HDF5     | In-house imaging | 12 geometries, 5000+ samples |
| D-0002  | Elastic Fluctuation Spectra         | 8 GB     | CSV/NPZ  | Experimental logs | Curvature extraction from microscopy |
| D-0003  | Synthetic Control Data              | 2 GB     | JSON/CSV | Generated | Robustness testing with noise injection |

---

## Dataset Descriptions

### **[Hydrogel Microfluidics Dataset](ca://s?q=Explain_hydrogel_microfluidics_dataset)**
- **Contents:** Imaging data of hydrogel filaments under geometric confinement.  
- **Samples:** 5000+ across 12 geometries.  
- **Format:** HDF5 with metadata annotations.  
- **Usage:** Benchmarking scaling collapse and universality.  

### **[Elastic Fluctuation Spectra](ca://s?q=Explain_elastic_fluctuation_spectra)**
- **Contents:** Curvature spectra extracted from high-resolution microscopy.  
- **Samples:** 2000+ spectra.  
- **Format:** CSV (raw) and NPZ (processed).  
- **Usage:** Input for FRG analysis and model comparison.  

### **[Synthetic Control Data](ca://s?q=Explain_synthetic_control_data)**
- **Contents:** Artificially generated datasets with controlled noise levels.  
- **Samples:** 1000+ synthetic runs.  
- **Format:** JSON and CSV.  
- **Usage:** Robustness testing, bootstrap validation, error analysis.  

---

## Access & Licensing
- All datasets are released under **CC BY 4.0**.  
- Raw and processed data are stored in `supplementary/datasets/`.  
- Access requires citation of the CEIT project publications.  

---

## Reproducibility Notes
- Random seeds documented in `experiments/config/`.  
- Environment specifications included in `benchmarks/config/`.  
- Data pipelines (MATLAB/Python) provided in `supplementary/code/`.  

---

## Links
- [Benchmarks](ca://s?q=Explain_benchmarks.md)  
- [Experiments](ca://s?q=Explain_experiments.md)  
- [Publications](ca://s?q=Explain_publications.md)  
- [Citations](ca://s?q=Explain_citations.md)
