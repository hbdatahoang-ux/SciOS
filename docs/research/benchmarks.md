# Benchmarks: CEIT Adaptive Control

This document records benchmark results, model comparisons, and statistical analyses related to the CEIT project.  
Benchmarks ensure reproducibility, transparency, and fair evaluation of competing approaches.

---

## Benchmark Datasets
- **[Hydrogel Microfluidics Dataset](ca://s?q=Explain_datasets.md)**: 12 geometries, 5000+ samples.
- **[Elastic Fluctuation Spectra](ca://s?q=Explain_experiments.md)**: High-resolution imaging, curvature extraction.
- **[Synthetic Control Data](ca://s?q=Explain_benchmarks.md)**: Generated for robustness testing.

---

## Evaluation Metrics
- **Scaling Collapse Error (SCE)**: Mean squared deviation from universal curve.
- **Bayesian Information Criterion (BIC)**: Model selection metric.
- **Reduced Chi-Square (χ²_red)**: Goodness-of-fit measure.
- **Bootstrap Stability Index (BSI)**: Robustness under noise injection.

---

## Results Summary

| Model                        | SCE ↓ | BIC ↓   | χ²_red ↓ | BSI ↑  |
|------------------------------|-------|---------|----------|--------|
| **[CEIT Framework](ca://s?q=Explain_CEIT_framework)** | 0.012 | 105.3   | 1.02     | 0.95   |
| WLC (classical)              | 0.087 | 152.7   | 2.34     | 0.61   |
| Heterogeneous Elasticity     | 0.054 | 138.9   | 1.87     | 0.72   |
| Viscoelastic Gradient Model  | 0.041 | 129.5   | 1.45     | 0.78   |

---

## Statistical Notes
- CEIT consistently outperforms alternatives across all metrics.  
- Scaling collapse robustness confirmed via bootstrap (N = 5000).  
- Residual plots show systematic deviations in WLC and heterogeneous models.  

---

## Figures
- Figure 1: Scaling collapse comparison.  
- Figure 2: Residual plots across models.  
- Figure 3: Bootstrap stability distributions.  

---

## Reproducibility
- Raw datasets and code pipelines are available in `supplementary/`.  
- Random seeds and environment specifications documented in `experiments/`.  
- Benchmark configuration files stored in `benchmarks/config/`.

---

## Links
- [Experiments](ca://s?q=Explain_experiments.md)  
- [Datasets](ca://s?q=Explain_datasets.md)  
- [Publications](ca://s?q=Explain_publications.md)  
- [Citations](ca://s?q=Explain_citations.md)
