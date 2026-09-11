<table style="width:71%;">
<colgroup>
<col style="width: 13%" />
<col style="width: 56%" />
</colgroup>
<thead>
<tr>
<th style="text-align: center;"><strong>GW</strong></th>
<th style="text-align: left;"><strong>GoalWise</strong><br />
Goal-Oriented Budgeting and Weekly Spending Pace</th>
</tr>
</thead>
<tbody>
</tbody>
</table>

Software Requirements\
Specification

Version 2.0 - Revised after Preliminary Design Review

| **NORMATIVE BASELINE \| PDR V2** |
|----------------------------------|

| **Course**         | MSCS 2101 - Software Engineering            |
|--------------------|---------------------------------------------|
| **Project**        | **GoalWise**                                |
| **Team**           | Group 3                                     |
| **Prepared by**    | Vishal, Nati, Ashutosh, and Thanh           |
| **Document owner** | Thanh - Quality Assurance and Documentation |
| **Version**        | **2.0**                                     |
| **Date**           | August 9, 2026                              |

| **Purpose.** This document defines the complete, testable requirements for the GoalWise MVP and the bounded post-MVP AI explanation layer. Requirements are written in EARS and take precedence over illustrative mockup values. |
|----|

*Academic project document - Group 3*

# Document Control

Version ownership, revision history, approvals, and normative precedence.

| **Document title** | GoalWise Software Requirements Specification |
|----|----|
| **Document identifier** | GW-SRS-2.0 |
| **Version / status** | 2.0 / Revised PDR baseline |
| **Owner** | Thanh - Quality Assurance and Documentation |
| **Approver** | Group 3; final academic acceptance by course instructor |
| **Effective date** | August 9, 2026 |
| **Supersedes** | GoalWise SRS v1.0 |

## Revision History

| **Version** | **Date** | **Owner** | **Summary and rationale** |
|:--:|:--:|:--:|:---|
| 1.0 | July 26, 2026 | Group 3 | Initial approved SRS baseline referenced by the SPMP. |
| 2.0 | August 9, 2026 | Group 3 | PDR revision: narrowed MVP to manual inputs; deferred CSV import and runtime AI; clarified pace-v1 formulas, status precedence, recurrence, weekly-plan freeze, immutable snapshots, backend trust boundary, measurable NFRs, explicit security/privacy, traceability, ADRs, and AI provenance. Mockup numbers are designated non-normative and corrected by golden tests. |

## Approval Record

| **Name** | **Role** | **Approval / signature** | **Date** |
|:---|:---|:--:|:--:|
| Vishal | Project Manager / Leader | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_\_\_\_\_\_\_ |
| Nati | Assistant PM; Software Engineer | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_\_\_\_\_\_\_ |
| Ashutosh | UI/UX Designer | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_\_\_\_\_\_\_ |
| Thanh | QA and Documentation | \_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_ | \_\_\_\_\_\_\_\_\_\_\_\_ |

| **Normative precedence.** If a supplied UI mockup, planning statement, or sample number conflicts with a requirement or formula in this SRS, this SRS Version 2.0 controls until a formally approved change updates the baseline. |
|----|

# Contents

| **1**          | **Introduction**                                  |
|----------------|---------------------------------------------------|
| **2**          | **Overall Description and PDR Scope Baseline**    |
| **3**          | **System Context, Data Model, and pace-v1 Rules** |
| **4**          | **External Interface Requirements**               |
| **5**          | **Functional Requirements**                       |
| **6**          | **Nonfunctional Requirements**                    |
| **7**          | **Data Requirements**                             |
| **8**          | **Verification and Product Acceptance**           |
| **9**          | **Requirements Traceability Matrix**              |
| **10**         | **PDR Alignment Actions**                         |
| **Appendix A** | AI Assistance and Provenance                      |
| **Appendix B** | Architecture Decision Record Updates              |
| **Appendix C** | Glossary and Data Dictionary                      |
| **Appendix D** | UI Mockups                                        |

| **EARS convention.** Normative requirements use one of these patterns: The system shall...; When \<trigger\>, the system shall...; While \<state\>, the system shall...; If \<unwanted condition\>, the system shall...; Where \<optional feature\>, the system shall.... |
|----|

# 1. Introduction

## 1.1 Purpose

GoalWise is a goal-oriented budgeting web application that helps one user pursue one active savings goal by calculating a deterministic weekly safe-to-spend amount. This SRS Version 2.0 defines the product baseline after the Preliminary Design Review and is intended to be testable, auditable, and implementable by the Group 3 development team.

## 1.2 Product Scope

- User registration, authentication, session management, and account recovery.

- One Active savings goal in USD with current saved amount, dates, and lifecycle status.

- Manual financial profile, Confirmed income sources, planned expenses, reserve buffer, and manual current-week spending total.

- Backend-owned pace-v1 calculation, immutable versioned snapshots, weekly-plan behavior, dashboard, status explanation, and calculation trace.

- User data export and verified account deletion.

- A static AI Future guardrail page in the MVP; optional post-MVP explanation requirements are specified but are not release acceptance criteria for the MVP.

## 1.3 Out of Scope for the Version 2.0 MVP

- CSV transaction import, bank synchronization, and transaction-correction workflows.

- Multiple simultaneous goals, household sharing, mobile native applications, multi-currency support, investments, lending, tax advice, and automatic transfers or payments.

- Any AI-generated calculation, recommendation, override, or dependency required for core operation.

## 1.4 Intended Audience

| **Audience** | **Use of this SRS** |
|:---|:---|
| Course instructor / reviewer | Evaluate scope, rigor, traceability, security, and product acceptance. |
| Project manager | Control the requirements baseline and approve changes. |
| Backend engineer | Implement APIs, validation, pace-v1, persistence, security, and snapshots. |
| UI/UX designer and frontend engineer | Implement user workflows and render official backend results accessibly. |
| QA and documentation owner | Derive tests, collect evidence, maintain traceability, and audit release readiness. |

## 1.5 References

> **1.** GoalWise Software Project Management Plan, Version 1.0, August 9, 2026.
>
> **2.** GoalWise Preliminary Design Review UI mockups: landing, goal setup, financial inputs, dashboard, calculation details, and AI Future.
>
> **3.** Instructor feedback requiring SRS Version 2.0, EARS requirements, measurable NFRs, explicit security, updated traceability and revision history, AI provenance, and ADR updates.
>
> **4.** IEEE 830 Software Requirements Specification guidance, as referenced by the project plan.
>
> **5.** OWASP ASVS, NIST Secure Software Development Framework, WCAG 2.2, and NIST AI Risk Management Framework, as referenced by the project plan.

## 1.6 Definitions and Requirement Conventions

| **Convention** | **Meaning** |
|:---|:---|
| Must | Required for the September 12, 2026 MVP acceptance unless this SRS is formally changed. |
| Should | Important but may be deferred only through documented change control. |
| Future | Specified for a bounded post-MVP capability and excluded from MVP acceptance. |
| EARS | Easy Approach to Requirements Syntax; each normative requirement uses a trigger/state/condition plus shall. |
| Verification | Test, analysis, inspection, contract test, security test, or demonstration used to prove compliance. |
| Normative | Binding requirement, formula, constraint, or acceptance criterion. |
| Non-normative | Illustration, mockup, or example that does not override the requirements baseline. |

# 2. Overall Description and PDR Scope Baseline

## 2.1 Product Perspective

GoalWise is a responsive web application with a React or Next.js client, a FastAPI REST backend under /api/v1, PostgreSQL in production, SQLite for local tests, and an optional future AI adapter. The backend is the source of truth for financial calculations and persisted snapshots.

## 2.2 Product Functions

- Authenticate one user and isolate that user's financial workspace.

- Create and maintain one Active goal.

- Capture manual cash, income, expenses, reserve, and current-week spending.

- Run the pace-v1 formula and status rules deterministically.

- Persist immutable snapshots and weekly plans.

- Display a dashboard, status rationale, calculation breakdown, and snapshot trace.

- Export and delete user-owned data.

- Display AI guardrails in the MVP and safely support an optional explain-only layer later.

## 2.3 User Classes

| **User class** | **Capabilities and constraints** |
|:---|:---|
| Visitor | Views the public landing page and may register or sign in; cannot access financial data. |
| Registered user | Owns one private workspace, enters data, reviews results, exports data, and deletes the account. |
| System operator | Maintains infrastructure, backups, monitoring, and secrets; does not need a financial-data browsing UI. |
| Course reviewer | Uses an approved demo account and evidence package; receives no special production privilege. |

## 2.4 Operating Environment

| **Client** | Responsive browser UI on current and previous Chrome, Firefox, and Edge; current Safari. |
|----|----|
| **Frontend** | React or Next.js. |
| **Backend** | Python FastAPI REST services under /api/v1. |
| **Production data** | PostgreSQL with encrypted backups. |
| **Development/test data** | SQLite may be used for local development and automated tests. |
| **Hosting** | HTTPS-capable provider with environment secrets, monitoring, and logging. |
| **Currency** | USD only in Version 2.0. |

## 2.5 Constraints

- One Active goal per user.

- Manual inputs only in the MVP.

- All official financial results are produced by pace-v1 on the backend.

- AI is not permitted to calculate, modify, or override official results.

- The four-person project schedule targets final release on September 12, 2026.

## 2.6 Assumptions and Dependencies

- Users provide accurate cash, income, expense, reserve, and saved-amount information.

- A Confirmed income source represents money the user reasonably expects to receive.

- The hosting provider supplies HTTPS, database, backup, and secret-management capabilities.

- No external AI service is required for the MVP or for deterministic operation.

## 2.7 PDR Scope Decisions

