# Release Policy

Version: 1.0  
Status: Draft  
Date: 2026-07-09  
Authors: Governance Committee  

---

## Purpose
This document defines the **release policy** for project artifacts (datasets, notebooks, manuscripts, software).  
It ensures consistency, transparency, and reproducibility across all releases.

---

## Release Types
- **[Major Release](ca://s?q=Explain_major_release)**: Introduces significant new features, structural changes, or governance updates.  
- **[Minor Release](ca://s?q=Explain_minor_release)**: Adds incremental improvements, bug fixes, or small enhancements.  
- **[Patch Release](ca://s?q=Explain_patch_release)**: Fixes urgent issues without altering functionality.  
- **[Pre-release](ca://s?q=Explain_pre_release)**: Beta or candidate versions for testing before official release.  

---

## Versioning
- Follows **[Semantic Versioning](ca://s?q=Explain_semantic_versioning)**: `MAJOR.MINOR.PATCH`.  
- Pre-releases use suffixes like `-beta`, `-rc1`.  
- Metadata (`metadata.yml`) must include version number and release date.  

---

## Approval Process
1. **Proposal**: Release candidate proposed in `governance/proposals/`.  
2. **Review**: Governance committee validates compliance with standards.  
3. **Testing**: Validation notebooks and CI pipelines must pass.  
4. **Approval**: Majority vote required for major/minor releases.  
5. **Publication**: Release artifacts moved to `published/` directory.  

---

## Documentation
- Each release must include a **[changelog](ca://s?q=Explain_changelog_file)** in `governance/changelog.md`.  
- Release notes must summarize changes, improvements, and known issues.  
- Artifacts must be tagged in repository for traceability.  

---

## Archival
- Superseded releases are moved to `archived/`.  
- Archived versions remain accessible but are not maintained.  
- Lifecycle tracked in `governance/revision_history.md`.  

---

## Notes
- Emergency patches may bypass full approval but must be documented retroactively.  
- Releases must comply with licensing and metadata standards.  
- This policy is reviewed annually and updated as needed.  
