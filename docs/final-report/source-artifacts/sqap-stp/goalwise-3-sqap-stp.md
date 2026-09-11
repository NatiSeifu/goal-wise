**GoalWise**

**Software Quality Assurance Plan (SQAP)\
and Software Testing Plan (STP)**

*Goal-Oriented Budgeting and Weekly Spending Pace*

| **Course**  | MSCS 2101 - Software Engineering |
|-------------|----------------------------------|
| **Team**    | Group 3                          |
| **Version** | 1.0                              |
| **Date**    | August 2026                      |

# Document Scope

This document combines the Software Quality Assurance Plan and the Software Testing Plan required for the GoalWise project. It follows the structure of IEEE Std 730-1998 and expands Section 7 into a project-specific testing plan. The GoalWise SRS Version 2.0 is the normative baseline for testing. Where the older SPMP and the SRS differ, SRS Version 2.0 controls the MVP scope.

# 1. Purpose

This Software Quality Assurance Plan (SQAP) and Software Testing Plan (STP) define how Group 3 will verify and validate the GoalWise MVP. GoalWise is a responsive budgeting web application that allows a user to pursue one active savings goal using a deterministic weekly safe-to-spend calculation. The official financial result is calculated by the backend using the pace-v1 algorithm. AI is not permitted to calculate, modify, or override official financial results.

The objectives of this plan are to:

- Verify that the implementation conforms to the GoalWise SRS Version 2.0.

- Validate that the product is usable and fit for its intended purpose.

- Ensure that every Must requirement has test evidence before release.

- Detect functional, security, reliability, performance, accessibility, and usability defects before deployment.

- Establish a repeatable process for reporting, prioritizing, correcting, and retesting defects.

- Prevent AI-generated code or AI-generated tests from being accepted without independent human verification.

- Minimize defects in Alpha, Beta, and final release candidates.

The GoalWise SRS Version 2.0 is the normative requirements baseline. CSV transaction import and runtime AI explanations are excluded from MVP acceptance. The MVP instead uses manual financial inputs and provides a static AI Future guardrail page.

# 2. Reference Documents

> 1\. GoalWise Software Requirements Specification (SRS), Version 2.0.
>
> 2\. GoalWise Software Project Management Plan (SPMP), Version 1.0.
>
> 3\. GoalWise Software Design Description (SDD).
>
> 4\. IEEE Std 730-1998, Software Quality Assurance Plans.
>
> 5\. OWASP Application Security Verification Standard (ASVS).
>
> 6\. NIST Secure Software Development Framework (SSDF).
>
> 7\. WCAG 2.2 Level AA.
>
> 8\. GoalWise architecture decision records.
>
> 9\. GoalWise test cases, test reports, and requirements traceability matrix.

Where the SPMP and SRS differ, SRS Version 2.0 controls the implementation and testing baseline.

# 3. Management

## 3.1 Organization

Quality assurance is integrated into the four-person GoalWise development team rather than being a separate organization.

| **Team Member** | **Quality Responsibility** |
|----|----|
| Vishal | Project management, schedule, backlog, change approval, release readiness |
| Nati | Backend, APIs, pace-v1 engine, database, technical verification |
| Ashutosh | Frontend, UI/UX, usability and accessibility |
| Thanh | QA lead, testing, defect tracking, documentation, traceability |

Thanh serves as the primary QA and documentation owner. Developers are responsible for unit and integration testing of the code they implement, but a developer shall not be the sole approver of their own change.

## 3.2 Quality Responsibilities

The QA lead will:

- Maintain the test plan and test evidence.

- Maintain requirement-to-test traceability.

- Review CI results and coverage.

- Coordinate system, regression, security, accessibility, and acceptance testing.

- Log and classify defects.

- Verify corrective actions before closure.

- Confirm release quality gates.

The Project Manager will make release decisions with the team. Final academic acceptance is performed by the course instructor.

## 3.3 Quality Objectives

- 100% of approved pace-v1 golden tests pass.

- At least 90% branch coverage for the pace engine.

- At least 75% backend line coverage.

- All Must requirements have passing verification evidence.