| **Topic** | **Earlier baseline** | **PDR evidence** | **V2.0 decision** | **Downstream action** |
|:---|:---|:---|:---|:---|
| CSV import | Included in SPMP v1.0 MVP | Financial Inputs mockup says deferred | Deferred from SRS v2.0 MVP; manual entry only. | Update SPMP T8 and acceptance workflow. |
| Runtime AI summary | Included as optional MVP feature | AI screen labels it a deferred future layer | Excluded from MVP acceptance; bounded Future requirements retained. | Update SPMP T10 and AI acceptance wording. |
| Calculation source | Deterministic objective | Calculation screen states backend source of truth | Backend-only official calculation is explicit. | Frontend must not recompute official values. |
| Snapshot behavior | Referenced in planning/risk | Goal and dashboard mockups show immutable snapshot flow | Snapshot contents, atomicity, and immutability are explicit. | Database and tests must enforce append-only behavior. |
| Current week | Weekly allowance mentioned | Dashboard shows opening and remaining | Opening is frozen; manual weekly spend changes remaining. | Add manual weekly-spend control to implementation. |
| Mockup numbers | No reconciliation rule | Displayed values are internally inconsistent | Formulas and golden tests are normative; mockup values must be refreshed. | Correct UI fixture before CDR. |

| **Configuration alignment action.** The SPMP is a planning artifact and still contains CSV-import and AI-summary tasks. Before CDR, update its scope, task list, schedule, and acceptance steps so they match this SRS Version 2.0. |
|----|

# 3. System Context, Data Model, and pace-v1 Rules

## 3.1 Context and Trust Boundaries

| **Component** | **Responsibility** | **Trust rule** |
|:---|:---|:---|
| Browser client | Collects user input and renders results. | Untrusted for official calculations; no secrets stored in client code. |
| FastAPI application | Validates, authorizes, normalizes, calculates, persists, and returns official results. | Primary application trust boundary and calculation source of truth. |
| PostgreSQL | Stores user data, inputs, snapshots, weekly plans, and audit events. | Restricted service access; encrypted at rest and backed up. |
| Hosting / monitoring | Provides TLS termination, runtime, logs, alerts, and backups. | Administrative access controlled and auditable. |
| AI provider - Future | Generates optional explanation of committed snapshot values. | External/untrusted output; minimized payload; never a calculation authority. |

## 3.2 Core Data Entities

| **Entity** | **Purpose** | **Key relationships** |
|:---|:---|:---|
| User | Identity, password hash, time zone, lifecycle state. | Owns all other records. |
| Goal | One savings target and lifecycle state. | One Active goal per user; has snapshots. |
| FinancialProfile | Starting cash, balance-as-of date, reserve. | One current profile per user. |
| IncomeSource | Manual expected income and confirmation. | Many per user; expanded into occurrences. |
| PlannedExpense | Manual planned outflow. | Many per user; expanded into occurrences. |
| CalculationSnapshot | Immutable normalized inputs and pace-v1 outputs. | Many per goal; latest drives dashboard. |
| WeeklyPlan | Frozen weekly opening and manual spending total. | At most one per user per local week. |
| AuditEvent | Security and change metadata. | Append-only; excludes financial values. |
| AIExplanation - Future | Validated explanation for one committed snapshot. | Optional and non-authoritative. |

## 3.3 Normative pace-v1 Formula

<table style="width:69%;">
<colgroup>
<col style="width: 68%" />
</colgroup>
<thead>
<tr>
<th><p><strong>Normative formula</strong></p>
<p>forecast_income = sum(confirmed income occurrences in forecast window)</p>
<p>forecast_expenses = sum(enabled planned-expense occurrences in forecast window)</p>
<p>forecast_resources = starting_cash + forecast_income - forecast_expenses - reserve_buffer</p>
<p>goal_gap = max(target_amount - current_saved_amount, 0)</p>
<p>discretionary_capacity = forecast_resources - goal_gap</p>
<p>projected_shortfall = max(-discretionary_capacity, 0)</p>
<p>remaining_weeks = max(1, ceil((target_date - balance_as_of_date) / 7))</p>
<p>weekly_safe_to_spend = floor(max(discretionary_capacity, 0) / remaining_weeks)</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

The forecast window includes occurrences after the balance-as-of date and through the target date inclusive. All intermediate money values use integer cents. Only the final Weekly Safe-to-Spend value is reduced to whole dollars by flooring; it is never rounded upward.

## 3.4 Expected Pace and Status Precedence

<table style="width:69%;">
<colgroup>
<col style="width: 68%" />
</colgroup>
<thead>
<tr>
<th><p><strong>Expected-pace formula</strong></p>
<p>baseline_saved = saved amount in first Active-goal snapshot</p>
<p>elapsed_fraction = clamp((as_of_date - start_date) / (target_date - start_date), 0, 1)</p>
<p>expected_saved = baseline_saved + (target_amount - baseline_saved) * elapsed_fraction</p>
<p>pace_tolerance = max(25 USD, 2 percent of target_amount)</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

> **1.** Completed, when Goal Gap equals 0.
>
> **2.** At Risk, when Projected Shortfall is greater than 0.
>
> **3.** Ahead, when no shortfall exists and current saved is above expected saved by more than the tolerance.
>
> **4.** Off Pace, when no shortfall exists and current saved is below expected saved by more than the tolerance.
>
> **5.** On Track, otherwise.

## 3.5 Weekly Plan Rule

<table style="width:69%;">
<colgroup>
<col style="width: 68%" />
</colgroup>
<thead>
<tr>
<th><p><strong>Monday-through-Sunday weekly plan</strong></p>
<p>weekly_opening = latest weekly_safe_to_spend when the local week begins</p>
<p>current_week_remaining = weekly_opening - recorded_current_week_discretionary_spending</p>
<p>same-week recalculations update next-week recommendation, not weekly_opening</p></th>
</tr>
</thead>
<tbody>
</tbody>
</table>

## 3.6 Mockup Numerical Reconciliation

| **Value** | **Displayed mockup value** | **Normative pace-v1 result** |
|:---|:---|:---|
| Starting cash | \$3,150 | \$3,150 |
| Confirmed future income | \$5,270 | \$5,270 |
| Planned future expenses | \$2,930 | \$2,930 |
| Reserve buffer | \$260 | \$260 |
| Forecast Resources | \$5,230 | \$5,230 |
| Target / saved / Goal Gap | \$12,000 / \$4,850 / \$7,150 | \$12,000 / \$4,850 / \$7,150 |
| Projected Shortfall | \$740 | \$1,920 |
| Weekly Safe-to-Spend, 30 weeks | \$192 | \$0 |

| **PDR correction required.** The supplied mockup inputs produce Forecast Resources of \$5,230 and Goal Gap of \$7,150. Therefore pace-v1 produces a \$1,920 projected shortfall and \$0 weekly safe-to-spend. The displayed \$740 and \$192 are illustrative and must be replaced before CDR. |
|----|

# 4. External Interface Requirements

## 4.1 User Interface Requirements

| **ID** | **Priority** | **EARS requirement** | **Verification** |
|:--:|:--:|:---|:--:|
| **UIR-001** | **Must** | The GoalWise web interface shall present all required workflows without horizontal scrolling at viewport widths from 360 pixels through 1440 pixels. | **Test** |
| **UIR-002** | **Must** | When an unauthenticated visitor opens the product landing page, the GoalWise system shall describe the deterministic safe-to-spend value, the one-active-goal scope, manual inputs, immutable snapshots, and the AI explain-only boundary without displaying private financial data. | **Inspection** |
| **UIR-003** | **Must** | When an authenticated user opens the application, the GoalWise system shall provide navigation to Dashboard, Goal, Inputs, Calculation, and AI Future and shall visually identify the current destination. | **Test** |
| **UIR-004** | **Must** | When a form field is required or invalid, the GoalWise system shall display a persistent text label and a field-specific error adjacent to the control. | **Test** |
| **UIR-005** | **Must** | When the backend returns an official pace result, the GoalWise interface shall render the returned values and shall not recompute or replace them in client-side code. | **Inspection/Test** |
| **UIR-006** | **Must** | The GoalWise REST interface shall exchange UTF-8 JSON under /api/v1, represent money as integer cents, and represent dates and timestamps using ISO 8601. | **Contract test** |
| **UIR-007** | **Must** | If an API request fails, the GoalWise REST interface shall return an application/problem+json response containing a stable error code, a safe user message, and a correlation identifier. | **Contract test** |
| **UIR-008** | **Must** | When the system stores a timestamp, the GoalWise system shall store it in UTC and shall display it in the user-selected IANA time zone. | **Test** |

## 4.2 Screen-to-Workflow Mapping

| **Mockup** | **Normative purpose** | **Primary requirements** |
|:---|:---|:---|
| UI-01 Landing page | Public value proposition, deterministic/AI boundary, Create active goal, View calculation. | UIR-002; FR-AUTH-001 |
| UI-02 Goal Setup | Goal fields, one-active-goal scope, server validation, save-normalize-calculate-snapshot flow. | FR-GOAL-001..007; FR-SNAP-001 |
| UI-03 Financial Inputs | Starting cash, date, reserve, income sources, planned expenses, manual-only scope. | FR-INP-001..010 |
| UI-04 Dashboard | Safe-to-spend, status, progress, weekly opening/remaining, shortfall, why-status, snapshot note. | FR-DASH-001..007; FR-WEEK-001..004 |
| UI-05 Calculation Details | pace-v1 breakdown, snapshot_id, formula_version, backend trust boundary. | FR-CALC-001..015; FR-SNAP-002..003 |
| UI-06 AI Future | Deferred layer and runtime guardrails; no calculation or core dependency. | FR-AI-001..007 |

## 4.3 Software and Communications Interfaces

- Browser to backend: HTTPS REST/JSON under /api/v1.

- Backend to PostgreSQL: authenticated encrypted connection where supported by the provider.

- Backend to AI provider: no connection in the MVP; future requests are server-side only and minimized.

- CI/CD to repository and hosting: protected credentials stored in managed secrets.

| **Review-only control.** The Spec trace button shown in the mockups is treated as a prototype/review affordance and is not an end-user MVP requirement unless separately approved through change control. |
|----|

# 5. Functional Requirements

All requirements in this section use EARS and have stable identifiers for tests and traceability.

## 5.1 Authentication and Account

