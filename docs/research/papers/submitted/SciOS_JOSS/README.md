# Submission Package – SciOS to JOSS

Version: 1.0  
Status: Submitted  
Date: 2026-07-08  
Authors: SciOS Development Team

---

## Overview
This directory contains the **submission package** for the paper describing the *SciOS* software, submitted to the *Journal of Open Source Software (JOSS)*.  
It includes the manuscript, source files, and metadata required by the journal.

---

## Structure
SciOS_JOSS/
├── README.md        # Documentation of submission package
├── manuscript.pdf   # Final manuscript submitted
├── source/          # Source files (code snippets, figures, tables)
└── metadata.yml     # Metadata for submission (authors, affiliations, keywords, software info)

Code

---

## Usage
- **manuscript.pdf**: Final version of the paper submitted to JOSS.  
- **source/**: Contains LaTeX source, figures, tables, and code snippets used to generate the manuscript.  
- **[metadata.yml](ca://s?q=Explain_metadata_file)**: Machine-readable metadata including authors, affiliations, keywords, software repository link, and license information.  

---

## Best Practices
- Ensure manuscript follows JOSS guidelines (short paper, focus on software contribution).  
- Metadata must include repository URL, license, and installation instructions.  
- Source files should allow exact reproduction of the submitted manuscript.  
- Keep submission artifacts immutable once sent to the journal.  

---

## Lifecycle
Submission artifacts follow the standard lifecycle ([lifecycle.md](ca://s?q=Explain_Artifact_Lifecycle)):

Draft → Internal Review → Submitted → Accepted → Published → Archived  

---

## Notes
- This package is frozen at the time of submission.  
- Any post-submission changes must be tracked in `review/revision_history.md`.  
- Accepted versions will be moved to `published/`.