- No unresolved Critical or High security findings exist at release.

- All core workflows remain functional without any AI service dependency.

- No release-blocking accessibility, reliability, or data-isolation defects remain.

# 4. Documentation

The project will maintain the following controlled documents:

| **Document** | **Owner** | **Purpose** |
|----|----|----|
| SRS v2.0 | Thanh | Normative product requirements |
| SPMP | Vishal | Schedule, responsibilities, risks and project controls |
| SDD | Nati | Architecture and detailed design |
| SQAP/STP | Thanh | Quality and testing strategy |
| Requirements Traceability Matrix | Thanh | Requirement-to-test mapping |
| Test Cases | QA + developers | Repeatable verification procedures |
| Test Report | Thanh | Test execution results |
| Defect Log | Thanh | Defect status and corrective action |
| User Guide | Ashutosh | End-user instructions |
| Deployment Guide | Nati | Release and recovery procedures |
| ADRs | Team | Important technical decisions |

Documents will be stored in the project repository and versioned. Major revisions will receive a new document version. Testing will be based primarily on the SRS rather than on UI mockups. Mockups are non-normative where their values conflict with the SRS.

# 5. Standards, Practices, Conventions, and Metrics

## 5.1 Coding Standards

- Python/FastAPI backend: PEP 8 compatible formatting and linting.

- React/Next.js frontend: ESLint and consistent formatter rules.

- REST APIs: /api/v1 versioning and structured JSON contracts.

- Money values: integer cents internally.

- Dates and timestamps: ISO 8601.

- Database access: parameterized operations.

- Secrets: environment-managed and never committed to source control.

- Naming and comments should make business logic understandable without depending on AI-generated explanations.

## 5.2 Development Practices

- Feature branches.

- Pull requests before merge.

- Protected main branch.

- At least one reviewer other than the author.

- Automated CI tests.

- Static analysis and linting.

- Dependency scanning.

- Requirement-linked test cases.

- Regression testing after defect fixes.

- Semantic release tagging.

No AI-generated code may bypass normal review.

## 5.3 Quality Metrics

| **Metric**                                 | **Target**          |
|--------------------------------------------|---------------------|
| Approved pace-v1 golden tests passed       | 100%                |
| Pace-engine branch coverage                | \>= 90%             |
| Backend line coverage                      | \>= 75%             |
| Must requirements with test evidence       | 100%                |
| Critical/High security findings at release | 0                   |
| CI build pass rate for release candidate   | 100%                |
| Failed regression tests at release         | 0                   |
| Critical accessibility violations          | 0                   |
| First-time usability success               | \>= 80%             |
| Defect count by severity                   | Tracked each sprint |
| Reopened defects                           | Tracked             |
| Build failures                             | Tracked             |
| Requirement completion                     | Tracked             |

The pace engine must produce the correct result in 100% of approved golden scenarios and return deterministic results for repeated identical normalized inputs.

# 6. Reviews and Audits

## 6.1 Requirements Review

The team will review SRS requirements for testability, completeness, internal consistency, EARS syntax, clear acceptance criteria, and traceability to tests. A requirement with unclear expected behavior will be clarified before implementation or test approval.

## 6.2 Design Review

- Backend ownership of financial calculations.

- Correct database relationships.

- Atomic input/snapshot persistence.

- Immutable calculation snapshots.

- Appropriate trust boundaries.

- Secure session and secret handling.

## 6.3 Code Review

Every pull request must receive at least one approval from a person other than its author. Reviewers will check requirement conformance, logic correctness, input and error handling, security, test quality, edge cases, readability and maintainability, and whether AI-generated implementation assumptions were independently verified. Code review is a release-quality gate rather than an optional practice.

## 6.4 Quality Audits

- Requirements traceability audit.

- Test evidence audit.

- Security audit.

- Accessibility audit.

- Documentation audit.

- Release readiness audit.

The release cannot be approved if a Must requirement lacks verification evidence.

# 7. Test - Software Testing Plan

## 7.1 Test Objectives