| **ID** | **Priority** | **EARS requirement** | **Verification** |
|:--:|:--:|:---|:--:|
| **FR-AUTH-001** | **Must** | When a visitor submits a unique valid email address and an accepted password, the GoalWise system shall create one user account and start an authenticated session. | **Test** |
| **FR-AUTH-002** | **Must** | When a registered user submits valid credentials, the GoalWise system shall authenticate the user and provide access only to that user's workspace. | **Test** |
| **FR-AUTH-003** | **Must** | If submitted credentials are invalid, the GoalWise system shall deny authentication and display a generic error that does not reveal whether the email address exists. | **Test** |
| **FR-AUTH-004** | **Must** | When an authenticated user selects Sign out, the GoalWise system shall invalidate the active session and return the user to an unauthenticated page. | **Test** |
| **FR-AUTH-005** | **Should** | When a registered user requests password recovery, the GoalWise system shall issue a one-time reset token that expires after 30 minutes and shall allow the password to be replaced after token validation. | **Test** |

## 5.2 Active Goal Management

| **ID** | **Priority** | **EARS requirement** | **Verification** |
|:--:|:--:|:---|:--:|
| **FR-GOAL-001** | **Must** | When an authenticated user creates a goal, the GoalWise system shall accept a goal name, target amount, current saved amount, start date, target date, and lifecycle status. | **Test** |
| **FR-GOAL-002** | **Must** | When a goal is submitted, the GoalWise system shall validate that the name contains 1 to 80 characters, money values are nonnegative USD amounts, and the target date is later than the start date. | **Test** |
| **FR-GOAL-003** | **Must** | While a user has an Active goal, the GoalWise system shall prevent creation or activation of a second Active goal. | **Test** |
| **FR-GOAL-004** | **Must** | When the user edits the Active goal, the GoalWise system shall persist the validated values and preserve prior calculation snapshots. | **Test** |
| **FR-GOAL-005** | **Must** | When the current saved amount is greater than or equal to the target amount, the GoalWise system shall set the goal lifecycle status to Completed; when the user archives a non-Active goal, the system shall set its status to Archived. | **Test** |
| **FR-GOAL-006** | **Must** | When a valid goal save occurs and all required financial inputs exist, the GoalWise system shall normalize the inputs, run pace-v1, and insert a new immutable calculation snapshot in one server-side operation. | **Test** |
| **FR-GOAL-007** | **Must** | If a valid goal save occurs while required financial inputs are missing, the GoalWise system shall save the goal, shall not create a calculation snapshot, and shall identify each missing input needed to calculate. | **Test** |

## 5.3 Manual Financial Inputs

| **ID** | **Priority** | **EARS requirement** | **Verification** |
|:--:|:--:|:---|:--:|
| **FR-INP-001** | **Must** | When the user edits the financial profile, the GoalWise system shall accept starting cash, a balance-as-of date, and a reserve buffer. | **Test** |
| **FR-INP-002** | **Must** | When financial profile values are submitted, the GoalWise system shall reject negative money values, dates later than the current local date for the balance-as-of date, and values that exceed the configured maximum of 999,999,999.99 USD. | **Test** |
| **FR-INP-003** | **Must** | When the user creates an income source, the GoalWise system shall accept a label, amount, recurrence type, next receipt date, and confirmation status. | **Test** |
| **FR-INP-004** | **Must** | While an income source is not Confirmed, the GoalWise system shall exclude every occurrence of that source from forecast income. | **Test** |
| **FR-INP-005** | **Must** | When expanding a recurring income or expense, the GoalWise system shall support One-time, Weekly, Biweekly, and Monthly recurrence; for a monthly day that does not exist, the system shall use the final calendar day of that month. | **Test** |
| **FR-INP-006** | **Must** | When the user creates a planned expense, the GoalWise system shall accept a label, amount, recurrence type, next due date, and classification as Fixed or Variable. | **Test** |
| **FR-INP-007** | **Must** | When the user adds, edits, disables, or deletes an income source or planned expense, the GoalWise system shall persist the change only after server-side validation. | **Test** |
| **FR-INP-008** | **Must** | While the product is operating as the Version 2.0 MVP, the GoalWise system shall accept financial data only through manual entry and shall not expose CSV import, bank synchronization, or transaction-correction controls. | **Test** |
| **FR-INP-009** | **Must** | When a valid financial-input save occurs and an Active goal exists, the GoalWise system shall save the input changes and the resulting snapshot atomically. | **Test** |
| **FR-INP-010** | **Must** | When the user records a current-week discretionary-spending total, the GoalWise system shall store the nonnegative amount in the current weekly plan and recalculate current-week remaining without changing the weekly opening allowance. | **Test** |

## 5.4 Deterministic pace-v1 Calculation

| **ID** | **Priority** | **EARS requirement** | **Verification** |
|:--:|:--:|:---|:--:|
| **FR-CALC-001** | **Must** | When an official pace result is requested, the GoalWise backend shall be the only component that calculates the official financial outputs. | **Test** |
| **FR-CALC-002** | **Must** | When pace-v1 receives valid inputs, the GoalWise system shall normalize currency to integer cents, normalize dates to calendar dates, and evaluate the calculation without binary floating-point money arithmetic. | **Test** |
| **FR-CALC-003** | **Must** | When pace-v1 calculates a forecast, the GoalWise system shall include occurrences strictly after the balance-as-of date and on or before the target date, and shall set remaining weeks to max(1, ceil((target date - balance-as-of date) / 7)). | **Test** |
| **FR-CALC-004** | **Must** | When pace-v1 totals future income, the GoalWise system shall sum only Confirmed income occurrences in the forecast window. | **Test** |
| **FR-CALC-005** | **Must** | When pace-v1 totals planned future expenses, the GoalWise system shall sum every enabled planned-expense occurrence in the forecast window. | **Test** |
| **FR-CALC-006** | **Must** | When pace-v1 calculates Forecast Resources, the GoalWise system shall compute starting cash plus confirmed future income minus planned future expenses minus the reserve buffer. | **Test** |
| **FR-CALC-007** | **Must** | When pace-v1 calculates Goal Gap, the GoalWise system shall compute max(target amount minus current saved amount, 0). | **Test** |
| **FR-CALC-008** | **Must** | When pace-v1 calculates capacity and risk, the GoalWise system shall compute Discretionary Capacity as Forecast Resources minus Goal Gap and Projected Shortfall as max(0 minus Discretionary Capacity, 0). | **Test** |
| **FR-CALC-009** | **Must** | When pace-v1 calculates Weekly Safe-to-Spend, the GoalWise system shall compute floor(max(Discretionary Capacity, 0) / remaining weeks) in whole USD dollars. | **Test** |
| **FR-CALC-010** | **Must** | When an intermediate monetary value has fractional cents or the final weekly allowance has fractional dollars, the GoalWise system shall round toward lower spendable value and shall never round the allowance upward. | **Test** |
| **FR-CALC-011** | **Must** | When the first Active-goal snapshot is created, the GoalWise system shall store the saved amount as baseline saved; for later snapshots, the system shall calculate expected saved to date by linear interpolation from baseline saved on the goal start date to the target amount on the target date. | **Test** |
| **FR-CALC-012** | **Must** | When the Goal Gap equals zero, the GoalWise system shall assign the pace status Completed. | **Test** |
| **FR-CALC-013** | **Must** | If Projected Shortfall is greater than zero and the goal is not Completed, the GoalWise system shall assign the pace status At Risk before evaluating any expected-pace comparison. | **Test** |
| **FR-CALC-014** | **Must** | If Projected Shortfall is zero and current saved is greater than expected saved by more than max(25 USD, 2 percent of target amount), the GoalWise system shall assign Ahead; if it is lower by more than that tolerance, the system shall assign Off Pace; otherwise the system shall assign On Track. | **Test** |
| **FR-CALC-015** | **Must** | When identical normalized inputs are evaluated with the same formula version, the GoalWise system shall return identical outputs and shall identify the result with formula_version pace-v1. | **Test** |

## 5.5 Snapshots and Weekly Plan

| **ID** | **Priority** | **EARS requirement** | **Verification** |
|:--:|:--:|:---|:--:|
| **FR-SNAP-001** | **Must** | When a valid goal or financial-input change triggers pace-v1, the GoalWise system shall insert one new calculation snapshot after the input changes are persisted. | **Test** |
| **FR-SNAP-002** | **Must** | When a calculation snapshot is created, the GoalWise system shall store a unique snapshot identifier, user and goal identifiers, normalized inputs, outputs, formula version, creation timestamp, and an input-content hash. | **Test** |
| **FR-SNAP-003** | **Must** | While a calculation snapshot exists, the GoalWise system shall prevent updates and ordinary deletes to that snapshot and shall permit removal only as part of verified account deletion or retention cleanup. | **Test** |
| **FR-SNAP-004** | **Must** | If persistence of either the user-owned input change or its calculation snapshot fails, the GoalWise system shall roll back both changes and shall retain the previously committed state. | **Test** |
| **FR-WEEK-001** | **Must** | When an authenticated user first opens GoalWise in a new Monday-through-Sunday local week and a valid latest calculation exists, the GoalWise system shall create a weekly plan whose opening allowance equals the latest Weekly Safe-to-Spend. | **Test** |
| **FR-WEEK-002** | **Must** | While the same local week is active, the GoalWise system shall keep the weekly opening allowance fixed even when later input changes create new calculation snapshots. | **Test** |
| **FR-WEEK-003** | **Must** | When a same-week calculation changes Weekly Safe-to-Spend, the GoalWise system shall display the new value as the next-week recommendation and shall not replace the current-week opening allowance. | **Test** |
| **FR-WEEK-004** | **Must** | When current-week discretionary spending changes, the GoalWise system shall compute current-week remaining as opening allowance minus recorded spending and shall display a negative amount with a warning when spending exceeds the opening allowance. | **Test** |

## 5.6 Dashboard and Explanation

