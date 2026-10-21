# CEIT Supplementary Materials

This directory contains supplementary materials for the CEIT research project.  
These files provide additional context, extended data, or supporting documentation that complements the main paper.

---

# Directory Structure

supplementary/
├── README.md
├── registry.csv
├── SUP-0001.md
├── SUP-0002.pdf
└── ...

Code

---

# Naming Convention

Every supplementary item uses the following format:

SUP-0001
SUP-0002
SUP-0003
...

Code

Rules

- Prefix: `SUP`
- Four-digit numeric identifier
- IDs are immutable
- IDs must never be reused

---

# Required Files

Every supplementary item consists of:

- File (Markdown, PDF, or other format)
- Registry entry in `registry.csv`
- Reference inside the manuscript

Example

registry.csv
↓
SUP-0001.md
↓
paper.md

Code

---

# Lifecycle

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

# Registry

Every supplementary item must appear in:

registry.csv

Code

Example

| ID      | Title                  | Status   |
| ------- | ---------------------- | -------- |
| SUP-0001| Extended Derivation    | Draft    |

---

# Referencing

Inside the manuscript:

```markdown
See Supplementary Material SUP-0001.
or

markdown
Supplementary Information (SUP-0001)
Best Practices
One supplementary item = one file

Keep items atomic

Avoid duplicate information

Register every item before using it

Keep filenames synchronized with IDs

Related Documentation
registry.csv

paper.md

tables/README.md

figures/README.md

equations/README.md

Maintainer
SciOS Research Team
Project: CEIT (Constrained-Induced Elasticity Theory)