> 1\. Implements all Must requirements in SRS v2.0.
>
> 2\. Produces correct and deterministic pace-v1 calculations.
>
> 3\. Protects user and financial data.
>
> 4\. Correctly isolates users.
>
> 5\. Handles errors without corrupting previously committed data.
>
> 6\. Meets performance and reliability thresholds.
>
> 7\. Works across supported browsers.
>
> 8\. Is usable and accessible.
>
> 9\. Remains fully functional without an external AI service.
>
> 10\. Is fit for its intended budgeting purpose.

Testing includes verification - are we building the product correctly? - and validation - are we building the correct product?

## 7.2 Test Levels and Sequence

### Level 1 - Unit Testing

Individual functions and classes will be tested first. Primary targets include pace-v1 formulas, recurrence expansion, currency normalization, downward rounding, Goal Gap and Projected Shortfall calculations, status precedence, input validation, authentication helpers, and data-model rules. The pace engine receives the strongest unit-testing emphasis because incorrect financial calculations are a catastrophic project risk.

### Level 2 - Integration Testing

After units pass, integration tests will verify interactions between FastAPI routes and services, the service layer and database, goal/input updates and the calculation engine, the calculation engine and snapshot creation, authentication and protected resources, frontend/backend API contracts, and weekly-plan logic with persisted snapshots. Top-down testing will be used for user-facing workflows while targeted bottom-up tests will validate lower-level calculation and persistence services.

### Level 3 - System Testing

The integrated application will then be tested as a complete product. System testing includes end-to-end workflows, cross-browser testing, performance testing, security testing, accessibility testing, recovery testing, export/deletion testing, error handling, and regression testing.

### Level 4 - Acceptance Testing

Acceptance testing will confirm that the MVP meets the SRS and customer/course expectations. The final workflow will demonstrate:

> 1\. Account creation.
>
> 2\. Goal setup.
>
> 3\. Manual financial inputs.
>
> 4\. pace-v1 calculation.
>
> 5\. Dashboard review.
>
> 6\. Calculation trace.
>
> 7\. Data export.
>
> 8\. Verified account deletion.

The course instructor is the final academic acceptance authority.

## 7.3 Test Strategies

### Black-Box Testing

Black-box testing will be used for user workflows, API behavior, form validation, authentication, dashboard output, export and deletion, cross-browser behavior, and security behavior. Inputs and expected outputs will be derived from the SRS without relying on implementation details.

### White-Box Testing

White-box testing will be used for pace-v1 branches, status precedence, error paths, snapshot transaction logic, authentication/authorization logic, and coverage analysis.

### Positive, Negative, Boundary, and Regression Testing

Positive tests confirm normal workflows. Negative tests use invalid, missing, oversized, unauthorized, or malicious inputs and require the system to fail safely. Boundary tests cover zero values, completed goals, maximum allowed financial values, date boundaries, month-end recurrence, session expiry, failed-login thresholds, and weekly spending boundaries. Every corrected defect should receive a regression test where practical, and the full automated suite will run before each release candidate.

## 7.4 Key Test Cases