| **ID** | **Priority** | **EARS requirement** | **Verification** |
|:--:|:--:|:---|:--:|
| **FR-DASH-001** | **Must** | If no complete calculable plan exists, the GoalWise dashboard shall display a setup state that identifies the missing goal or financial inputs and provides a direct action to complete them. | **Test** |
| **FR-DASH-002** | **Must** | When a valid latest snapshot exists, the GoalWise dashboard shall display the current-week safe-to-spend amount, pace status, percentage of goal saved, and a plain-language statement that the backend produced the result. | **Test** |
| **FR-DASH-003** | **Must** | When a valid latest snapshot exists, the GoalWise dashboard shall display the active goal name, current saved amount, target amount, target date, and remaining weeks. | **Test** |
| **FR-DASH-004** | **Must** | When a valid latest snapshot exists, the GoalWise dashboard shall display current-week opening, current-week remaining, projected shortfall, formula version, and goal progress. | **Test** |
| **FR-DASH-005** | **Must** | When the user opens Why this status, the GoalWise system shall display expected saved to date, current saved amount, the gap versus expected pace, and the rule that selected the current status. | **Test** |
| **FR-DASH-006** | **Must** | When the user opens Calculation Details, the GoalWise system shall display every pace-v1 input category and output value plus snapshot_id, formula_version, and the backend-source-of-truth notice. | **Test** |
| **FR-DASH-007** | **Must** | When a goal or financial input is saved successfully, the GoalWise system shall refresh the dashboard from the newly committed snapshot and shall identify statuses by text and icon rather than color alone. | **Test** |

## 5.7 Data Export and Deletion

| **ID** | **Priority** | **EARS requirement** | **Verification** |
|:--:|:--:|:---|:--:|
| **FR-DATA-001** | **Must** | When an authenticated user requests a data export, the GoalWise system shall generate a machine-readable package containing the user profile, goals, financial inputs, weekly plans, calculation snapshots, and audit metadata owned by that user. | **Test** |
| **FR-DATA-002** | **Must** | When an export is ready, the GoalWise system shall make it available only to the requesting user through a single-use link that expires after 24 hours. | **Test** |
| **FR-DATA-003** | **Must** | When an authenticated user confirms account deletion by re-entering the current password, the GoalWise system shall disable the account immediately and queue deletion of user-owned production data. | **Test** |
| **FR-DATA-004** | **Must** | When export or account-deletion actions occur, the GoalWise system shall create a security audit event that records the user identifier, action, timestamp, outcome, and correlation identifier without recording financial values or credentials. | **Test** |

## 5.8 AI Future Layer

| **ID** | **Priority** | **EARS requirement** | **Verification** |
|:--:|:--:|:---|:--:|
| **FR-AI-001** | **Must** | While the Version 2.0 MVP AI feature flag is disabled, the GoalWise system shall display the AI Future guardrail page and shall not call an external AI provider. | **Test** |
| **FR-AI-002** | **Future** | Where the post-MVP AI explanation feature is enabled, the GoalWise system shall send only pace status, weekly safe-to-spend, projected shortfall, progress percentage, remaining weeks, formula version, and non-identifying goal context to the AI provider. | **Test** |
| **FR-AI-003** | **Future** | Where the post-MVP AI explanation feature is enabled, the GoalWise system shall use AI only to explain an already committed snapshot and shall not use AI output to calculate or modify safe-to-spend, pace status, shortfall, or stored inputs. | **Test** |
| **FR-AI-004** | **Future** | If an AI response does not match the approved JSON schema, contains a numeric value inconsistent with the source snapshot, or contains prohibited advice, the GoalWise system shall reject the response and display the deterministic fallback explanation. | **Test** |
| **FR-AI-005** | **Future** | If the AI provider is unavailable, times out after 5 seconds, or returns an error, the GoalWise system shall display the deterministic fallback explanation and shall keep every core GoalWise function available. | **Test** |
| **FR-AI-006** | **Future** | Where an AI explanation is displayed, the GoalWise system shall label it as generated, cite the snapshot timestamp and formula version, and shall not present investment, lending, tax, legal, or automatic-transfer advice. | **Test** |
| **FR-AI-007** | **Future** | Before the post-MVP AI explanation feature is released, the GoalWise team shall approve and execute objective tests for numeric consistency, prohibited advice, privacy payloads, fallback behavior, and human readability. | **Inspection/Test** |

## 5.9 Error Handling

| **ID** | **Priority** | **EARS requirement** | **Verification** |
|:--:|:--:|:---|:--:|
| **FR-ERR-001** | **Must** | If user input fails validation, the GoalWise system shall preserve all other submitted values, identify every invalid field, and shall not create a calculation snapshot. | **Test** |
| **FR-ERR-002** | **Must** | If a calculation or snapshot transaction fails after a previously valid snapshot exists, the GoalWise system shall retain and label the previous snapshot as the latest available result and shall notify the user that the new change was not committed. | **Test** |
| **FR-ERR-003** | **Must** | If an unexpected server error occurs, the GoalWise system shall present a non-sensitive message containing a correlation identifier and shall record diagnostic detail in restricted server logs. | **Test** |

# 6. Nonfunctional Requirements

Measurable quality, security, privacy, accessibility, and operational requirements.

## 6.1 Accuracy and Determinism

| **ID** | **Priority** | **EARS requirement** | **Verification** |
|:--:|:--:|:---|:--:|
| **NFR-ACC-001** | **Must** | When the approved pace-v1 golden-test suite is executed, the GoalWise system shall produce the expected output for 100 percent of approved scenarios before release. | **Automated test** |
| **NFR-ACC-002** | **Must** | When money is stored or calculated, the GoalWise system shall preserve cent-level accuracy for intermediate values and shall apply whole-dollar downward rounding only at the final Weekly Safe-to-Spend step. | **Unit test** |
| **NFR-ACC-003** | **Must** | When the same normalized input document and formula version are replayed 1,000 times, the GoalWise system shall produce byte-equivalent official output values in all 1,000 runs. | **Determinism test** |

## 6.2 Performance

| **ID** | **Priority** | **EARS requirement** | **Verification** |
|:--:|:--:|:---|:--:|
| **NFR-PERF-001** | **Must** | When up to 50 concurrent authenticated sessions submit valid plans containing no more than 100 income sources and 100 expenses each, 95 percent of save-and-recalculate requests shall complete within 2.0 seconds and 99 percent within 4.0 seconds. | **Load test** |
| **NFR-PERF-002** | **Must** | When the dashboard is requested under the same load, 95 percent of backend dashboard responses shall complete within 750 milliseconds and the browser Largest Contentful Paint shall be at most 2.5 seconds on a 10 Mbps connection. | **Load/UI test** |
| **NFR-PERF-003** | **Must** | When a user with up to 10,000 owned records requests an export, the GoalWise system shall prepare the export within 10 seconds in 95 percent of tests. | **Performance test** |

## 6.3 Reliability and Availability

| **ID** | **Priority** | **EARS requirement** | **Verification** |
|:--:|:--:|:---|:--:|
| **NFR-REL-001** | **Must** | When a goal or financial-input transaction succeeds, the GoalWise system shall commit all user changes and the corresponding snapshot exactly once; partial commits shall occur in zero approved fault-injection tests. | **Fault-injection test** |
| **NFR-REL-002** | **Must** | If the application process restarts after a committed calculation, the GoalWise system shall restore the latest committed snapshot and weekly plan without manual intervention. | **Recovery test** |
| **NFR-REL-003** | **Must** | If every external AI dependency is unavailable for 24 hours, 100 percent of authentication, goal, input, calculation, dashboard, export, and deletion tests shall remain executable without AI. | **Dependency-isolation test** |
| **NFR-REL-004** | **Must** | The production service shall achieve at least 99.0 percent monthly availability excluding announced maintenance windows of no more than two hours per month. | **Monitoring analysis** |

## 6.4 Security

| **ID** | **Priority** | **EARS requirement** | **Verification** |
|:--:|:--:|:---|:--:|
| **NFR-SEC-001** | **Must** | When data is transmitted over a network, the GoalWise system shall use TLS 1.2 or later, redirect HTTP to HTTPS, and enable HTTP Strict Transport Security in production. | **Security scan** |
| **NFR-SEC-002** | **Must** | When a password is accepted, the GoalWise system shall require at least 12 characters and shall store only an Argon2id hash or a bcrypt hash with cost 12 or higher and a unique salt. | **Inspection/Test** |
| **NFR-SEC-003** | **Must** | When an authenticated browser session is created, the GoalWise system shall use Secure, HttpOnly, SameSite cookies, expire the session after 30 minutes of inactivity, and impose a 24-hour absolute lifetime. | **Security test** |
| **NFR-SEC-004** | **Must** | If an account or source IP produces five failed sign-in attempts within 15 minutes, the GoalWise system shall block additional sign-in attempts for 15 minutes and shall log the event. | **Security test** |
| **NFR-SEC-005** | **Must** | When any protected resource is requested, the GoalWise system shall verify server-side ownership and shall pass 100 percent of horizontal and vertical authorization tests without exposing another user's data. | **Authorization test** |
| **NFR-SEC-006** | **Must** | When the backend processes user-controlled values, the GoalWise system shall use server-side allow-list validation and parameterized database operations and shall produce zero exploitable SQL-injection findings in the release security test. | **SAST/DAST** |
| **NFR-SEC-007** | **Must** | When the web client renders user-controlled content or submits a state-changing request, the GoalWise system shall enforce output encoding, a restrictive Content Security Policy, and CSRF protection appropriate to the selected session design. | **Security test** |
| **NFR-SEC-008** | **Must** | When application secrets, session keys, or database credentials are stored, the GoalWise system shall keep them outside source control in managed environment secrets and shall rotate exposed secrets before deployment. | **Repository/infra inspection** |
| **NFR-SEC-009** | **Must** | Before a release is accepted, the GoalWise build shall report zero unresolved Critical or High dependency, container, static-analysis, or dynamic-analysis security findings. | **CI security gate** |
| **NFR-SEC-010** | **Must** | When authentication, authorization failure, goal/input change, export, deletion, or security-control failure occurs, the GoalWise system shall record a timestamped audit event with correlation identifier and shall exclude credentials, session tokens, and full financial values. | **Log inspection** |
| **NFR-SEC-011** | **Must** | When sensitive data is stored in production or backup media, the GoalWise system shall use provider-managed encryption at rest and shall restrict database and backup access to the application service and authorized operators. | **Infrastructure inspection** |
| **NFR-SEC-012** | **Must** | When a release candidate is tested, all authentication and account-management endpoints shall be rate limited and every state-changing endpoint shall reject unauthenticated requests in 100 percent of approved security tests. | **Security test** |

