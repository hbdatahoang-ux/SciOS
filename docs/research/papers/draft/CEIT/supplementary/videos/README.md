# CEIT Videos

This directory contains video recordings and supplementary visual materials for the CEIT research project.  
These videos provide experimental footage, simulation recordings, or explanatory animations that complement the main paper.

---

# Directory Structure

videos/
├── README.md
├── registry.csv
├── V-0001.mp4
├── V-0002.mov
└── ...

Code

---

# Naming Convention

Every video uses the following format:

V-0001
V-0002
V-0003
...

Code

Rules

- Prefix: `V`
- Four-digit numeric identifier
- IDs are immutable
- IDs must never be reused

---

# Required Files

Every video consists of:

- Video file (MP4, MOV, AVI, etc.)
- Registry entry in `registry.csv`
- Reference inside the manuscript or supplementary materials

Example

registry.csv
↓
V-0001.mp4
↓
paper.md

Code

---

# Video Lifecycle

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

Each video should:

- Use a widely supported format (MP4 preferred)
- Include metadata in `registry.csv` (author, date, description)
- Remain unmodified (raw footage stored separately in `raw_images/` if applicable)
- Use UTF-8 encoding for registry entries

---

# Registry

Every video must appear in:

registry.csv

Code

Example

| ID     | Title                  | Status   |
| ------ | ---------------------- | -------- |
| V-0001 | Microfluidic Experiment| Draft    |

---

# Referencing

Inside the manuscript:

```markdown
See Video V-0001.
or

markdown
Video (V-0001)
Best Practices
One video = one file

Keep videos atomic

Provide clear metadata

Register every video before using it

Keep filenames synchronized with IDs

Use consistent formats (prefer MP4)

Related Documentation
registry.csv

paper.md

tables/README.md

figures/README.md

equations/README.md

supplementary/README.md

raw_images/README.md

Maintainer
SciOS Research Team
Project: CEIT (Constrained-Induced Elasticity Theory)