| **Test ID** | **Requirement** | **Test / Input** | **Acceptance Criteria** |
|----|----|----|----|
| TC-AUTH-001 | FR-AUTH-001 | Register using valid unique email/password | Account created and authenticated session begins |
| TC-AUTH-003 | FR-AUTH-003 | Submit invalid credentials | Access denied with generic error; account existence not revealed |
| TC-GOAL-003 | FR-GOAL-003 | Try creating second Active goal | System rejects second Active goal |
| TC-INP-004 | FR-INP-004 | Add unconfirmed \$1,000 income | Income excluded from forecast |
| TC-INP-008 | FR-INP-008 | Inspect MVP input options | Only manual entry exists; no CSV or bank synchronization controls |
| TC-CALC-006 | FR-CALC-006 | Cash 5,000; income 1,000; expense 500; reserve 500 | Forecast Resources = \$5,000 |
| TC-CALC-009 | FR-CALC-009 | Capacity \$1,000; 10 weeks | Weekly Safe-to-Spend = \$100 |
| TC-CALC-010 | FR-CALC-010 | Capacity = 999 cents; 4 weeks | Final allowance = \$2, never rounded upward |
| TC-CALC-013 | FR-CALC-013 | Positive projected shortfall | Status = At Risk before pace comparison |
| TC-CALC-015 | FR-CALC-015 | Replay identical normalized inputs | Identical result and formula_version = pace-v1 |
| TC-SNAP-003 | FR-SNAP-003 | Attempt ordinary update/delete of snapshot | Operation denied; snapshot remains unchanged |
| TC-SNAP-004 | FR-SNAP-004 | Simulate persistence failure | Both input and snapshot changes roll back |
| TC-WEEK-002 | FR-WEEK-002 | Recalculate during same week | Weekly opening remains unchanged |
| TC-WEEK-004 | FR-WEEK-004 | Spend more than opening allowance | Negative remaining amount and warning displayed |
| TC-DASH-006 | FR-DASH-006 | Open Calculation Details | All pace-v1 inputs/outputs, snapshot ID and formula version displayed |
| TC-DATA-002 | FR-DATA-002 | Request export | Export accessible only to requester using single-use 24-hour link |
| TC-ERR-001 | FR-ERR-001 | Submit multiple invalid fields | Errors identify all invalid fields; no snapshot is created |
| TC-AI-001 | FR-AI-001 | Run MVP with AI flag disabled | AI Future page appears and no external AI request occurs |
| PT-001 | NFR-PERF-001 | 50 concurrent valid sessions | 95% \<=2 sec and 99% \<=4 sec |
| RT-001 | NFR-REL-001 | Inject failure during input/snapshot transaction | Zero partial commits |
| ST-005 | NFR-SEC-005 | Attempt cross-user resource access | 100% unauthorized access attempts denied |
| ST-006 | NFR-SEC-006 | SQL injection/SAST/DAST tests | Zero exploitable SQL-injection findings |
| ST-009 | NFR-SEC-009 | Run CI security scans | Zero unresolved Critical/High findings |
| AT-A11Y-001 | NFR-A11Y-001 | WCAG 2.2 AA audit | Zero Critical accessibility violations |
| UT-USAB-001 | NFR-USAB-001 | Five first-time users perform core workflow | \>=80% complete within 10 minutes unaided |
| CT-MNT-002 | NFR-MNT-002 | CI coverage analysis | Pace branch \>=90%; backend line \>=75% |
| OT-OBS-001 | NFR-OBS-001 | Send API request | Correlation ID appears in response and related logs |
| BCP-001 | NFR-BCP-001 | Backup/restore test | Daily encrypted backup, RPO \<=24h and RTO \<=4h |

## 7.5 Golden Test Set

### GT-01 - Positive Capacity

Inputs: Starting cash \$5,000; confirmed income \$1,000; expenses \$500; reserve \$500; target \$10,000; saved \$6,000; 10 weeks. Expected: Forecast Resources \$5,000; Goal Gap \$4,000; Discretionary Capacity \$1,000; Projected Shortfall \$0; Weekly Safe-to-Spend \$100.

### GT-02 - Corrected PDR Scenario

Inputs: Starting cash \$3,150; confirmed future income \$5,270; planned future expenses \$2,930; reserve \$260; target \$12,000; saved \$4,850; 30 weeks. Expected: Forecast Resources \$5,230; Goal Gap \$7,150; Capacity -\$1,920; Projected Shortfall \$1,920; Weekly Safe-to-Spend \$0; Status At Risk. Earlier mockup values of \$740 shortfall and \$192 safe-to-spend are not valid for these inputs.

### GT-03 - Completed Goal

Target = \$10,000 and saved = \$10,000. Expected status: Completed.

### GT-04 - Unconfirmed Income

An otherwise valid \$1,000 income source is marked unconfirmed. Expected: it contributes \$0 to forecast income.

### GT-05 - Downward Rounding

Discretionary capacity = 999 cents across four weeks. Expected Weekly Safe-to-Spend: \$2, not \$2.50 or \$3.

### GT-06 - Monthly Boundary

A monthly occurrence begins January 31 and continues into February. Expected February occurrence date: the final calendar day of February.

All golden tests must pass before release.