## 6.5 Privacy

| **ID** | **Priority** | **EARS requirement** | **Verification** |
|:--:|:--:|:---|:--:|
| **NFR-PRI-001** | **Must** | While operating the MVP, the GoalWise system shall not request or store bank credentials, bank account numbers, payment-card data, government identifiers, or automatic-transfer instructions. | **Inspection/Test** |
| **NFR-PRI-002** | **Must** | When an account deletion is confirmed, the GoalWise system shall remove user-owned production data within 30 days and shall allow encrypted backups containing the data to expire within 35 days. | **Retention audit** |
| **NFR-PRI-003** | **Future** | Where AI explanations are enabled, the GoalWise system shall send none of the user's email address, authentication data, raw transaction descriptions, full financial profile, or snapshot identifiers to the AI provider. | **Payload inspection** |

## 6.6 Accessibility and Usability

| **ID** | **Priority** | **EARS requirement** | **Verification** |
|:--:|:--:|:---|:--:|
| **NFR-A11Y-001** | **Must** | When the production user interface is audited, the GoalWise system shall conform to WCAG 2.2 Level AA for the implemented workflows and shall have zero Critical accessibility violations in the automated audit. | **Audit/Test** |
| **NFR-A11Y-002** | **Must** | When a keyboard-only user completes registration, goal setup, financial input, dashboard review, calculation review, export, and deletion, the GoalWise system shall provide visible focus and operable controls without a keyboard trap. | **Keyboard test** |
| **NFR-USAB-001** | **Must** | When at least five first-time target users perform the core workflow, at least 80 percent shall complete account creation, goal setup, financial inputs, and dashboard review within 10 minutes without facilitator assistance. | **Usability test** |
| **NFR-USAB-002** | **Must** | When an input error occurs, the GoalWise system shall describe the problem and corrective action in plain language with no unexplained technical code in 100 percent of reviewed validation messages. | **Content review** |

## 6.7 Maintainability and Portability

| **ID** | **Priority** | **EARS requirement** | **Verification** |
|:--:|:--:|:---|:--:|
| **NFR-MNT-001** | **Must** | When backend interfaces change incompatibly, the GoalWise team shall publish the change under a new API version and shall preserve /api/v1 behavior for the released MVP. | **Inspection** |
| **NFR-MNT-002** | **Must** | Before a merge to the protected main branch, the pace engine shall maintain at least 90 percent branch coverage and the backend shall maintain at least 75 percent line coverage. | **CI coverage gate** |
| **NFR-MNT-003** | **Must** | Before code reaches the protected main branch, the GoalWise repository shall require a passing CI build and approval from at least one reviewer other than the author. | **Repository inspection** |
| **NFR-PORT-001** | **Must** | When tested in the current and immediately previous major versions of Chrome, Firefox, and Edge and the current Safari release, all Must workflows shall complete without a browser-specific blocker. | **Cross-browser test** |

## 6.8 Observability and Continuity

| **ID** | **Priority** | **EARS requirement** | **Verification** |
|:--:|:--:|:---|:--:|
| **NFR-OBS-001** | **Must** | When an API request enters the backend, the GoalWise system shall assign or preserve a correlation identifier and include it in the response and all server logs associated with the request. | **Integration test** |
| **NFR-OBS-002** | **Must** | When the production error rate exceeds 5 percent for five consecutive minutes or the service becomes unavailable, the monitoring system shall notify the designated operator within five additional minutes. | **Monitoring test** |
| **NFR-BCP-001** | **Must** | When a production database backup job runs, the GoalWise system shall create an encrypted backup at least once every 24 hours and shall demonstrate a recovery point objective of 24 hours and a recovery time objective of 4 hours. | **Backup/restore test** |

# 7. Data Requirements

## 7.1 Data Classification

| **Class** | **Examples** | **Required handling** |
|:---|:---|:---|
| Public | Landing-page copy, formula documentation, status definitions. | May be cached and logged. |
| Confidential user data | Email, goal, cash, income, expenses, reserve, saved amount. | User isolation, encrypted transport/storage, no public logs. |
| Restricted security data | Password hashes, reset tokens, session keys, provider secrets. | Least privilege, no exports, no application logs. |
| Audit metadata | User ID, action, timestamp, result, correlation ID. | Append-only, no credentials or financial values. |
| Future AI payload | Minimized snapshot outputs and non-identifying context. | Server-side only, inspected against allow-list. |

## 7.2 Validation Rules

| **Field / domain** | **Normative rule** |
|:---|:---|
| Email | Normalized to lowercase for uniqueness; syntactically valid; maximum 254 characters. |
| Goal name / labels | Goal 1-80 characters; income and expense labels 1-100 characters; trimmed. |
| Money | USD; nonnegative unless an output is explicitly allowed to be negative; maximum 999,999,999.99; stored in cents. |
| Dates | ISO calendar dates; target after start; balance-as-of not in future; occurrence window as defined in Section 3. |
| Recurrence | One-time, Weekly, Biweekly, Monthly; next date required; month-end fallback rule. |
| Time zone | Valid IANA identifier; used for weekly plan and display. |
| Lifecycle | Goal status Active, Completed, or Archived; account status Active, Disabled, or DeletionPending. |

## 7.3 Retention and Deletion

- User data remains until verified account deletion or a formally approved retention change.

- Audit metadata is retained for at least 90 days unless the account deletion process requires earlier removal of user-linked data.

- Export links expire after 24 hours.

- Production data is removed within 30 days after deletion confirmation; backup copies expire within 35 days.

- Snapshots are append-only during normal operation but are removed with verified account deletion.

## 7.4 Snapshot Schema Minimum

| **Field** | **Requirement** |
|:---|:---|
| snapshot_id | Opaque unique identifier. |
| user_id / goal_id | Ownership and traceability identifiers. |
| formula_version | pace-v1 for this baseline. |
| input_hash | Hash of canonical normalized input document. |
| normalized_inputs | Goal, profile, expanded forecast totals, baseline, dates, and remaining weeks. |
| outputs | Forecast Resources, Goal Gap, Discretionary Capacity, Projected Shortfall, Weekly Safe-to-Spend, expected saved, pace gap, status. |
| created_at | UTC timestamp. |

# 8. Verification and Product Acceptance

## 8.1 Verification Methods

| **Method** | **Evidence** |
|:---|:---|
| Automated test | Unit, integration, contract, end-to-end, golden, fault-injection, cross-browser, accessibility, or performance result. |
| Security test | SAST, dependency scan, authorization tests, DAST, configuration inspection, and remediation evidence. |
| Analysis | Formula walkthrough, capacity calculation, availability report, or retention review. |
| Inspection | Code/configuration review, UI content review, repository control, or documentation audit. |
| Demonstration | Observed end-to-end workflow using the release candidate. |

## 8.2 Golden Test Baseline

| **Test** | **Inputs / condition** | **Expected result** |
|:---|:---|:---|
| GT-01 Positive capacity | Cash 5,000; income 1,000; expenses 500; reserve 500; target 10,000; saved 6,000; 10 weeks. | Forecast 5,000; gap 4,000; capacity 1,000; shortfall 0; weekly 100. |
| GT-02 PDR mockup correction | Cash 3,150; income 5,270; expenses 2,930; reserve 260; target 12,000; saved 4,850; 30 weeks. | Forecast 5,230; gap 7,150; capacity -1,920; shortfall 1,920; weekly 0; At Risk. |
| GT-03 Completed goal | Target 10,000; saved 10,000; forecast resources 2,000; 8 weeks. | Gap 0; shortfall 0; weekly 250; Completed. |
| GT-04 Unconfirmed income | Same as GT-01 but 1,000 income is unconfirmed. | Forecast 4,000; gap 4,000; capacity 0; weekly 0. |
| GT-05 Downward rounding | Discretionary capacity 999 cents; 4 remaining weeks. | Weekly safe-to-spend 2 USD, not 2.50 or 3. |
| GT-06 Monthly boundary | Monthly occurrence starts Jan 31 and target includes Feb 28. | February occurrence date is Feb 28. |

## 8.3 MVP Acceptance Criteria

> **1.** Every Must functional and interface requirement is implemented and has passing evidence.
>
> **2.** Every Must nonfunctional requirement meets its stated measurement or has an instructor-approved exception recorded before release.
>
> **3.** All approved pace-v1 golden tests pass, including the corrected PDR mockup case.
>
> **4.** Pace-engine branch coverage is at least 90 percent and backend line coverage is at least 75 percent.
>
> **5.** No unresolved Critical or High security findings remain.
>
> **6.** The end-to-end demonstration completes account creation, goal setup, manual financial inputs, calculation, dashboard review, calculation trace, export, and deletion.
>
> **7.** CSV import and runtime AI explanation are not required for MVP acceptance.
>
> **8.** The course instructor is the final acceptance authority for the academic release.

## 8.4 Release Evidence Package

- Traceability matrix with requirement status and linked test evidence.

- Golden-test report and coverage report.

- Security, privacy, accessibility, performance, and backup/restore evidence.

- Usability-session summary.

- Known-issues list with severity and disposition.

- Release tag, deployment guide, user guide, and updated ADRs.

# 9. Requirements Traceability Matrix

Each normative requirement traces to a source, objective, use case, design decision, verification method, and test identifier.

