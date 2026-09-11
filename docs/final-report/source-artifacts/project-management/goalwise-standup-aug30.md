**GoalWise**

**Weekly Standup Report**

*Week of August 30, 2026 (Security Week) · MSCS 2101, Group 3*

# **Done This Week**

## **Vishal — Project Manager**

- In charge of security review and coordinating the team to finalize the security features, including the UX and source code – ensure the whole team follows the direction in the review document.

- Lead the acceptance test for ready features SAST review

## **Nati — Backend**

- Target to complete CSV import + AI explain-only layer — positioned as bounded demo increments, explicitly not touching pace-v1 calculation

- Execute the SQAP release-candidate checklist (Appendix A) once CSV/AI increments land

- Support SAST review and perform DAST review on staging

## **Ashutosh — Frontend / UX**

- Continue to optimize UX design based on updated source code and update security features on the UX

- Perform UI streamlining with new security features

- Support DAST review on staging

## **Thanh — QA / Documentation**

- Add two new risks (Deployment drift, UX completeness) to the SPMP register to match what's shown in the CDR deck

- Recommend and gather security risks for Vishal to complete the security review

- Review all security solutions and features for documentation

- Partially performing acceptance tests with Vishal

# **In Progress / Next**

- Review security features and test for release on staging

- Test CSV import + AI explain-only layer with new security features

- Define necessary actions for pending code errors and warnings

- Prepare for rehearsal

# **Blockers / Watch Items**

- SPMP risk register and CDR deck risk list are still out of sync — low urgency but should close before Final

- Frontend Docker image was running as root in the production stage — no USER directive. Added a non-root user.

- 21 other Semgrep warnings — all triaged as false positives or not applicable (mostly i18n label warnings, which don't apply since we're English-only for MVP).