## 7.6 Functional and Non-Functional Testing

### Functional Tests

Functional testing covers registration and authentication, goal creation and editing, one-Active-goal restriction, manual financial inputs, confirmed and unconfirmed income, planned expenses, recurrence logic, pace-v1 calculations, status logic, snapshots, weekly plans, dashboard, error handling, export, account deletion, and AI Future guardrail behavior.

### Performance Tests

The principal performance test will simulate up to 50 concurrent authenticated users with plans containing up to 100 income sources and 100 expenses. Acceptance targets: 95% of save/recalculate requests complete within 2 seconds; 99% within 4 seconds; 95% of dashboard backend responses within 750 ms; browser Largest Contentful Paint \<=2.5 seconds on a 10 Mbps connection; and export of up to 10,000 owned records completes within 10 seconds in at least 95% of tests.

### Reliability Tests

Reliability tests will include transaction fault injection, application restart after committed calculation, restoration of latest snapshot and weekly plan, AI dependency unavailable for 24 hours, and backup/restore tests.

### Security Tests

Security testing will include SAST, dependency scanning, DAST where practical, authentication testing, session security, authorization and cross-user access, SQL injection, XSS, CSRF, rate limiting, secret scanning, HTTPS/TLS configuration, audit logging, and account deletion/export authorization. No Critical or High security finding may remain unresolved for release.

## 7.7 Requirements Traceability Matrix

The SRS v2.0 contains the master traceability baseline. The following matrix shows the principal SQAP/STP mappings.

| **SRS Requirement** | **Verification Test** |
|---------------------|-----------------------|
| FR-AUTH-001         | TC-AUTH-001           |
| FR-AUTH-003         | TC-AUTH-003           |
| FR-GOAL-003         | TC-GOAL-003           |
| FR-INP-004          | TC-INP-004 / GT-04    |
| FR-INP-008          | TC-INP-008            |
| FR-CALC-006         | TC-CALC-006 / GT-01   |
| FR-CALC-009         | TC-CALC-009 / GT-01   |
| FR-CALC-010         | TC-CALC-010 / GT-05   |
| FR-CALC-013         | TC-CALC-013 / GT-02   |
| FR-CALC-015         | TC-CALC-015           |
| FR-SNAP-003         | TC-SNAP-003           |
| FR-SNAP-004         | TC-SNAP-004 / RT-001  |
| FR-WEEK-002         | TC-WEEK-002           |
| FR-WEEK-004         | TC-WEEK-004           |
| FR-DASH-006         | TC-DASH-006           |
| FR-DATA-002         | TC-DATA-002           |
| FR-ERR-001          | TC-ERR-001            |
| FR-AI-001           | TC-AI-001             |
| NFR-ACC-001         | GT-SUITE              |
| NFR-PERF-001        | PT-001                |
| NFR-REL-001         | RT-001                |
| NFR-SEC-005         | ST-005                |
| NFR-SEC-006         | ST-006                |
| NFR-SEC-009         | ST-009                |
| NFR-A11Y-001        | AT-A11Y-001           |
| NFR-USAB-001        | UT-USAB-001           |
| NFR-MNT-002         | CT-MNT-002            |
| NFR-OBS-001         | OT-OBS-001            |
| NFR-BCP-001         | BCP-001               |

Before final release, the QA lead will audit the complete SRS matrix to confirm that every Must requirement has linked passing evidence.

## 7.8 Test Execution Sequence

> 1\. Static formatting and lint checks.
>
> 2\. SAST and secret scan.
>
> 3\. Unit tests.
>
> 4\. pace-v1 golden tests.
>
> 5\. Coverage measurement.
>
> 6\. API/contract tests.
>
> 7\. Database integration tests.
>
> 8\. Frontend/backend integration tests.
>
> 9\. System and end-to-end tests.
>
> 10\. Negative and boundary tests.
>
> 11\. Cross-browser tests.
>
> 12\. Performance/load tests.
>
> 13\. Security tests.
>
> 14\. Accessibility tests.
>
> 15\. Reliability and recovery tests.
>
> 16\. Regression suite.
>
> 17\. User acceptance/usability testing.
>
> 18\. Final release acceptance demonstration.