| **Requirement** | **Priority** | **Source / rationale** | **Objective** | **Use case** | **ADR** | **Verification / test** |
|:--:|:--:|:---|:--:|:--:|:--:|:---|
| **UIR-001** | **Must** | PDR UI set | OBJ-5 | All | ADR-006 | Test / TC-UI-001 |
| **UIR-002** | **Must** | UI-01 | OBJ-2, OBJ-6 | UC-01 | ADR-002, ADR-005 | Inspection / TC-UI-002 |
| **UIR-003** | **Must** | UI-02..UI-06 | OBJ-5 | UC-02..UC-05 | ADR-006 | Test / TC-UI-003 |
| **UIR-004** | **Must** | PDR feedback | OBJ-5 | UC-02, UC-03 | ADR-006 | Test / TC-UI-004 |
| **UIR-005** | **Must** | UI-05 trust boundary | OBJ-1, OBJ-3 | UC-04, UC-05 | ADR-001, ADR-006 | Inspection/Test / TC-UI-005 |
| **UIR-006** | **Must** | SPMP 6.3 | OBJ-1, OBJ-3 | All | ADR-006 | Contract test / TC-UI-006 |
| **UIR-007** | **Must** | PDR clarified NFRs | OBJ-4, OBJ-5 | All | ADR-006 | Contract test / TC-UI-007 |
| **UIR-008** | **Must** | Weekly local week glossary | OBJ-3, OBJ-5 | UC-04, UC-05 | ADR-007 | Test / TC-UI-008 |
| **FR-AUTH-001** | **Must** | SPMP MVP scope | OBJ-2, OBJ-4 | UC-01 | ADR-006 | Test / TC-AUTH-001 |
| **FR-AUTH-002** | **Must** | SPMP MVP scope | OBJ-4 | UC-01 | ADR-006 | Test / TC-AUTH-002 |
| **FR-AUTH-003** | **Must** | Security requirement | OBJ-4 | UC-01 | ADR-006 | Test / TC-AUTH-003 |
| **FR-AUTH-004** | **Must** | SPMP MVP scope | OBJ-4 | UC-01 | ADR-006 | Test / TC-AUTH-004 |
| **FR-AUTH-005** | **Should** | Authentication completeness | OBJ-4, OBJ-5 | UC-01 | ADR-006 | Test / TC-AUTH-005 |
| **FR-GOAL-001** | **Must** | UI-02 | OBJ-2 | UC-02 | ADR-002 | Test / TC-GOAL-001 |
| **FR-GOAL-002** | **Must** | PDR sharpened validation | OBJ-1, OBJ-5 | UC-02 | ADR-002 | Test / TC-GOAL-002 |
| **FR-GOAL-003** | **Must** | SPMP constraint; UI-02 | OBJ-2 | UC-02 | ADR-002 | Test / TC-GOAL-003 |
| **FR-GOAL-004** | **Must** | UI-02 snapshot message | OBJ-2, OBJ-3 | UC-02 | ADR-004 | Test / TC-GOAL-004 |
| **FR-GOAL-005** | **Must** | Goal lifecycle clarification | OBJ-2 | UC-02 | ADR-002 | Test / TC-GOAL-005 |
| **FR-GOAL-006** | **Must** | UI-02 process trace | OBJ-1, OBJ-3 | UC-02 | ADR-001, ADR-004 | Test / TC-GOAL-006 |
| **FR-GOAL-007** | **Must** | PDR missed case | OBJ-3, OBJ-5 | UC-02 | ADR-004 | Test / TC-GOAL-007 |
| **FR-INP-001** | **Must** | UI-03 | OBJ-2 | UC-03 | ADR-003 | Test / TC-INP-001 |
| **FR-INP-002** | **Must** | PDR measurable validation | OBJ-1, OBJ-4 | UC-03 | ADR-003 | Test / TC-INP-002 |
| **FR-INP-003** | **Must** | UI-03 | OBJ-2 | UC-03 | ADR-003 | Test / TC-INP-003 |
| **FR-INP-004** | **Must** | SPMP scope control | OBJ-1 | UC-03 | ADR-001, ADR-003 | Test / TC-INP-004 |
| **FR-INP-005** | **Must** | PDR missed recurrence case | OBJ-1 | UC-03 | ADR-001 | Test / TC-INP-005 |
| **FR-INP-006** | **Must** | UI-03 | OBJ-2 | UC-03 | ADR-003 | Test / TC-INP-006 |
| **FR-INP-007** | **Must** | UI-03; security validation | OBJ-2, OBJ-4 | UC-03 | ADR-003, ADR-006 | Test / TC-INP-007 |
| **FR-INP-008** | **Must** | UI-03 PDR scope note | OBJ-2 | UC-03 | ADR-003 | Test / TC-INP-008 |
| **FR-INP-009** | **Must** | UI-02 process trace | OBJ-1, OBJ-3 | UC-03 | ADR-004 | Test / TC-INP-009 |
| **FR-INP-010** | **Must** | UI-04 opening versus remaining; PDR missed case | OBJ-1, OBJ-5 | UC-04 | ADR-007 | Test / TC-INP-010 |
| **FR-CALC-001** | **Must** | Landing/UI-05 trust boundary | OBJ-1, OBJ-3 | UC-04, UC-05 | ADR-001, ADR-006 | Test / TC-CALC-001 |
| **FR-CALC-002** | **Must** | PDR accuracy clarification | OBJ-1 | UC-04 | ADR-001 | Test / TC-CALC-002 |
| **FR-CALC-003** | **Must** | Glossary; UI-04 remaining weeks | OBJ-1 | UC-04 | ADR-008 | Test / TC-CALC-003 |
| **FR-CALC-004** | **Must** | SPMP scope control; glossary | OBJ-1 | UC-04 | ADR-001 | Test / TC-CALC-004 |
| **FR-CALC-005** | **Must** | Glossary; UI-03 | OBJ-1 | UC-04 | ADR-001 | Test / TC-CALC-005 |
| **FR-CALC-006** | **Must** | SPMP glossary | OBJ-1 | UC-04, UC-05 | ADR-001, ADR-008 | Test / TC-CALC-006 |
| **FR-CALC-007** | **Must** | SPMP glossary | OBJ-1 | UC-04, UC-05 | ADR-001, ADR-008 | Test / TC-CALC-007 |
| **FR-CALC-008** | **Must** | SPMP glossary | OBJ-1 | UC-04, UC-05 | ADR-001, ADR-008 | Test / TC-CALC-008 |
| **FR-CALC-009** | **Must** | SPMP glossary and downward-rounding control | OBJ-1 | UC-04, UC-05 | ADR-001, ADR-008 | Test / TC-CALC-009 |
| **FR-CALC-010** | **Must** | SPMP scope control | OBJ-1 | UC-04 | ADR-008 | Test / TC-CALC-010 |
| **FR-CALC-011** | **Must** | PDR clarified pace status | OBJ-1, OBJ-3 | UC-04 | ADR-008 | Test / TC-CALC-011 |
| **FR-CALC-012** | **Must** | SPMP glossary status list | OBJ-1 | UC-04 | ADR-008 | Test / TC-CALC-012 |
| **FR-CALC-013** | **Must** | UI-04; PDR status precedence | OBJ-1 | UC-04 | ADR-008 | Test / TC-CALC-013 |
| **FR-CALC-014** | **Must** | PDR clarified measurable status thresholds | OBJ-1 | UC-04 | ADR-008 | Test / TC-CALC-014 |
| **FR-CALC-015** | **Must** | UI-05 formula version; auditability | OBJ-1, OBJ-3 | UC-05 | ADR-001, ADR-004 | Test / TC-CALC-015 |
| **FR-SNAP-001** | **Must** | UI-02 process trace | OBJ-3 | UC-02, UC-03 | ADR-004 | Test / TC-SNAP-001 |
| **FR-SNAP-002** | **Must** | UI-05 snapshot trace | OBJ-3, OBJ-4 | UC-05 | ADR-004 | Test / TC-SNAP-002 |
| **FR-SNAP-003** | **Must** | Landing/UI-04 immutable snapshot | OBJ-3, OBJ-4 | UC-05, UC-06 | ADR-004 | Test / TC-SNAP-003 |
| **FR-SNAP-004** | **Must** | PDR reliability clarification | OBJ-3, OBJ-4 | UC-02, UC-03 | ADR-004 | Test / TC-SNAP-004 |
| **FR-WEEK-001** | **Must** | SPMP glossary weekly plan | OBJ-1, OBJ-5 | UC-04 | ADR-007 | Test / TC-WEEK-001 |
| **FR-WEEK-002** | **Must** | SPMP scope control | OBJ-1, OBJ-3 | UC-04 | ADR-007 | Test / TC-WEEK-002 |
| **FR-WEEK-003** | **Must** | SPMP scope control | OBJ-1, OBJ-5 | UC-04 | ADR-007 | Test / TC-WEEK-003 |
| **FR-WEEK-004** | **Must** | UI-04 opening/remaining; PDR missed case | OBJ-1, OBJ-5 | UC-04 | ADR-007 | Test / TC-WEEK-004 |
| **FR-DASH-001** | **Must** | PDR missed empty state | OBJ-5 | UC-02, UC-03 | ADR-006 | Test / TC-DASH-001 |
| **FR-DASH-002** | **Must** | UI-04 | OBJ-3, OBJ-5 | UC-04 | ADR-001, ADR-006 | Test / TC-DASH-002 |
| **FR-DASH-003** | **Must** | UI-04 | OBJ-2, OBJ-5 | UC-04 | ADR-006 | Test / TC-DASH-003 |
| **FR-DASH-004** | **Must** | UI-04 | OBJ-1, OBJ-3 | UC-04 | ADR-004, ADR-007 | Test / TC-DASH-004 |
| **FR-DASH-005** | **Must** | UI-04 | OBJ-3, OBJ-5 | UC-04 | ADR-008 | Test / TC-DASH-005 |
| **FR-DASH-006** | **Must** | UI-05 | OBJ-3 | UC-05 | ADR-004, ADR-006 | Test / TC-DASH-006 |
| **FR-DASH-007** | **Must** | PDR accessibility/refresh feedback | OBJ-3, OBJ-5 | UC-04 | ADR-006 | Test / TC-DASH-007 |
| **FR-DATA-001** | **Must** | SPMP MVP scope | OBJ-3, OBJ-4 | UC-06 | ADR-004, ADR-006 | Test / TC-DATA-001 |
| **FR-DATA-002** | **Must** | Privacy/security clarification | OBJ-4 | UC-06 | ADR-006 | Test / TC-DATA-002 |
| **FR-DATA-003** | **Must** | SPMP MVP scope | OBJ-4 | UC-06 | ADR-006 | Test / TC-DATA-003 |
| **FR-DATA-004** | **Must** | PDR explicit security | OBJ-3, OBJ-4 | UC-06 | ADR-004, ADR-006 | Test / TC-DATA-004 |
| **FR-AI-001** | **Must** | UI-06 PDR scope | OBJ-2, OBJ-6 | UC-F01 | ADR-005 | Test / TC-AI-001 |
| **FR-AI-002** | **Future** | SPMP FR-AI-001 risk reference | OBJ-4, OBJ-6 | UC-F01 | ADR-005 | Test / TC-AI-002 |
| **FR-AI-003** | **Future** | Landing/UI-06 boundary | OBJ-1, OBJ-6 | UC-F01 | ADR-005 | Test / TC-AI-003 |
| **FR-AI-004** | **Future** | SPMP FR-AI-003 risk reference | OBJ-1, OBJ-4, OBJ-6 | UC-F01 | ADR-005 | Test / TC-AI-004 |
| **FR-AI-005** | **Future** | SPMP FR-AI-004/NFR-REL-003 | OBJ-5, OBJ-6 | UC-F01 | ADR-005 | Test / TC-AI-005 |
| **FR-AI-006** | **Future** | SPMP scope controls; UI-06 | OBJ-4, OBJ-6 | UC-F01 | ADR-005 | Test / TC-AI-006 |
| **FR-AI-007** | **Future** | UI-06 runtime guardrails | OBJ-4, OBJ-6 | UC-F01 | ADR-005 | Inspection/Test / TC-AI-007 |
| **FR-ERR-001** | **Must** | PDR error handling | OBJ-3, OBJ-5 | UC-02, UC-03 | ADR-004, ADR-006 | Test / TC-ERR-001 |
| **FR-ERR-002** | **Must** | PDR reliability | OBJ-3, OBJ-5 | UC-04 | ADR-004 | Test / TC-ERR-002 |
| **FR-ERR-003** | **Must** | PDR security/observability | OBJ-4, OBJ-5 | All | ADR-006 | Test / TC-ERR-003 |
| **NFR-ACC-001** | **Must** | SPMP objective/acceptance | OBJ-1 | UC-04, UC-05 | ADR-001, ADR-008 | Automated test / GT-SUITE |
| **NFR-ACC-002** | **Must** | PDR clarified accuracy | OBJ-1 | UC-04 | ADR-001, ADR-008 | Unit test / TC-NACC-002 |
| **NFR-ACC-003** | **Must** | Deterministic objective | OBJ-1, OBJ-3 | UC-05 | ADR-001 | Determinism test / TC-NACC-003 |
| **NFR-PERF-001** | **Must** | SPMP NFR-PERF-001 risk | OBJ-5 | UC-02, UC-03 | ADR-006 | Load test / PT-001 |
| **NFR-PERF-002** | **Must** | PDR measurable NFR | OBJ-5 | UC-04 | ADR-006 | Load/UI test / PT-002 |
| **NFR-PERF-003** | **Must** | Data export scope | OBJ-4, OBJ-5 | UC-06 | ADR-006 | Performance test / PT-003 |
| **NFR-REL-001** | **Must** | PDR reliability | OBJ-3 | UC-02, UC-03 | ADR-004 | Fault-injection test / RT-001 |
| **NFR-REL-002** | **Must** | Snapshot objective | OBJ-3, OBJ-5 | UC-04 | ADR-004 | Recovery test / RT-002 |
| **NFR-REL-003** | **Must** | SPMP objective/NFR-REL-003 | OBJ-5, OBJ-6 | All core | ADR-005 | Dependency-isolation test / RT-003 |
| **NFR-REL-004** | **Must** | SPMP infrastructure | OBJ-5 | All | ADR-006 | Monitoring analysis / AT-001 |
| **NFR-SEC-001** | **Must** | SPMP infrastructure | OBJ-4 | All | ADR-006 | Security scan / ST-001 |
| **NFR-SEC-002** | **Must** | PDR explicit security | OBJ-4 | UC-01 | ADR-006 | Inspection/Test / ST-002 |
| **NFR-SEC-003** | **Must** | PDR explicit security | OBJ-4 | UC-01 | ADR-006 | Security test / ST-003 |
| **NFR-SEC-004** | **Must** | PDR explicit security | OBJ-4 | UC-01 | ADR-006 | Security test / ST-004 |
| **NFR-SEC-005** | **Must** | PDR explicit security | OBJ-4 | All | ADR-006 | Authorization test / ST-005 |
| **NFR-SEC-006** | **Must** | SPMP NFR-SEC-006 | OBJ-4 | All | ADR-006 | SAST/DAST / ST-006 |
| **NFR-SEC-007** | **Must** | PDR explicit security | OBJ-4 | All | ADR-006 | Security test / ST-007 |
| **NFR-SEC-008** | **Must** | SPMP secure secret management | OBJ-4 | All | ADR-006 | Repository/infra inspection / ST-008 |
| **NFR-SEC-009** | **Must** | SPMP NFR-SEC-009/acceptance | OBJ-4 | All | ADR-006 | CI security gate / ST-009 |
| **NFR-SEC-010** | **Must** | PDR explicit security | OBJ-3, OBJ-4 | All | ADR-004, ADR-006 | Log inspection / ST-010 |
| **NFR-SEC-011** | **Must** | PDR explicit security | OBJ-4 | All | ADR-006 | Infrastructure inspection / ST-011 |
| **NFR-SEC-012** | **Must** | PDR explicit security | OBJ-4 | All | ADR-006 | Security test / ST-012 |
| **NFR-PRI-001** | **Must** | SPMP scope controls | OBJ-4 | UC-03 | ADR-003 | Inspection/Test / PRT-001 |
| **NFR-PRI-002** | **Must** | Data deletion scope | OBJ-4 | UC-06 | ADR-004, ADR-006 | Retention audit / PRT-002 |
| **NFR-PRI-003** | **Future** | SPMP NFR-PRI-003 | OBJ-4, OBJ-6 | UC-F01 | ADR-005 | Payload inspection / PRT-003 |
| **NFR-A11Y-001** | **Must** | SPMP quality standards | OBJ-5 | All UI | ADR-006 | Audit/Test / AX-001 |
| **NFR-A11Y-002** | **Must** | PDR accessibility | OBJ-5 | All UI | ADR-006 | Keyboard test / AX-002 |
| **NFR-USAB-001** | **Must** | PDR measurable NFR | OBJ-5 | UC-01..UC-04 | ADR-006 | Usability test / UT-001 |
| **NFR-USAB-002** | **Must** | PDR usability | OBJ-5 | UC-02, UC-03 | ADR-006 | Content review / UT-002 |
| **NFR-MNT-001** | **Must** | SPMP /api/v1 | OBJ-3 | All | ADR-006 | Inspection / MT-001 |
| **NFR-MNT-002** | **Must** | SPMP NFR-MNT-002/quality | OBJ-1, OBJ-3 | All | ADR-001 | CI coverage gate / MT-002 |
| **NFR-MNT-003** | **Must** | SPMP configuration management | OBJ-3, OBJ-4 | All | ADR-006 | Repository inspection / MT-003 |
| **NFR-PORT-001** | **Must** | SPMP client layer | OBJ-5 | All UI | ADR-006 | Cross-browser test / BT-001 |
| **NFR-OBS-001** | **Must** | PDR observability | OBJ-3, OBJ-4 | All | ADR-006 | Integration test / OT-001 |
| **NFR-OBS-002** | **Must** | SPMP monitoring/logging | OBJ-5 | All | ADR-006 | Monitoring test / OT-002 |
| **NFR-BCP-001** | **Must** | SPMP automated backups | OBJ-3, OBJ-5 | All | ADR-006 | Backup/restore test / BCT-001 |

