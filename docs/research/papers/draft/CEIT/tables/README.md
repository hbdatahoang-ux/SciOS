# CEIT Tables

This directory contains all tabular data used in the CEIT research project.

Every table must have a unique identifier and be registered in `registry.csv`.

---

# Directory Structure

tables/
├── README.md
├── registry.csv
├── T-0001.csv
├── T-0002.csv
└── ...

Code

---

# Naming Convention

Every table uses the following format:

T-0001
T-0002
T-0003
...

Code

Rules

- Prefix: `T`
- Four-digit numeric identifier
- IDs are immutable
- IDs must never be reused

---

# Required Files

Every table consists of:

- CSV file
- Registry entry
- Reference inside the manuscript

Example

registry.csv
↓
T-0001.csv
↓
paper.md

Code

---

# Table Lifecycle

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

# CSV Requirements

Each table should:

- Include a header row
- Include measurement units where applicable
- Use UTF-8 encoding
- Use comma-separated values

Example

```csv
Parameter,Value,Unit,Description
Channel Width,800,µm,Microchannel width
Registry
Every table must appear in:

Code
registry.csv
Example

ID	Title	Status
T-0001	Experimental Parameters	Draft


Referencing
Inside the manuscript:

markdown
See Table T-0001.
or

markdown
Table 1 (T-0001)
Versioning
Tables may evolve.

Example

Code
v0.1
v0.2
v1.0
IDs remain unchanged.

Best Practices
One table = one CSV file

Keep tables atomic

Avoid duplicate information

Include units for every numeric column

Register every table before using it

Keep filenames synchronized with IDs

Related Documentation
registry.csv

paper.md

references.bib

figures/README.md

equations/README.md

Maintainer
SciOS Research Team
Project: CEIT (Constrained-Induced Elasticity Theory)