A failure at a mandatory CI gate prevents the code from proceeding to merge or release.

## 7.9 AI-Generated Code and the Spec-Conformance Trap

AI may assist with implementation and test generation, but AI-produced output is not treated as authoritative. A passing AI-generated test proves only that the implementation matches that particular test. It does not prove that either the test or the implementation matches the actual requirement. This is the spec-conformance trap.

For example, an AI system could generate both an incorrect pace-v1 implementation and an incorrect test expecting the same wrong answer. The test would pass even though the product violates the SRS.

To prevent this:

- Expected financial results will be calculated independently before being encoded into automated tests.

- Golden-test expected values will be manually reviewed by the team.

- Test cases will reference SRS requirement IDs.

- Reviewers will compare AI-generated tests directly against EARS requirements.

- Human-authored negative and boundary tests will supplement generated tests.

- Tests will intentionally challenge assumptions made by AI-generated code.

- Code and tests generated together by the same AI interaction will receive particular scrutiny.

- AI-generated dependencies will not be added without human verification.

Human-added edge and error cases include zero capacity, negative capacity, a completed goal, missing required inputs, target-date boundaries, month-end recurrence, unconfirmed income, very large but valid money values, invalid negative values, duplicate Active goal, repeated identical inputs, transaction failure during snapshot creation, unauthorized cross-user access, expired session, excess failed login attempts, AI service unavailable, and malformed or malicious user input.

## 7.10 CI Test Gates

Every pull request must pass the automated quality pipeline before merge. Required gates are:

> 1\. Build succeeds.
>
> 2\. Formatting/lint checks pass.
>
> 3\. Unit tests pass.
>
> 4\. Golden tests pass.
>
> 5\. Integration tests pass.
>
> 6\. Pace-engine branch coverage \>=90%.
>
> 7\. Backend line coverage \>=75%.
>
> 8\. SAST passes.
>
> 9\. Dependency scan has no unresolved Critical/High issue.
>
> 10\. Secret scan passes.
>
> 11\. Required reviewer approves the change.

The protected main branch will prevent bypassing these gates.

# 8. Problem Reporting and Corrective Action

All discovered defects will be logged in GitHub Issues.

## 8.1 Defect Categories

| **Severity** | **Definition** |
|----|----|
| Critical | System unusable; incorrect financial guidance with broad impact; security breach; data loss or cross-user data exposure. |
| High | Major required feature unavailable; major incorrect calculation; authentication/authorization failure; release-blocking security problem. |
| Medium | Partial feature degradation; incorrect secondary behavior with workaround; significant usability/accessibility issue. |
| Low | Cosmetic issue; minor wording/layout problem; non-blocking inconvenience. |

## 8.2 Defect Workflow

> 1\. Discover defect.
>
> 2\. Record reproducible steps and evidence.
>
> 3\. Assign severity and affected requirement.
>
> 4\. Assign owner.
>
> 5\. Implement correction.
>
> 6\. Run the original failed test.
>
> 7\. Run related regression tests.
>
> 8\. QA verifies resolution.
>
> 9\. Close defect or reopen if unsuccessful.

Critical and High defects block release unless an explicit documented exception is approved.

## 8.3 Test/Defect Report Format

| **Field**                | **Entry**                      |
|--------------------------|--------------------------------|
| Test ID                  | Unique test identifier         |
| Requirement ID           | SRS requirement being tested   |
| Tester                   | Person executing test          |
| Date                     | Execution date                 |
| Build/Version            | Tested release candidate       |
| Pass/Fail                | Result                         |
| Defect Severity          | Critical / High / Medium / Low |
| Resolved?                | Yes / No                       |
| Retest Result            | Pass / Fail / Pending          |
| Comments                 | Observed behavior and evidence |
| Standard-Code Compliance | Compliant / Not Compliant      |

# 9. Tools, Techniques, and Methodologies