| **Traceability maintenance.** When a requirement changes, the team shall update the requirement text, revision history, linked ADR, test identifier, and this matrix in the same pull request. |
|----|

# 10. PDR Alignment Actions

| **Action** | **Required change** | **Owner** | **Due** | **Status** |
|:---|:---|:---|:---|:---|
| A-01 | Correct the dashboard and calculation-detail fixture so the displayed shortfall and weekly allowance match pace-v1. | UI/UX + Backend | Before CDR | Open |
| A-02 | Update SPMP scope, T8 Transaction Import, T10 AI Summary, schedule, risk text, and acceptance flow to match SRS v2.0. | Project Manager | Before CDR | Open |
| A-03 | Add a simple manual current-week discretionary-spending control so Dashboard opening and remaining are explainable. | UI/UX + Frontend | Before UI complete | Open |
| A-04 | Approve the status tolerance max(\$25, 2 percent of target) and baseline-saved rule as the team's official pace classification. | Entire Team | Before implementation lock | Review |
| A-05 | Review security thresholds against the selected hosting and authentication libraries and retain equal-or-stronger controls. | Backend + QA | Before security testing | Open |
| A-06 | Replace prototype-only Spec trace controls or clearly hide them from the production end-user build. | UI/UX | Before beta | Open |
| A-07 | Complete human review of the AI Assistance appendix and record final tools, prompts, corrections, and approvals. | Entire Team | Before submission | Open |

| **Change control.** Closing an action that changes a normative requirement requires an SRS revision or an approved change record; a UI-only correction that implements an existing requirement does not. |
|----|

# Appendix A - AI Assistance and Provenance

| **Responsibility.** Group 3 remains responsible for reviewing, revising, testing, citing, and defending every requirement and design decision in this document. |
|----|

