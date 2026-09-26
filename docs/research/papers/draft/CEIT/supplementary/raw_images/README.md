# CEIT Raw Images

This directory contains raw, unprocessed images collected during the CEIT research project.  
These images serve as primary visual data before any editing, annotation, or figure generation.

---

# Directory Structure

raw_images/
├── README.md
├── registry.csv
├── RI-0001.png
├── RI-0002.tif
└── ...

Code

---

# Naming Convention

Every raw image uses the following format:

RI-0001
RI-0002
RI-0003
...

Code

Rules

- Prefix: `RI`
- Four-digit numeric identifier
- IDs are immutable
- IDs must never be reused

---

# Required Files

Every raw image consists of:

- Image file (PNG, TIFF, JPEG, etc.)
- Registry entry in `registry.csv`
- Reference inside the manuscript or supplementary materials

Example

registry.csv
↓
RI-0001.png
↓
paper.md

Code

---

# Image Lifecycle

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

Each raw image should:

- Be stored in a lossless format (PNG, TIFF preferred)
- Include metadata in `registry.csv` (author, date, description)
- Use UTF-8 encoding for registry entries
- Remain unmodified (no annotations, no edits)

---

# Registry

Every raw image must appear in:

registry.csv

Code

Example

| ID     | Title                  | Status   |
| ------ | ---------------------- | -------- |
| RI-0001| Microfluidic Channel   | Draft    |

---

# Referencing

Inside the manuscript:

```markdown
See Raw Image RI-0001.
or

markdown
Raw Image (RI-0001)
Best Practices
One raw image = one file

Keep raw images atomic

Do not edit or annotate raw images

Register every raw image before using it

Keep filenames synchronized with IDs

Use consistent formats (prefer PNG/TIFF)

Related Documentation
registry.csv

paper.md

figures/README.md

tables/README.md

equations/README.md

supplementary/README.md

Maintainer
SciOS Research Team
Project: CEIT (Constrained-Induced Elasticity Theory)