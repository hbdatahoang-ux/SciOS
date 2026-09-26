# CEIT Additional Results

This directory contains supplementary or extended results that support the CEIT research project.  
These results include extended analyses, secondary experiments, or computational outputs that complement the main findings.

---

# Directory Structure

additional_results/
├── README.md
├── registry.csv
├── AR-0001.csv
├── AR-0002.md
└── ...

Code

---

# Naming Convention

Every additional result uses the following format:

AR-0001
AR-0002
AR-0003
...

Code

Rules

- Prefix: `AR`
- Four-digit numeric identifier
- IDs are immutable
- IDs must never be reused

---

# Required Files

Every additional result consists of:

- File (CSV, Markdown, or other format)
- Registry entry in `registry.csv`
- Reference inside the manuscript

Example

registry.csv
↓
AR-0001.csv
↓
paper.md

Code

---

# Result Lifecycle

Draft
↓
Reviewed
↓
Approved
↓
Published

Code

Status is recorded in `registry.csv`.

---

# File Requirements

Each result file should:

- Include clear headers (for CSV/TSV)
- Provide metadata (author, version, status, created/modified dates)
- Use UTF-8 encoding
- Include units for numeric data where applicable

Example (CSV):

```csv
Parameter,Value,Unit,Description
Elastic Modulus,120,MPa,Measured under constrained conditions
Registry
Every additional result must appear in:

Code
registry.csv
Example

ID	Title	Status
AR-0001	Extended Elastic Moduli	Draft


Referencing
Inside the manuscript:

markdown
See Additional Result AR-0001.
or

markdown
Additional Result (AR-0001)
Best Practices
One result = one file

Keep results atomic

Provide clear context and metadata

Register every result before using it

Keep filenames synchronized with IDs

Use consistent formatting

Related Documentation
registry.csv

paper.md

tables/README.md

figures/README.md

equations/README.md

supplementary/README.md

Maintainer
SciOS Research Team
Project: CEIT (Constrained-Induced Elasticity Theory)