| **Item** | **Entry** |
|:---|:---|
| AI tools used | OpenAI ChatGPT (GPT-5.6 Pro), August 9, 2026. Prior SPMP provenance also identifies Copilot and ChatGPT Deep Research. |
| Materials supplied to AI | GoalWise SPMP v1.0, instructor PDR feedback, and six GoalWise UI mockups. |
| What AI assisted with | Organizing the SRS; drafting EARS requirements; making NFRs measurable; expanding explicit security/privacy controls; reconciling scope; creating the traceability matrix; drafting ADR updates; identifying inconsistent mockup calculations; and formatting the DOCX. |
| Human-authored inputs preserved | GoalWise product concept, one-goal scope, manual financial assumptions, deterministic pace engine, UI direction, technology stack, team roles, and AI explain-only boundary. |
| Key prompt / specification | Create GoalWise SRS Version 2.0 from the supplied SPMP, professor feedback, and UI mockups; use EARS; include measurable NFRs, explicit security, traceability, revision history, AI provenance, and ADR updates. |
| AI-generated draft content | Initial requirement wording, formula clarification, testable thresholds, trace links, tables, and document layout. |
| Material correction identified | The mockup values \$740 projected shortfall and \$192 weekly safe-to-spend do not follow the stated input values and glossary formulas; the normative result is \$1,920 shortfall and \$0 weekly safe-to-spend. |
| Human review required | All four members must verify the pace formula, expected-pace threshold, current-week workflow, security feasibility, priorities, test cases, dates, and cross-document scope before submission. |
| Validation approach | Cross-review by project, backend, UI/UX, and QA owners; execute golden tests, security/privacy checklist, accessibility and usability tests, and traceability audit. |
| Citation / acknowledgment | OpenAI ChatGPT assistance, August 9, 2026. Retain this appendix in the submitted SRS to satisfy AI-provenance requirements. |

# Appendix B - Architecture Decision Record Updates

The following ADR summaries are updated for the SRS Version 2.0 baseline. The SDD may expand these records, but it shall not contradict their decisions without approved change control.

## ADR-001 Backend-owned deterministic pace engine

| **Status** | Accepted - reaffirmed in v2.0 |
|----|----|
| **Context** | Financial guidance must be reproducible and independent of UI or AI behavior. |
| **Decision** | Implement pace-v1 as a pure backend service using integer-cent arithmetic. The frontend renders returned values only. |
| **Consequences** | Improves auditability and testing; prevents client drift; requires API calls for official results. |

## ADR-002 One Active goal and USD-only MVP

| **Status** | Accepted - reaffirmed in v2.0 |
|----|----|
| **Context** | The four-person team needs a controlled scope and unambiguous formula behavior. |
| **Decision** | Permit one Active goal per user and represent all Version 2.0 money in USD. |
| **Consequences** | Simplifies data model and UI; multiple goals and currencies remain deferred. |

## ADR-003 Manual financial inputs only

| **Status** | Revised after PDR |
|----|----|
| **Context** | The SPMP listed CSV import, but the PDR mockup explicitly defers CSV import, bank sync, and transaction correction. |
| **Decision** | Limit the MVP to manual profile, income, expense, reserve, and weekly-spend entry. |
| **Consequences** | Reduces integration/privacy risk; SPMP task and acceptance sections must be updated. |

## ADR-004 Immutable versioned calculation snapshots

| **Status** | Accepted - sharpened in v2.0 |
|----|----|
| **Context** | Users and reviewers need to reproduce every official result and formula version. |
| **Decision** | Write an append-only snapshot with normalized inputs, outputs, input hash, formula version, and timestamp in the same transaction as the triggering change. |
| **Consequences** | Supports auditability and rollback; increases storage and requires retention handling. |

## ADR-005 AI at the edge, explain-only, and deferred

| **Status** | Revised after PDR |
|----|----|
| **Context** | The AI mockup defines a future layer and the product must remain reliable without AI. |
| **Decision** | Disable runtime AI in the MVP. Future AI may explain committed snapshots only through minimized payloads, schema validation, and deterministic fallback. |
| **Consequences** | Eliminates MVP dependency and calculation risk; future integration has explicit guardrails. |

## ADR-006 REST backend as source of truth

| **Status** | Accepted - reaffirmed in v2.0 |
|----|----|
| **Context** | The UI must remain responsive while validation, authorization, and calculation stay centralized. |
| **Decision** | Use React/Next.js with FastAPI /api/v1 and PostgreSQL; all protected behavior is server-authorized. |
| **Consequences** | Clear trust boundary and contract tests; requires robust API errors and observability. |

## ADR-007 Frozen weekly opening allowance

| **Status** | New in v2.0 |
|----|----|
| **Context** | The SPMP says the current week is separate from next-week recalculation, and the dashboard shows opening and remaining. |
| **Decision** | Create one Monday-Sunday weekly plan, freeze its opening, and change remaining only through manual current-week spending; show new calculations as next-week recommendations. |
| **Consequences** | Prevents midweek allowance churn; requires weekly-plan state and a simple spending control. |

## ADR-008 Normative formula and status classification

| **Status** | New in v2.0 |
|----|----|
| **Context** | Mockup values and prior wording were insufficient to implement or test pace status consistently. |
| **Decision** | Adopt the Section 3 formulas, status precedence, linear expected pace, and tolerance max(\$25, 2 percent of target). |
| **Consequences** | Enables golden tests and consistent UI; team must approve thresholds before implementation lock. |

# Appendix C - Glossary and Data Dictionary

| **Term** | **Definition** |
|:---|:---|
| Active goal | The single savings goal currently used by the pace engine. |
| Available / starting cash | Liquid money available as of the balance-as-of date, excluding money already recorded as current goal savings. |
| Balance-as-of date | The date on which starting cash is accurate and after which forecast occurrences are counted. |
| Confirmed income | An income source the user expects with sufficient certainty and that is included in the forecast. |
| Current goal savings | Money already set aside toward the goal and not included in starting cash. |
| Discretionary Capacity | Forecast Resources minus Goal Gap. |
| EARS | Easy Approach to Requirements Syntax. |
| Expected saved | The linearly interpolated saved amount expected by the current as-of date. |
| Forecast Resources | Starting cash plus Confirmed future income minus planned future expenses and reserve buffer. |
| Formula version | Identifier stored with each snapshot so official financial behavior can be reproduced. |
| Goal Gap | Target amount minus current saved amount, never below zero. |
| Golden test | A manually verified input/output case used as an authoritative automated calculation test. |
| MVP | Minimum Viable Product required for the course release. |
| Pace status | Completed, At Risk, Ahead, Off Pace, or On Track under Section 3.4. |
| Planned expense | A future obligation entered by the user and subtracted from Forecast Resources. |
| Projected Shortfall | The amount by which Goal Gap exceeds Forecast Resources. |
| Reserve buffer | User-confirmed cash withheld from spendable funds to reduce optimistic guidance. |
| Snapshot | Immutable record of normalized calculation inputs, outputs, formula version, and timestamp. |
| Weekly plan | The opening allowance fixed for a Monday-through-Sunday local week plus manual spending and remaining amount. |
| Weekly Safe-to-Spend | Conservatively rounded positive Discretionary Capacity allocated across remaining weeks. |

## Core Field Dictionary

| **Field** | **Type** | **Rule** |
|:---|:---|:---|
| User.email | string | Unique normalized email; confidential. |
| User.time_zone | string | IANA time-zone identifier. |
| Goal.name | string | 1-80 characters. |
| Goal.target_amount_cents | integer | Positive USD cents. |
| Goal.current_saved_cents | integer | Nonnegative USD cents. |
| Goal.start_date / target_date | date | Target later than start. |
| FinancialProfile.starting_cash_cents | integer | Nonnegative USD cents. |
| FinancialProfile.balance_as_of | date | Not later than current local date. |
| FinancialProfile.reserve_buffer_cents | integer | Nonnegative USD cents. |
| IncomeSource.confirmed | boolean | Only true sources count. |
| IncomeSource / PlannedExpense.recurrence | enum | One-time, Weekly, Biweekly, Monthly. |
| WeeklyPlan.week_start | date | Local Monday. |
| WeeklyPlan.opening_cents | integer | Frozen for week. |
| WeeklyPlan.spent_cents | integer | Manual nonnegative total. |
| CalculationSnapshot.formula_version | string | pace-v1. |
| CalculationSnapshot.input_hash | string | Hash of canonical normalized inputs. |

# Appendix D - UI Mockups

Supplied PDR visuals are non-normative illustrations. Requirements and formulas in this SRS control.

<figure>
<img src="media/image1.png" title="Figure D-1" style="width:8.25in;height:6.32672in" alt="Figure D-1. GoalWise public landing page mockup." />
<figcaption aria-hidden="true"><p>Figure D-1. GoalWise public landing page mockup.</p></figcaption>
</figure>

<figure>
<img src="media/image2.png" title="Figure D-2" style="width:9.75in;height:6.09375in" alt="Figure D-2. Goal setup mockup." />
<figcaption aria-hidden="true"><p>Figure D-2. Goal setup mockup.</p></figcaption>
</figure>

<figure>
<img src="media/image3.png" title="Figure D-3" style="width:9.75in;height:6.09375in" alt="Figure D-3. Manual financial inputs mockup." />
<figcaption aria-hidden="true"><p>Figure D-3. Manual financial inputs mockup.</p></figcaption>
</figure>

<figure>
<img src="media/image4.png" title="Figure D-4" style="width:9.5in;height:7.03594in" alt="Figure D-4. MVP dashboard mockup." />
<figcaption aria-hidden="true"><p>Figure D-4. MVP dashboard mockup.</p></figcaption>
</figure>

<figure>
<img src="media/image5.png" title="Figure D-5" style="width:9.75in;height:6.09375in" alt="Figure D-5. Calculation details and snapshot trace mockup." />
<figcaption aria-hidden="true"><p>Figure D-5. Calculation details and snapshot trace mockup.</p></figcaption>
</figure>

<figure>
<img src="media/image6.png" title="Figure D-6" style="width:9.75in;height:6.09375in" alt="Figure D-6. Deferred AI explanation guardrails mockup." />
<figcaption aria-hidden="true"><p>Figure D-6. Deferred AI explanation guardrails mockup.</p></figcaption>
</figure>