| **Tool/Technique** | **Purpose** |
|----|----|
| GitHub | Repository, pull requests, defects, version control |
| GitHub CI/CD | Automated quality gates |
| PyTest | Backend/unit/integration testing |
| Playwright | Browser/end-to-end testing |
| FastAPI test client | API testing |
| Coverage tools | Branch and line coverage |
| ESLint | Frontend linting |
| Python lint/format tool | Backend quality checks |
| SAST tool | Static security analysis |
| Dependency scanner | Vulnerable dependency detection |
| Secret scanner | Credential leakage prevention |
| Browser developer tools | UI and performance inspection |
| Accessibility scanner | Automated accessibility checks |
| Manual peer review | Logic/security/spec verification |

Testing combines white-box, black-box, boundary, negative, regression, load, security, accessibility, and usability techniques.

# 10. Code Control

GitHub will be the configuration-control repository. Controls include a protected main branch, feature branches for development, required pull requests, peer approval, required CI gates, release tags, controlled baseline requirements, and prohibition of direct unreviewed production changes. Changes to normative SRS requirements require documented change control.

# 11. Media Control

Source code and project documentation will be maintained in the version-controlled repository. Production data will be protected through managed database storage, encryption at rest, encrypted backups, restricted access, and secret management outside source control. The project requires encrypted production backups at least once every 24 hours, with an RPO of 24 hours and an RTO of 4 hours.

# 12. Supplier Control

N/A for software development subcontractors. No external subcontractor performs development, testing, or QA for GoalWise. Hosting, database, and future AI services are treated as external technology dependencies rather than development subcontractors. The MVP must remain fully functional if AI services are unavailable.

# 13. Records Collection, Maintenance, and Retention

The following quality records will be maintained:

- Test cases.

- Test execution reports.

- CI results.

- Coverage reports.

- Security scan reports.

- Defect records.

- Pull-request reviews.

- Requirements traceability matrix.

- Accessibility results.

- Performance results.

- Usability-session findings.

- Release approval evidence.

Evidence will be linked to the corresponding requirement or defect where possible. Test evidence from earlier releases will be retained to support regression testing.

# 14. Training

Team members will maintain sufficient knowledge of Git and GitHub workflow, FastAPI, React/Next.js, PostgreSQL, PyTest, Playwright, secure coding practices, OWASP-style vulnerabilities, accessibility testing, and AI-assisted software review. The project SPMP assigns training ownership for FastAPI, React, security practices, Git workflow, and AI governance.

# 15. Risk Management

Risk management is defined in the GoalWise SPMP risk register and is incorporated into this SQAP by reference rather than duplicated. Quality-related risks include incorrect pace-engine calculations, security vulnerabilities, insecure AI-generated code, hallucinated AI-generated dependencies, integration failures, database performance issues, privacy leakage, and schedule slippage.

The highest-impact quality risk is incorrect financial calculation. Mitigation includes manually verified golden tests, \>=90% pace-engine branch coverage, deterministic backend calculation, peer review, and CI enforcement. Security-related mitigation includes static analysis, parameterized database operations, server-side validation, dependency scanning, authorization testing, and zero unresolved Critical/High findings before release.

# Appendix A. Release Candidate Error-Minimization Strategy

Before a release candidate is accepted, Group 3 will:

> 1\. Freeze normative requirements for the candidate.
>
> 2\. Run the complete automated suite.
>
> 3\. Run all pace-v1 golden tests.
>
> 4\. Review coverage reports.
>
> 5\. Resolve Critical and High defects.
>
> 6\. Run SAST and dependency/security scans.
>
> 7\. Execute regression tests.
>
> 8\. Perform system and end-to-end testing.
>
> 9\. Perform accessibility and cross-browser checks.
>
> 10\. Perform performance and recovery tests.
>
> 11\. Review requirement traceability for missing evidence.
>
> 12\. Conduct an independent peer review of AI-assisted code and tests.
>
> 13\. Perform acceptance testing using the complete user workflow.
>
> 14\. Record known lower-severity issues and their disposition.
>
> 15\. Tag the approved build so the tested release is reproducible.

A release candidate will not be accepted merely because its automated tests pass. Release requires evidence that the tests themselves represent the SRS correctly and that the system is fit for its intended purpose.
