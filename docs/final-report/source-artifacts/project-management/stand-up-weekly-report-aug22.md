# **Weekly Stand-Up — Team Status Report · Week 7**

**Team:** GoalWise · **Week:** 7 · **Date:** Aug 22, 2026 · **Members reporting:** Nati, Vishal, Ashutosh, Thanh

### **1. Done since last stand-up**

- Completed and presented the **Critical Design Review (CDR)** for GoalWise v0.2.0, covering changes since the PDR, detailed architecture/design, implementation progress, testing strategy, risks, and the plan through final release.

- Completed the **SQAP + Software Testing Plan (STP)**, establishing our quality objectives, testing levels, requirements traceability, defect process, release criteria, and AI-verification practices.

- Continued testing the existing v0.2.0 staging workflow rather than expanding scope this week. Current testing focuses on verifying the integrated frontend/backend flow, deterministic pace calculations, authentication/CSRF behavior, and SRS conformance.

- Continued using automated CI testing, **Ruff** linting, and **mypy** type checking alongside manual staging verification.

### **2. Plan for next week**

- Conduct the next **security review**, including authentication/authorization, CSRF, user-data isolation, dependency/security checks, and other security requirements — Nati, Thanh.

- Begin implementing **AI-generated summaries/explanations** while keeping all official financial calculations deterministic and backend-owned — Nati.

- Refine and streamline the **UI/UX** based on manual testing so the core GoalWise workflow is smoother and more intuitive — Ashutosh, all.

- Broaden manual, system, and acceptance testing and resolve outstanding defects — all.

- Once the application is stable and passes release-quality checks, begin ramping up for the **production deployment**.

### **3. Blockers / risks / help needed**

No current blockers, and no major corrective CDR feedback was identified.

The primary risk is introducing new AI and UI functionality while approaching the final release. We are mitigating this by keeping AI outside the deterministic pace-v1 financial engine and requiring the existing core workflow to continue passing our quality gates as new functionality is introduced.

### **4. Member contributions**

- **Nati** — did: technical testing, CDR preparation, and outlined the technical plan for the remaining development period · next: security review, AI-summary implementation, and release preparation.

- **Vishal** — did: tracked project progress against planned milestones and performed application testing · next: continue release-readiness and requirements tracking.

- **Ashutosh** — did: investigated UI/UX improvements and collaborated on the SQAP/STP · next: streamline the interface and improve usability.

- **Thanh** — did: developed and documented the SQAP/STP and testing strategy · next: coordinate broader testing, traceability, and security verification.

### **5. Deliverable status**

**CDR deck** — completed and presented; covers the layered modular architecture, detailed module/data design, v0.2.0 implementation progress, verification strategy, risks, and final development plan.

**SQAP + STP** — completed. Defines unit, integration, system, and acceptance testing; requirements-to-test traceability; golden tests for the pace-v1 engine; security/accessibility/performance testing; defect handling; and release-quality gates.

**Testing** — CI remains active with automated tests, Ruff linting, and mypy type checking. Manual staging and SRS workflow testing are continuing, with broader security, system, cross-browser, accessibility, and acceptance testing planned as we move toward the release candidate.

### **6. AI & tools note**

AI assisted with implementation, review, documentation, and preparation of CDR/SQAP materials, but AI-generated output is not treated as authoritative. Our SQAP specifically addresses the **spec-conformance trap**: an AI-generated implementation and AI-generated test can agree with each other while both disagree with the SRS.

Testing and review have therefore emphasized independently verified expected results, requirement-linked tests, manual staging workflows, and human-added edge cases. Previous review already caught hosted CSRF/cookie behavior and a goal-archive workflow gap that were not obvious from checking backend code alone. Going forward, the same verification approach will be applied to the security review and AI-summary increment before production release.
