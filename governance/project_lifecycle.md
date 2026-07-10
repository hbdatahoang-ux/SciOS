# Project Lifecycle

Version: 1.0  
Status: Draft  
Date: 2026-07-09  
Authors: Governance Committee  

---

## Purpose
This document defines the **lifecycle stages** of project artifacts (datasets, notebooks, manuscripts, submissions, governance files).  
It ensures consistency, reproducibility, and traceability across the project.

---

## Lifecycle Stages

1. **[Draft](ca://s?q=Explain_draft_stage)**  
   - Initial creation of artifact.  
   - Content may be incomplete or exploratory.  
   - Stored in working directories (e.g., `notebooks/`, `datasets/`).  

2. **[Internal Review](ca://s?q=Explain_internal_review_stage)**  
   - Artifact reviewed by team members.  
   - Feedback documented in `review/revision_history.md`.  
   - May include reviewer notes and preliminary responses.  

3. **[Submitted](ca://s?q=Explain_submitted_stage)**  
   - Artifact packaged and sent to external journal/conference.  
   - Stored in `submitted/` with metadata, cover letter, and supplementary files.  
   - Immutable once submitted.  

4. **[Accepted](ca://s?q=Explain_accepted_stage)**  
   - Artifact approved by external reviewers/editors.  
   - Final adjustments made based on acceptance requirements.  
   - Transition prepared for publication.  

5. **[Published](ca://s?q=Explain_published_stage)**  
   - Artifact officially published in journal/conference.  
   - Stored in `published/` with DOI and citation metadata.  
   - Becomes reference point for future work.  

6. **[Archived](ca://s?q=Explain_archived_stage)**  
   - Artifact superseded by newer versions.  
   - Moved to `archived/` for historical record.  
   - No longer actively maintained but remains accessible.  

---

## Governance Rules
- Each stage requires documentation in `revision_history.md`.  
- Metadata (`metadata.yml`) must be updated at every transition.  
- Releases must comply with **[release_policy.md](ca://s?q=Explain_release_policy_file)**.  
- Decisions about lifecycle transitions are recorded in **[decision_process.md](ca://s?q=Explain_decision_process_file)**.  

---

## Notes
- Emergency transitions (e.g., urgent patch releases) may bypass full review but must be documented retroactively.  
- Lifecycle policy is reviewed annually by the governance committee.  
