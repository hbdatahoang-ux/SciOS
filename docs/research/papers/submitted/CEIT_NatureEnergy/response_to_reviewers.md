# Response to Reviewers

We thank the reviewers for their careful evaluation of our manuscript  
**"Geometry-Driven Renormalization of Elastic Fluctuations in Constrained Hydrogel Microfluidics"**.  
We appreciate their constructive comments and suggestions, which have helped us improve the clarity and robustness of the paper.  
Below we provide a point-by-point response.

---

## Reviewer 1

**Comment 1:**  
The manuscript claims universality of the scaling law, but does not provide sufficient robustness checks.  
Please clarify how noise and subsampling affect the scaling collapse.

**Response:**  
We have added a new section in the Supplementary Information (SI-5) detailing bootstrap stability analysis and subsampling tests.  
These results confirm that the scaling collapse is robust to noise injection and dataset subsampling.  
Error bars are now explicitly defined via bootstrap resampling (N > 5000).

---

**Comment 2:**  
The FRG truncation scheme is briefly mentioned but not justified.  
Please provide more details on operator hierarchy and regulator independence.

**Response:**  
We expanded SI-3 to include a full derivation of the flow equation, justification of the truncation scheme, and a discussion of regulator independence.  
This ensures transparency and reproducibility of the FRG framework.

---

## Reviewer 2

**Comment 1:**  
The comparison with heterogeneous elasticity and viscoelastic gradient models is not convincing.  
Please provide quantitative metrics.

**Response:**  
We now include Bayesian Information Criterion (BIC) and χ²_red values in Figure 5 and SI-6.  
These metrics demonstrate that only the CEIT framework reproduces both fluctuation spectra and scaling collapse simultaneously.  
Residual plots confirm systematic