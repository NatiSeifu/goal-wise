# **Weekly Stand-Up — Team Status Report · Week 9**

**Team:** GoalWise · **Week:** 9 · **Date:** Sept. 5, 2026 · **Members reporting:** Nati, Vishal, Ashutosh, Thanh

### **1. Done since last stand-up**

- Advanced GoalWise to **v0.3.0**, including the first working **AI summarization/explanation feature** while keeping the deterministic pace-v1 engine as the source of truth for all financial calculations.

- Continued **UI/UX streamlining**, improving the core workflow and overall presentation while leaving room for final cosmetic refinements.

- Completed follow-up work from the security review, including additional verification of authentication, CSRF protections, ownership controls, input validation, and dependency safety.

- Expanded testing around **cross-user resource access** after the security review identified insufficient automated negative-authorization coverage. The goal is to ensure that one authenticated user cannot access or modify another user's goals or financial information.

- Continued CI verification with automated tests, **Ruff** linting, and **mypy** type checking while manually exercising v0.3.0 in staging.

### **2. Plan for next week**

- Complete final system, regression, security, and manual acceptance testing — **all**.

- Continue UI polish and address any late usability issues or bugs discovered before the final demo — **Ashutosh, Nati**.

- Verify the new AI summarization workflow while ensuring AI remains explanatory and cannot modify official pace-v1 financial results — **Nati, Thanh**.

- Evaluate one or two bounded **experimental features** beyond the original MVP specification to exercise agile iteration without destabilizing the verified core — **all**.

- Prepare a stable **v1.0.0 production release** representing the completed specification; if appropriate, keep more experimental post-MVP functionality separate as a later v1.1.0-style increment.

### **3. Blockers / risks / help needed**

No current blockers.

The main risk is **scope creep** now that the original core specification has largely been satisfied. Experimental features could introduce regressions immediately before the final demo. We will therefore treat v1.0.0 as the stable, specification-compliant baseline and keep any aggressive post-MVP additions bounded, testable, and removable without affecting the deterministic financial core.

### **4. Member contributions**

- **Nati** — did: v0.3.0 technical implementation, AI-summary integration, security/testing follow-up, and backend verification · next: finalize AI behavior, resolve late bugs, and prepare the release candidate.

- **Vishal** — did: tracked security/release readiness and coordinated testing against project requirements · next: oversee final acceptance and release-readiness checks.

- **Ashutosh** — did: continued frontend/UI/UX streamlining and tested the updated user workflow · next: final UI polish and usability improvements for the demo.

- **Thanh** — did: supported QA/security verification, requirements tracking, and testing documentation · next: coordinate final regression/acceptance testing and verify remaining test evidence.

### **5. Deliverable status**

**Threat model** — complete. CSRF and IDOR/BOLA remain key modeled threats for authenticated financial and goal-mutation endpoints; mitigations include per-session CSRF protection and server-side user_id ownership enforcement.

**SAST scan** — completed and findings triaged. The previously identified real Docker security finding was corrected; remaining reported warnings were reviewed rather than automatically accepted as vulnerabilities.

**AI-code review + dependencies** — reviewed. Dependency verification produced a potentially suspicious package finding that required additional investigation rather than trusting the dependency name at face value. No major confirmed dependency vulnerability was accepted into the release path, and dependency provenance remains part of our review process.

**Fixes/resilience** — security follow-up expanded negative authorization coverage for **cross-user access**, addressing a gap identified during the initial review. Existing CSRF/session protections, ownership checks, input validation, CI gates, and staging verification remain in place. GoalWise v0.3.0 also preserves the architectural boundary that AI may explain deterministic results but cannot become the source of financial calculations.

### **6. AI & tools note**

AI assisted with implementation of the new summarization feature, code/security review, and test planning. As with previous increments, AI output was independently checked against the SRS, architecture, and actual repository behavior.

This week's follow-up demonstrated two useful review outcomes. First, dependency review surfaced a **potentially questionable dependency** that required manual investigation instead of assuming an AI-suggested or plausibly named package was safe. Second, the security review showed that manually tracing ownership checks was not enough evidence by itself: **cross-user negative-test coverage was insufficient**, so we expanded testing to verify that User B cannot access or modify User A's private GoalWise resources.

With the original MVP functionality largely in place, our focus is shifting from feature completion toward **final verification, UI polish, release stability, and controlled experimentation** before the final demo.
