# Final Report Source Artifacts

This directory collects course artifacts used as source material for the final
GoalWise project report. Original submitted files are preserved where available.
DOCX artifacts also include Markdown conversions so report sections can be
revised and cited without editing binary files.

## Artifact Index

| Report source area | Files | Notes |
| --- | --- | --- |
| Proposal / project framing | `proposal/goalwise-product-research-and-sdlc-blueprint.pdf` | Source for problem, stakeholders, scope, and early SDLC framing. |
| PDR material | `pdr/goalwise-3-deck.pdf`, `pdr/goalwise-3-deck.pptx`, `pdr/goalwise-g3-submission.zip`, `pdr/goalwise-g3.pdf`, `pdr/goalwise-group3-slides.pdf` | Source for preliminary architecture, initial scope, and PDR changes. |
| CDR material | `cdr/goalwise-cdr-group3-aug22-2026.pdf`, `cdr/goalwise-cdr-group3-aug22-2026.pptx` | Source for refined architecture, detailed design diagrams, implementation progress, and quality gates. |
| SRS baselines | `srs/goalwise-srs-v1.0.docx`, `srs/goalwise-srs-v1.0.md`, `srs/goal-wise-srs-v1-legacy-source.docx`, `srs/goal-wise-srs-v1-legacy-source.md`, `srs/goalwise-srs-v2.0.docx`, `srs/goalwise-srs-v2.0.md` | Source for final requirements and SRS v2.0 delta analysis. The repo-level current SRS remains `docs/srs/goal-wise-srs-v2.md`. |
| SQAP / STP | `sqap-stp/goalwise-3-sqap-stp.docx`, `sqap-stp/goalwise-3-sqap-stp.md` | Source for verification, validation, test levels, and quality gates. |
| Security review | `security/goalwise-group3-security-review.docx`, `security/goalwise-group3-security-review.md` | Source for threat model, SAST results, dependency review, and residual risk. The repo also has `docs/security-review.md`. |
| UI mockup evidence | `ui-mockups/goalwise-mockup-assets.zip` | Source screenshots for implementation progress, usability discussion, and planned UI streamlining. |
| Project management evidence | `project-management/*` | Weekly standups and status reports for plan-versus-actual, schedule, risk, and team-process retrospective. |

## Still Needed For The Final Report

These sections are not satisfied by a single pre-existing artifact and should be
written from repo evidence, PR history, team memory, and final verification:

- Section 1: executive summary.
- Section 5: implementation account.
- Section 8: governance, intellectual property, accountability, and ethics.
- Section 9: final evolution and maintenance plan, using `docs/production-readiness-rally.md` as a starting point.
- Section 10: project management retrospective, using the standup artifacts and SPMP/proposal material.
- Section 11: lessons learned.
- Appendix B: accountability map.
- Appendix D: final code-review log, unless a separate review-log artifact is later added.

## Import Notes

- Files were copied from `~/Downloads`; the originals were not deleted.
- PDF and PPTX artifacts are retained in their original format because they are
  source submissions and Pandoc does not reliably convert them to structured
  Markdown.
- DOCX artifacts were converted to GitHub-flavored Markdown with Pandoc using
  `--wrap=none`.
- ZIP artifacts are retained as original submitted packages when they contain
  relevant source files.
