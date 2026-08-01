**\
MSCS 2101 — Software Engineering**

Software Requirements Specification

**GoalWise**

*Goal-Oriented Budgeting and Weekly Spending Pace*

Team: Group 3\
Version: 1.0\
Date: July 26, 2026

| **Member** | **Assigned Role(s)**                                      |
|------------|-----------------------------------------------------------|
| Vishal     | Project Manager / Leader                                  |
| Nati       | Assistant Project Manager; Software Engineer / Programmer |
| Ashutosh   | UI/UX Designer                                            |
| Thanh      | Quality Assurance & Documentation                         |

# Document Control

| **Version** | **Date** | **Owner** | **Summary** |
|----|----|----|----|
| 1.0 | Jul 24, 2026 | Group 3 | Initial team draft based on the approved GoalWise proposal and course EARS/AI-era model. |

# Contents

1\. Introduction

2\. Overall Description

3\. System Context and Product Model

4\. Specific Requirements

> 4.1 EARS Conventions
>
> 4.2 Functional Requirements
>
> 4.3 External Interface Requirements
>
> 4.4 Non-Functional and Quality Requirements
>
> 4.5 Security Abuse and Misuse Cases
>
> 4.6 Data Requirements

5\. Verification and Acceptance

Appendix A — AI Assistance & Provenance

Appendix B — Traceability Matrix

Appendix C — Glossary

# 1. Introduction

## 1.1 Purpose

This Software Requirements Specification (SRS) defines the functional,
interface, data, security, artificial intelligence, and quality
requirements for GoalWise, a goal-oriented budgeting web application.
The document is intended for Group 3, the course instructor, reviewers,
testers, and any developer or software agent asked to design, implement,
or verify the system. Requirements are written to be testable and
sufficiently specific that implementation can proceed without relying on
undocumented assumptions.

## 1.2 Scope

GoalWise helps a user pursue one near-term savings goal by converting
current financial resources, confirmed future income, planned expenses,
a reserve buffer, and the remaining time into a conservative weekly
safe-to-spend amount. The application is forward-looking: when relevant
financial information changes, the deterministic pace engine
recalculates the amount available for future weeks and explains the
reason for the change.

**In scope for v1.0:**

- Account creation and authenticated access to user-owned financial
  data.

- One active savings goal with a target amount, current saved amount,
  and target date.

- Manual entry of available cash, confirmed or unconfirmed income,
  recurring expenses, and a reserve buffer.

- CSV import of transaction data using a published template.

- Deterministic safe-to-spend, goal-feasibility, and pace-status
  calculations.

- A dashboard showing goal progress, the current weekly plan,
  assumptions, and calculation explanations.

- Optional AI-generated weekly summaries derived only from validated
  deterministic results.

- Data correction, export, and account/data deletion.

**Out of scope for v1.0:**

- Live bank synchronization, storage of online-banking credentials, or
  Plaid production integration.

- Automatic money transfers, bill payments, lending, investment
  execution, credit scoring, or tax calculations.

- Multiple simultaneous savings goals, household sharing, social feeds,
  or financial-advisor features.

- Guaranteed financial outcomes or personalized legal, tax, credit, or
  investment advice.

- Native iOS or Android applications and offline-first operation.

## 1.3 Intended Audience

The primary readers are the development team and course instructor.
Secondary readers include potential users participating in usability
tests, reviewers evaluating feasibility and risk, and future maintainers
who need to understand the original product boundaries and acceptance
criteria.

## 1.4 Definitions, Acronyms, and Abbreviations

EARS — Easy Approach to Requirements Syntax; NFR — Non-Functional
Requirement; MVP — Minimum Viable Product; LLM — Large Language Model;
CSV — Comma-Separated Values; TLS — Transport Layer Security; WCAG — Web
Content Accessibility Guidelines; ASVS — Application Security
Verification Standard; PII — Personally Identifiable Information.
Additional terms appear in Appendix C.

## 1.5 References

**\[R1\]** Group 3, GoalWise Project Proposal and product research
notes, July 2026.

**\[R2\]** MSCS 2101 EARS/AI-era SRS Worked Example: Trailhead, 2026.

**\[R3\]** IEEE Std 830-1998, Recommended Practice for Software
Requirements Specifications.

**\[R4\]** NIST SP 800-218, Secure Software Development Framework
(SSDF). [<u>Source link</u>](https://csrc.nist.gov/projects/ssdf)

**\[R5\]** OWASP Application Security Verification Standard (ASVS).
[<u>Source
link</u>](https://owasp.org/www-project-application-security-verification-standard/)

**\[R6\]** W3C Web Content Accessibility Guidelines (WCAG) 2.2.
[<u>Source link</u>](https://www.w3.org/TR/WCAG22/)

**\[R7\]** NIST Artificial Intelligence Risk Management Framework 1.0.
[<u>Source
link</u>](https://www.nist.gov/itl/ai-risk-management-framework)

**\[R8\]** Federal Reserve, Economic Well-Being of U.S. Households in
2025: Income and Expenses, 2026. [<u>Source
link</u>](https://www.federalreserve.gov/publications/2026-economic-well-being-of-us-households-in-2025-Income-and-Expenses.htm)

**\[R9\]** Gargano and Rossi, “Goal Setting and Saving in the FinTech
Era,” Journal of Finance, 2024. [<u>Source
link</u>](https://ideas.repec.org/a/bla/jfinan/v79y2024i3p1931-1976.html)

**\[R10\]** OpenAI ChatGPT (GPT-5.6 Thinking) and ChatGPT Deep Research
assistance, July 2026; see Appendix A.

## 1.6 Document Overview

Section 2 describes the product, users, constraints, and assumptions.
Section 3 defines the architecture, calculation model, and primary
workflows. Section 4 contains detailed EARS functional requirements,
measurable non-functional requirements, security abuse cases, and data
requirements. Section 5 defines verification. Appendix A records AI
assistance and human review, Appendix B provides traceability, and
Appendix C provides the glossary.

# 2. Overall Description

## 2.1 Product Perspective

GoalWise is a new, self-contained, responsive web application. It does
not replace a bank, accounting system, or professional financial
advisor. It accepts user-entered financial assumptions and transaction
files, stores user-owned data in its own database, executes a versioned
deterministic pace calculation, and optionally calls an external LLM
service to translate validated results into plain language. The MVP
deliberately avoids live banking integrations so that the team can focus
on correctness, transparency, privacy, and deliverability.

## 2.2 Product Vision and Differentiation

Traditional budgeting products commonly organize behavior around
spending categories and retrospective monthly reports. GoalWise
organizes the experience around one outcome: reaching a stated savings
amount by a stated date. Its primary user question is “Am I still on
pace, and what can I safely spend this week?” The competitive
distinction is not that goals or safe-to-spend concepts are entirely
new, but that GoalWise combines one-goal focus, conservative treatment
of uncertain income, weekly pacing, automatic recalculation, and an
explainable formula in a deliberately simple workflow.

## 2.3 Product Functions — Summary

- Create an account and maintain a private financial profile.

- Create and edit one active savings goal.

- Record available cash, income sources, recurring expenses, and a
  reserve buffer.

- Import and correct transactions from a defined CSV format.

- Calculate current cash, goal gap, forecast resources, shortfall or
  discretionary capacity, safe-to-spend, and pace status.

- Preserve calculation snapshots so changes can be explained and tested.

- Display a responsive dashboard with progress, weekly plan,
  assumptions, and alerts.

- Generate an optional weekly AI summary without delegating financial
  calculations to AI.

- Export or delete the user’s stored data.

## 2.4 User Classes and Characteristics

| **User class** | **Description** | **Experience** | **Permissions** |
|----|----|----|----|
| Registered user | Graduate student, young professional, intern, stipend recipient, or part-time worker saving for a near-term goal. | Comfortable with standard web forms; no finance or technical expertise assumed. | Own account, goals, financial inputs, imports, dashboard, export, deletion. |
| Unauthenticated visitor | Person who has not signed in. | Typical web user. | View landing page, product explanation, and sign-in/register screens only. |
| Team tester / demo operator | Team member using synthetic data during development and demonstration. | Technical familiarity. | Use test accounts and seeded datasets; no access to other real users’ data. |

## 2.5 Stakeholders

| **Stakeholder** | **Need / concern** | **How represented in this SRS** |
|----|----|----|
| Target users | A low-friction, understandable plan that does not overstate safe spending. | Goal, pace, usability, explanation, correction, and privacy requirements. |
| Development team | Stable scope and testable behavior. | EARS requirements, formulas, interfaces, traceability, and priorities. |
| Course instructor | Evidence of sound requirements engineering and responsible AI use. | Measurable NFRs, security/misuse cases, verification, provenance, roles. |
| Future maintainer | Clear assumptions and repeatable calculations. | Versioned formula, data model, test mappings, and glossary. |
| LLM service provider, if enabled | Receives only the minimum payload required. | AI data-minimization and fallback requirements. |

## 2.6 Operating Environment

- Responsive web application supporting current stable versions of
  Chrome, Firefox, Safari, and Edge.

- Frontend implemented with React or Next.js; backend REST API
  implemented with Python FastAPI.

- PostgreSQL for hosted environments; SQLite may be used for isolated
  local development and automated tests.

- HTTPS-capable hosting for all non-local environments.

- Optional external LLM API accessed only from the backend.

## 2.7 Constraints

- The project must be feasible for four students within the July
  19–September 13, 2026 development period.

- No production bank connection or bank credential handling is permitted
  in v1.0.

- The core financial result must be deterministic, versioned,
  explainable, and testable without an AI service.

- Only one active savings goal is supported in v1.0.

- Currency is U.S. dollars; time zone is the user-selected IANA time
  zone, defaulting to America/Los_Angeles.

- Weekly planning cycles begin Monday at 00:00 in the user’s configured
  time zone.

- All demonstrations must use synthetic, seeded, or team-owned test
  data.

## 2.8 Assumptions and Dependencies

- Users provide accurate starting cash, goal savings, income, expense,
  and transaction information.

- Only income marked confirmed is included in the default forecast;
  unconfirmed income is displayed but excluded.

- Imported transactions use the required CSV schema or are transformed
  by the user before upload.

- The hosting platform provides a managed HTTPS endpoint and persistent
  database.

- AI summaries depend on a configured provider, but all core functions
  must remain available when that provider is absent or unavailable.

- The application is an educational planning aid, not a fiduciary,
  banking, credit, tax, or investment service.

## 2.9 Team Roles

| **Member** | **Course role(s)** | **Primary SRS / development ownership** |
|----|----|----|
| Vishal | Project Manager / Leader | Product scope, stakeholder needs, priorities, backlog, acceptance decisions. |
| Nati | Assistant Project Manager; Software Engineer / Programmer | Architecture, pace engine, API, backend, AI boundaries, technical verification. |
| Ashutosh | UI/UX Designer | Personas, user workflows, interface design, accessibility, usability evaluation. |
| Thanh | Quality Assurance & Documentation | Requirement quality, traceability, test design, security review, document integration. |

# 3. System Context and Product Model

## 3.1 High-Level Architecture

The architecture separates the deterministic pace engine from
user-interface and AI concerns. The pace engine receives normalized data
and returns a structured calculation result. The AI layer may describe
that result but may not modify it.

<img src="media/image2.png" style="width:6.95833in;height:4.05208in" />

Figure 1. GoalWise high-level architecture and separation of the
deterministic financial core from optional AI functions.

## 3.2 Primary Workflow

1\. User creates an account and selects a time zone.

2\. User enters available cash and the date on which that cash value is
accurate.

3\. User creates one savings goal and enters current goal savings.

4\. User enters confirmed/unconfirmed income, recurring expenses, and a
reserve buffer.

5\. The pace engine calculates feasibility, shortfall or discretionary
capacity, remaining weeks, weekly safe-to-spend, and pace status.

6\. User optionally imports transactions dated after the cash balance
date; accepted transactions adjust current cash and trigger
recalculation.

7\. The dashboard displays the current plan and the reasons for any
change.

8\. If enabled, the AI service receives a minimized structured summary
and returns a validated plain-language explanation.

## 3.3 Deterministic Financial Model

The initial v1.0 pace-engine formula is normative for implementation and
testing. Money is represented internally as integer cents. Dates are
evaluated in the user’s configured time zone. The engine shall round the
final weekly safe-to-spend amount downward to the nearest whole U.S.
dollar to avoid optimistic guidance.

| **Term** | **Definition** |
|----|----|
| Current Cash | Starting available cash + accepted inflow transactions after the balance-as-of date − accepted outflow transactions after that date. |
| Confirmed Future Income | Sum of occurrences of active income sources marked Confirmed with payment dates after the calculation timestamp and on or before the goal target date. |
| Planned Future Expenses | Sum of occurrences of active recurring or one-time planned expenses with due dates after the calculation timestamp and on or before the goal target date. |
| Forecast Resources | Current Cash + Confirmed Future Income − Planned Future Expenses − Reserve Buffer. |
| Goal Gap | max(0, Goal Target Amount − Current Goal Savings). |
| Discretionary Capacity | Forecast Resources − Goal Gap. |
| Remaining Weeks | max(1, ceiling(number of calendar days from calculation date to target date ÷ 7)). |
| Weekly Safe-to-Spend | max(0, floor(Discretionary Capacity ÷ Remaining Weeks to the nearest whole dollar)). |
| Projected Shortfall | max(0, Goal Gap − Forecast Resources). |

**Weekly-cycle rule:** At Monday 00:00 local time, GoalWise stores the
current weekly safe-to-spend amount as that week’s opening allowance.
Discretionary outflows during the week reduce the displayed current-week
remainder. New data still triggers an immediate global recalculation,
but the new per-week amount becomes the opening allowance for the next
weekly cycle. This prevents midweek spending from being counted twice
while ensuring overspending changes future limits.

**Pace status:** The engine calculates expected savings to date using
linear progress from the goal start date and initial saved amount. The
tolerance is max(\$25, 5% of the target amount). Status is evaluated in
order: Completed when Goal Gap = \$0; Off Pace when Forecast Resources
\< Goal Gap; Ahead when Current Goal Savings exceeds expected savings by
at least the tolerance; At Risk when Current Goal Savings trails
expected savings by at least the tolerance; otherwise On Track.

## 3.4 Major Use Cases

| **ID** | **Use case** | **Primary actor** | **Precondition** | **Success outcome** |
|----|----|----|----|----|
| UC-01 | Create financial plan | Registered user | Signed in; no active goal | Valid goal and financial inputs stored; initial plan calculated. |
| UC-02 | Update income or expense | Registered user | Active goal exists | Input stored; new calculation snapshot and explanation created. |
| UC-03 | Import transactions | Registered user | CSV matches template | Valid rows imported once; errors reported by row; plan recalculated. |
| UC-04 | Review weekly pace | Registered user | Active goal and weekly snapshot exist | Dashboard shows allowance, spending, status, and assumptions. |
| UC-05 | Correct transaction | Registered user | Imported or manual transaction exists | Category or exclusion corrected; affected calculations updated. |
| UC-06 | Receive AI summary | Registered user | AI enabled; valid calculation exists | Validated summary displayed or deterministic fallback used. |
| UC-07 | Export/delete data | Registered user | Signed in | Portable export produced or user data deleted after confirmation. |

# 4. Specific Requirements

## 4.1 EARS Conventions

The following EARS patterns are used:

> Ubiquitous — “The system shall …”
>
> Event-driven — “When …, the system shall …”
>
> State-driven — “While …, the system shall …”
>
> Unwanted behavior — “If …, then the system shall …”
>
> Optional feature — “Where …, the system shall …”.
>
> “Must” requirements define the MVP acceptance baseline.
>
> “Should” requirements are planned but may be deferred only through an
> explicit team scope decision.
>
> “Could” requirements are optional enhancements.

## 4.2 Functional Requirements (EARS)

### 4.2.1 Account and Access Requirements

| **ID** | **Requirement (EARS)** | **Priority** | **Verify** |
|----|----|----|----|
| FR-AUTH-001 | When a visitor submits a unique email address and a password of at least 12 characters, the system shall create a user account and store only a salted password hash. | Must | Test |
| FR-AUTH-002 | When a user submits valid credentials, the system shall create an authenticated session and redirect the user to the dashboard. | Must | Test |
| FR-AUTH-003 | While a user is not authenticated, the system shall restrict access to all goals, financial inputs, transactions, calculations, exports, and account settings. | Must | Test |
| FR-AUTH-004 | When an authenticated user signs out, the system shall invalidate the active session token and redirect the user to the sign-in page. | Must | Test |
| FR-AUTH-005 | If a user requests a resource that belongs to another user, then the system shall deny the request and return no financial content from that resource. | Must | Test |

### 4.2.2 Goal Requirements

| **ID** | **Requirement (EARS)** | **Priority** | **Verify** |
|----|----|----|----|
| FR-GOAL-001 | When a user creates a savings goal, the system shall require a goal name, target amount, current saved amount, target date, and user time zone. | Must | Test |
| FR-GOAL-002 | If the target amount is not greater than \$0, the current saved amount is negative or greater than the target amount, or the target date is not later than the current local date, then the system shall reject the goal and identify each invalid field. | Must | Test |
| FR-GOAL-003 | While a user has an active goal, the system shall prevent creation of a second active goal and shall offer the user the choice to edit, complete, or archive the existing goal. | Must | Test |
| FR-GOAL-004 | When a user edits the target amount, current saved amount, target date, or time zone, the system shall save the valid change and create a new calculation snapshot. | Must | Test |
| FR-GOAL-005 | If the current saved amount becomes equal to or greater than the target amount, then the system shall mark the goal Completed, set the goal gap and weekly required contribution to \$0, and preserve the goal history. | Must | Test |

### 4.2.3 Financial Input Requirements

| **ID** | **Requirement (EARS)** | **Priority** | **Verify** |
|----|----|----|----|
| FR-FIN-001 | When a user configures the financial profile, the system shall require available cash and a balance-as-of date that is not in the future. | Must | Test |
| FR-FIN-002 | When a user creates an income source, the system shall require a name, amount, next payment date, frequency, and confidence value of Confirmed or Unconfirmed. | Must | Test |
| FR-FIN-003 | While an income source is marked Unconfirmed, the system shall display it separately and exclude all of its future occurrences from Forecast Resources. | Must | Test |
| FR-FIN-004 | When a user creates a planned expense, the system shall require a name, amount, next due date, frequency, and classification of Essential or Discretionary. | Must | Test |
| FR-FIN-005 | When the pace engine forecasts income or expenses, the system shall generate only occurrences after the calculation timestamp and on or before the goal target date. | Must | Test |
| FR-FIN-006 | When a financial profile is first created, the system shall suggest a reserve buffer equal to 5% of confirmed future income, rounded upward to the nearest whole dollar, and shall require the user to confirm or replace that amount before the first calculation. | Must | Test |
| FR-FIN-007 | When a user adds, edits, deactivates, or deletes an income source, planned expense, available-cash value, balance-as-of date, or reserve buffer, the system shall create a new calculation snapshot. | Must | Test |

### 4.2.4 Transaction Requirements

| **ID** | **Requirement (EARS)** | **Priority** | **Verify** |
|----|----|----|----|
| FR-TXN-001 | When a user uploads a CSV file, the system shall accept a UTF-8 file containing the required headers date, description, and amount, where date uses YYYY-MM-DD and positive amounts are inflows while negative amounts are outflows. | Must | Test |
| FR-TXN-002 | If a CSV file is larger than 5 MB, contains more than 10,000 data rows, omits a required header, or contains an unreadable encoding, then the system shall reject the file before inserting any rows. | Must | Test |
| FR-TXN-003 | When a CSV contains both valid and invalid rows, the system shall import valid rows in one database transaction, reject invalid rows, and return a row-level error report without silently modifying input values. | Must | Test |
| FR-TXN-004 | When a transaction is imported or entered manually, the system shall assign one category from Income, Essential Spending, Discretionary Spending, Transfer, or Ignored, using deterministic rules before any optional AI classification. | Must | Test |
| FR-TXN-005 | If a transaction has the same user, date, amount, and normalized description as an existing transaction, then the system shall flag it as a possible duplicate and exclude it from calculations unless the user explicitly keeps it. | Must | Test |
| FR-TXN-006 | When a user changes a transaction category or duplicate decision, the system shall preserve the original value, record the correction, and recalculate all affected views. | Must | Test |
| FR-TXN-007 | While a transaction date is on or before the balance-as-of date, the system shall exclude the transaction from Current Cash to prevent double counting. | Must | Test |
| FR-TXN-008 | While a transaction is categorized as Transfer or Ignored, the system shall exclude it from discretionary-spending totals and safe-to-spend explanations. | Must | Test |

### 4.2.5 Pace Engine Requirements

| **ID** | **Requirement (EARS)** | **Priority** | **Verify** |
|----|----|----|----|
| FR-PACE-001 | When the system has a valid active goal and financial profile, the pace engine shall calculate Current Cash, Confirmed Future Income, Planned Future Expenses, Reserve Buffer, Forecast Resources, Goal Gap, Discretionary Capacity, Remaining Weeks, Weekly Safe-to-Spend, Projected Shortfall, expected savings to date, and pace status. | Must | Test |
| FR-PACE-002 | The pace engine shall represent monetary inputs and intermediate results as integer cents and shall round the final Weekly Safe-to-Spend downward to the nearest whole U.S. dollar. | Must | Test |
| FR-PACE-003 | When the number of calendar days remaining is fewer than seven, the system shall use one Remaining Week rather than divide by a fractional or zero week. | Must | Test |
| FR-PACE-004 | If Forecast Resources is less than Goal Gap, then the system shall set Weekly Safe-to-Spend to \$0, calculate Projected Shortfall, and mark the goal Off Pace. | Must | Test |
| FR-PACE-005 | When a calculation result differs from the immediately previous snapshot, the system shall identify the changed inputs and the dollar change in Weekly Safe-to-Spend. | Must | Test |
| FR-PACE-006 | When the pace engine runs, the system shall store the calculation timestamp, formula version, normalized inputs, intermediate values, final values, and triggering event in an immutable calculation snapshot. | Must | Test |
| FR-PACE-007 | At Monday 00:00 in the user time zone, the system shall create a weekly plan snapshot using the latest Weekly Safe-to-Spend value as that week’s opening allowance. | Must | Test |
| FR-PACE-008 | While a weekly plan is active, the system shall calculate the current-week remainder as max(\$0, opening allowance minus accepted Discretionary Spending outflows dated within that local week). | Must | Test |
| FR-PACE-009 | When midweek financial data changes, the system shall recalculate the global plan immediately but shall not replace the current week’s opening allowance; the recalculated amount shall be used for the next weekly plan snapshot. | Must | Test |
| FR-PACE-010 | When the system assigns pace status, it shall evaluate status in this order: Completed, Off Pace, Ahead, At Risk, and On Track using the definitions in Section 3.3. | Must | Test |
| FR-PACE-011 | When the current saved amount is less than 50% of the target amount, then the system shall suggest saving recommendations for the user with explanation | Must | Test |

### 4.2.6 Dashboard and Interaction Requirements

| **ID** | **Requirement (EARS)** | **Priority** | **Verify** |
|----|----|----|----|
| FR-UI-001 | While an active goal exists, the dashboard shall display the goal name, target amount, current saved amount, target date, progress percentage, pace status, current-week opening allowance, current-week spending, current-week remainder, and latest Weekly Safe-to-Spend. | Must | Test |
| FR-UI-002 | When a user selects “How was this calculated?”, the system shall display the current values for Current Cash, Confirmed Future Income, Planned Future Expenses, Reserve Buffer, Goal Gap, Remaining Weeks, and the formula version. | Must | Test |
| FR-UI-003 | If any required input is missing or stale, then the dashboard shall identify the missing input and shall not present Weekly Safe-to-Spend as a valid recommendation. | Must | Test |
| FR-UI-004 | When the user changes a valid input, the system shall display the recalculated result and a concise change explanation without requiring a page reload. | Must | Test |
| FR-UI-005 | The system shall provide a progress chart that distinguishes actual goal savings from expected savings to date without relying on color alone. | Must | Test |
| FR-UI-006 | If a user overspends the weekly allowance, the system will not show the weekly safe-to-spend amount in positive, but a negative red number with a button of recommendation for the next week to keep up with the goal. | Must | Test |
| FR-UI-007 | If the period is the last week of the month, then the recommendation is a list of possible ways to reduce personal spending. | Must | Test |
| FR-UI-008 | When a user receives a validation or import error, the system shall identify the affected field or row and provide a corrective action in plain language. | Must | Test |

### 4.2.7 AI Requirements

| **ID** | **Requirement (EARS)** | **Priority** | **Verify** |
|----|----|----|----|
| FR-AI-001 | Where AI summaries are enabled, when a valid weekly calculation exists, the system shall send the AI service only a minimized structured payload containing pace status, allowed aggregate dollar values, percentage change, and up to three discretionary category totals. | Should | Test |
| FR-AI-002 | The system shall not use an AI model to calculate, alter, approve, or override Current Cash, Forecast Resources, Goal Gap, Weekly Safe-to-Spend, Projected Shortfall, or pace status. | Must | Test |
| FR-AI-003 | When the AI service returns a summary, the system shall validate the response against a defined JSON schema and shall reject any numerical value that is not present in the allowed calculation payload. | Must | Test |
| FR-AI-004 | If the AI service times out, fails, returns invalid JSON, includes prohibited advice, or fails numerical validation, then the system shall display a deterministic template summary and preserve all core functionality. | Must | Test |
| FR-AI-005 | While an AI-generated summary is displayed, the system shall label it “AI-generated explanation,” display the calculation timestamp, and provide access to the deterministic calculation details. | Must | Test |
| FR-AI-006 | The AI summary shall not recommend investments, borrowing, credit products, tax actions, legal actions, or guaranteed outcomes, and shall limit spending suggestions to categories and amounts already present in the validated payload. | Must | Test |
| FR-AI-007 | When a user disables AI summaries, the system shall stop sending new financial summary data to the AI provider and shall continue displaying deterministic summaries. | Must | Test |

### 4.2.8 Data Management Requirements

| **ID** | **Requirement (EARS)** | **Priority** | **Verify** |
|----|----|----|----|
| FR-DATA-001 | When a user requests an export, the system shall produce a machine-readable file containing the user profile, goal, financial inputs, transactions, weekly plans, and calculation snapshots owned by that user. | Should | Test |
| FR-DATA-002 | When a user confirms account deletion by re-entering their password, the system shall revoke active sessions, delete user-owned financial data, and schedule backup removal according to NFR-PRI-004. | Must | Test |
| FR-DATA-003 | The system shall not request or store online-banking usernames, online-banking passwords, debit-card PINs, full payment-card numbers, or brokerage credentials. | Must | Test |

## 4.3 External Interface Requirements

### 4.3.1 User Interface

- Responsive browser interface for desktop widths of 1024 pixels or
  greater and mobile widths down to 360 pixels.

- Primary navigation shall expose Dashboard, Goal, Income, Expenses,
  Transactions, Data/Privacy, and Account areas.

- All monetary fields shall display U.S. dollars with two decimal places
  for inputs and details; the headline Weekly Safe-to-Spend may display
  whole dollars after conservative rounding.

- Forms shall display field-level validation and retain valid user
  entries when another field fails.

- Charts shall include text equivalents or accessible tabular summaries.

### 4.3.2 Software Interfaces

- Frontend-to-backend communication shall use a versioned JSON REST API
  under /api/v1.

- The backend shall expose OpenAPI documentation in non-production or
  authorized development environments.

- The persistence layer shall use PostgreSQL in the hosted environment
  and may use SQLite for tests.

- Where enabled, the LLM provider shall be invoked only by the backend
  through a provider adapter so the implementation can be replaced
  without changing pace-engine code.

### 4.3.3 Communication Interfaces

- All non-local client-server traffic shall use HTTPS with TLS 1.2 or
  higher.

- CSV upload shall use multipart/form-data and shall enforce the limits
  in FR-TXN-002 and NFR-SEC-008.

- API responses shall use UTF-8 JSON and standard HTTP status codes;
  validation errors shall use a consistent machine-readable error
  schema.

## 4.4 Non-Functional and Quality Requirements

| **ID** | **Attribute** | **Requirement (measurable)** | **Verification** |
|----|----|----|----|
| NFR-ACC-001 | Calculation accuracy | The pace engine shall match 100% of approved golden test scenarios to the cent for intermediate values and to the specified downward-rounded whole dollar for Weekly Safe-to-Spend. | Automated golden tests |
| NFR-ACC-002 | Determinism | Identical normalized inputs, timestamps, time zone, and formula version shall produce byte-equivalent calculation values. | Repeatability test |
| NFR-PERF-001 | Performance | For a user with up to 10,000 transactions and 100 active financial-input records, 95% of non-AI pace calculations shall complete within 500 ms under a load of 25 concurrent users. | Load test LT-01 |
| NFR-PERF-002 | Performance | The authenticated dashboard shall become interactive within 3 seconds for 90% of test runs on a simulated 10 Mbps connection, excluding AI summary latency. | Browser performance test |
| NFR-PERF-003 | AI latency | Where AI summaries are enabled, 95% of valid AI-summary requests shall complete or fall back within 10 seconds. | Integration timing test |
| NFR-SEC-001 | Security | Passwords shall be stored using Argon2id or bcrypt with a unique salt; plaintext passwords shall not appear in storage, logs, analytics, or error reports. | Configuration and code review |
| NFR-SEC-002 | Security | All non-local client-server traffic shall use HTTPS with TLS 1.2 or higher. | Deployment scan |
| NFR-SEC-003 | Security — brute force | The login endpoint shall rate-limit an account and source address after 5 failed attempts within 10 minutes and shall not reveal whether an email address exists. | Security test ST-01 |
| NFR-SEC-004 | Security — sessions | Authenticated sessions shall expire after 30 minutes of inactivity and no later than 24 hours after issuance; logout and password change shall revoke active sessions. | Session test ST-02 |
| NFR-SEC-005 | Security — authorization | Every protected data request shall perform server-side ownership authorization; the security test suite shall demonstrate zero cross-user reads, writes, exports, or deletions across all protected endpoints. | IDOR test ST-03 |
| NFR-SEC-006 | Security — injection | All database access shall use parameterized queries or ORM bindings, and all client input shall be validated server-side against type, length, range, and allowed-value constraints. | Code review and injection tests |
| NFR-SEC-007 | Security — secrets | API keys, database credentials, and signing secrets shall be supplied through environment or secret-management configuration and shall produce zero findings in repository secret scanning before release. | Secret scan |
| NFR-SEC-008 | Security — upload abuse | CSV files shall be limited to 5 MB and 10,000 rows, stored outside executable paths, parsed as data only, and rejected if the MIME type, encoding, schema, or limits fail validation. | Upload security tests |
| NFR-SEC-009 | Security — dependency risk | The release candidate shall contain zero known Critical or High severity dependency vulnerabilities without a documented instructor-approved exception. | Dependency scan |
| NFR-PRI-001 | Privacy — minimization | The MVP shall not collect bank credentials, payment-card data, government identifiers, or any data not required by the requirements in this SRS. | Data inventory review |
| NFR-PRI-002 | Privacy — logging | Production logs shall exclude raw transaction descriptions, passwords, session tokens, full email addresses, exact account balances, and exact goal amounts. | Log inspection |
| NFR-PRI-003 | Privacy — AI | By default, the AI provider payload shall contain no email address, name, raw merchant description, full transaction list, account identifier, or authentication data; only the fields allowed by FR-AI-001 may be sent. | Payload inspection |
| NFR-PRI-004 | Privacy — deletion | Primary database records shall be deleted within 24 hours of a confirmed account-deletion request; encrypted backup copies shall expire within 30 days. | Deletion audit test |
| NFR-REL-001 | Reliability | A failed CSV import shall not leave a partially committed set of rows; either all valid rows identified in the import result are committed once or none are committed. | Transaction rollback test |
| NFR-REL-002 | Availability | The deployed application shall achieve at least 99% availability during the scheduled course demonstration window, excluding announced maintenance. | Uptime monitor |
| NFR-REL-003 | Graceful degradation | Loss of the AI provider shall not prevent sign-in, data entry, transaction import, pace calculation, dashboard use, export, or deletion. | Fault-injection test |
| NFR-USA-001 | Usability | At least 4 of 5 representative test participants shall create an account, enter a goal and financial profile, and identify Weekly Safe-to-Spend within 5 minutes without instructor assistance. | Moderated usability test |
| NFR-USA-002 | Comprehension | At least 4 of 5 representative test participants shall correctly explain, in their own words, why the displayed Weekly Safe-to-Spend changed after a supplied overspending scenario. | Comprehension test |
| NFR-A11Y-001 | Accessibility | The primary onboarding, dashboard, form, import, and deletion workflows shall meet the team-selected applicable WCAG 2.2 Level AA success criteria with no unresolved critical accessibility finding. | Automated and manual audit |
| NFR-A11Y-002 | Accessibility | All interactive controls shall be operable by keyboard, display a visible focus indicator, and expose an accessible name. | Keyboard and screen-reader test |
| NFR-MNT-001 | Maintainability | The repository shall pass configured formatting, linting, type-checking, and test commands with zero errors on the release branch. | CI pipeline |
| NFR-MNT-002 | Maintainability | The deterministic pace-engine module shall achieve at least 90% branch coverage, and the overall backend shall achieve at least 75% line coverage. | Coverage report |
| NFR-MNT-003 | Maintainability | Formula changes shall require a new formula-version identifier and new or updated golden test cases before merge. | Pull-request checklist |
| NFR-AIQ-001 | AI factual consistency | Across a labeled evaluation set of at least 50 scenarios, 100% of numerical claims in displayed AI summaries shall match values in the allowed deterministic payload. | AI evaluation test |
| NFR-AIQ-002 | AI safety | Across the same evaluation set, zero displayed summaries shall contain investment, credit, tax, legal, borrowing, or guaranteed-outcome recommendations. | AI safety review |
| NFR-AIQ-003 | AI transparency | Every displayed AI summary shall be visibly labeled and paired with a deterministic details view; 100% of tested summaries shall meet this condition. | UI test |

## 4.5 Security Abuse and Misuse Cases

| **ID** | **Abuse / misuse case** | **Potential effect** | **Required control(s)** | **Verification** |
|----|----|----|----|----|
| AB-01 | Attacker attempts credential stuffing or brute-force login. | Account compromise and financial-data exposure. | NFR-SEC-003, generic error messages, session controls. | ST-01, ST-02 |
| AB-02 | Authenticated user changes an identifier to request another user’s goal, transaction, or export. | Cross-user disclosure or modification. | FR-AUTH-005 and NFR-SEC-005 ownership checks on every endpoint. | ST-03 |
| AB-03 | User uploads a malformed, oversized, formula-injection, or binary file disguised as CSV. | Resource exhaustion, parser exploitation, unsafe exported spreadsheets. | FR-TXN-002/003, NFR-SEC-008; neutralize spreadsheet-formula prefixes in exports. | ST-04 |
| AB-04 | Transaction description contains SQL, HTML, script, or template payload. | Injection or cross-site scripting. | NFR-SEC-006; output encoding; parameterized queries. | ST-05 |
| AB-05 | Transaction description contains prompt-injection text intended to alter AI instructions. | Misleading or unauthorized AI output. | Raw descriptions excluded from default AI payload; fixed system prompt; schema and policy validation. | AIT-04 |
| AB-06 | User enters unrealistically high unconfirmed income to inflate spending guidance. | Overly optimistic plan. | FR-FIN-003 excludes unconfirmed income; assumptions shown. | TC-FIN-03 |
| AB-07 | User imports the same transactions repeatedly. | Double-counted spending or income. | FR-TXN-005 duplicate detection and explicit override. | TC-TXN-05 |
| AB-08 | AI invents a dollar amount or recommends borrowing/investing. | Financial harm or false authority. | FR-AI-002/003/004/006; NFR-AIQ-001/002. | AIT-01 to AIT-03 |
| AB-09 | Sensitive financial values are written to logs or analytics. | Privacy breach. | NFR-PRI-002; structured redaction and log review. | ST-06 |
| AB-10 | User treats the output as a guarantee and ignores uncertainty or missing inputs. | Missed goal or unpaid obligations. | FR-UI-003; visible assumptions; educational-use disclaimer; Off Pace shortfall. | UT-03 |
| AB-11 | Malicious user submits extreme values or dates to overflow calculations. | Incorrect calculation or denial of service. | Server-side ranges, integer cents, bounded records, date validation. | ST-07 |
| AB-12 | Deleted user data remains accessible through active sessions or normal queries. | Privacy violation. | FR-DATA-002 and NFR-PRI-004; session revocation and deletion audit. | ST-08 |

## 4.6 Data Requirements

### 4.6.1 Core Entities

| **Entity** | **Required fields (summary)** | **Ownership / relationship** | **Retention** |
|----|----|----|----|
| User | id, email, password_hash, time_zone, created_at, deleted_at | Owns all private records. | Until account deletion; backups ≤30 days. |
| Goal | id, user_id, name, target_cents, initial_saved_cents, current_saved_cents, start_date, target_date, status | One active Goal per User; archived history allowed. | Until user deletion. |
| FinancialProfile | user_id, starting_cash_cents, balance_as_of_date, reserve_buffer_cents | One current profile per User. | Until user deletion. |
| IncomeSource | id, user_id, name, amount_cents, next_date, frequency, confidence, active | Many per User. | Until deleted or user deletion. |
| PlannedExpense | id, user_id, name, amount_cents, next_date, frequency, classification, active | Many per User. | Until deleted or user deletion. |
| Transaction | id, user_id, date, normalized_description, amount_cents, category, source, duplicate_status, original_values | Many per User; corrections retain original values. | Until user deletion. |
| CalculationSnapshot | id, user_id, goal_id, formula_version, trigger, normalized_input_json, result_json, calculated_at | Immutable history for active/archived goal. | Until user deletion. |
| WeeklyPlan | id, user_id, goal_id, week_start, opening_allowance_cents, created_from_snapshot_id | One per local week per active goal. | Until user deletion. |
| AISummary | id, user_id, snapshot_id, provider, model, prompt_version, output, validation_status, created_at | Optional; references a deterministic snapshot. | Until user deletion or explicit removal. |
| AuditEvent | id, user_id, event_type, resource_type, timestamp, non-sensitive metadata | Security and change events without financial values. | 90 days for MVP unless user deletion occurs first. |

### 4.6.2 Data Integrity Rules

- All monetary values shall be stored as integer cents; floating-point
  money storage is prohibited.

- All persisted records shall use server-generated identifiers and
  created/updated timestamps.

- Foreign-key or equivalent application constraints shall prevent
  orphaned user-owned records.

- Calculation snapshots shall be immutable after creation; corrections
  create new snapshots.

- The combination of user_id and normalized duplicate fingerprint shall
  support duplicate detection without preventing an explicit keep
  decision.

- Date/time values shall be stored in UTC where a timestamp is required
  and converted using the user’s IANA time zone for weekly boundaries
  and date presentation.

# 5. Verification and Acceptance

## 5.1 Verification Strategy

Each Must functional requirement shall have at least one automated or
documented manual test before v1.0 acceptance. Core financial
calculations require automated unit and golden tests. API behavior
requires integration tests. Primary workflows require browser-level
end-to-end tests. Security requirements require configuration review and
adversarial tests. Accessibility and usability requirements require both
automated checks and human evaluation. AI requirements require a fixed
labeled evaluation set and fault injection.

| **Verification class** | **Applies to** | **Evidence** |
|----|----|----|
| Unit / golden tests | Formula, validation, recurrence generation, categorization, duplicate detection. | CI test report and coverage report. |
| API integration tests | Authentication, authorization, CRUD, import, export, deletion, AI adapter. | Automated API test results. |
| End-to-end tests | Register, configure plan, import, review dashboard, correct data, delete account. | Browser test report and screenshots. |
| Performance/load tests | NFR-PERF requirements. | Measured percentile report and test configuration. |
| Security tests | NFR-SEC and abuse cases. | Security checklist, scan outputs, and adversarial test results. |
| Accessibility/usability | NFR-A11Y and NFR-USA. | Audit report, participant tasks, observations, and outcomes. |
| AI evaluation | FR-AI and NFR-AIQ. | Scenario set, outputs, validation results, and failures/corrections. |

## 5.2 MVP Acceptance Criteria

- All Must functional requirements pass their mapped tests or have a
  documented, instructor-approved scope change.

- All calculation golden scenarios pass and NFR-ACC-001/002 are
  satisfied.

- No unresolved Critical or High severity security defect remains.

- The full primary workflow can be demonstrated using synthetic data
  without direct database editing.

- The system remains usable when the AI provider is disabled or fails.

- Traceability connects stakeholder needs to requirements, design
  components, and test cases.

- Appendix A accurately records the AI tools, prompts/specifications,
  generated content, human edits, and verification status.

# Appendix A — AI Assistance & Provenance

This appendix records generative-AI assistance used to prepare the
starter SRS. The team remains responsible for reviewing, revising,
testing, citing, and defending every requirement. Before submission,
Group 3 should update this table with any additional tools and the final
human-review status.

| **Item** | **Entry** |
|----|----|
| AI tools used | OpenAI ChatGPT (GPT-5.6 Thinking) for SRS drafting and refinement; ChatGPT Deep Research for background research and source discovery. |
| What AI assisted with | Organizing the IEEE-830/EARS structure; converting the approved GoalWise concept into candidate EARS requirements; proposing measurable NFRs; defining a deterministic formula; identifying abuse/misuse cases; drafting traceability and verification mappings; editing for consistency. |
| Key prompt / specification | “Create a complete starter Software Requirements Specification for GoalWise using the course EARS/AI-era example. Include precise EARS functional requirements, measurable NFRs, security and misuse cases, traceability, AI provenance, team roles, deterministic financial logic, and clear MVP boundaries.” The prompt also included the approved GoalWise concept, course instructions, team roles, and the Trailhead example. |
| Human-authored inputs | The team selected GoalWise; defined the target user, one-goal product concept, forward-looking safe-to-spend value, technology direction, AI use cases, principal risk, mitigation concept, and team roles. |
| AI-generated draft content | Initial prose, requirement wording, proposed thresholds, formula details, architecture description, misuse scenarios, test identifiers, and traceability mappings in this starter document. |
| Human review completed to date | The product concept was reviewed during team ideation. The draft intentionally keeps calculations deterministic, excludes live bank sync, limits the MVP to one active goal, and prevents AI from generating the financial result. |
| Human review still required before submission | All four members must verify formula assumptions and examples; confirm priorities and NFR thresholds; validate security controls against the chosen implementation; review references; add team-authored edits; run a requirement inspection; and record approval. Any unverified requirement must be revised or marked as an assumption rather than submitted as fact. |
| Corrections and scope controls applied | Removed live banking credentials and automatic transfers; limited currency to U.S. dollars; made unconfirmed income non-counting; added conservative downward rounding; separated current-week allowance from next-week recalculation; required deterministic fallback when AI fails; prohibited AI financial advice. |
| How output will be validated | Cross-review by product, technical, UI/UX, and QA owners; golden calculation tests; traceability review; security and privacy checklist; usability test; AI numerical-consistency and prohibited-advice evaluation. |
| Citation / acknowledgment | OpenAI ChatGPT assistance, July 24, 2026. Public sources used for background are listed in Section 1.5. This appendix should be retained in the submitted SRS to satisfy course AI-provenance requirements. |

# Appendix B — Traceability Matrix

The design-element names are proposed components for the later Software
Design Description (SDD). Test identifiers are starter identifiers for
the Software Test Plan (STP) and may be expanded while preserving the
requirement mapping.

| **Requirement** | **Source / need** | **Design element (SDD)** | **Test / evidence (STP)** | **Priority** |
|----|----|----|----|----|
| FR-AUTH-001 | SN-SEC-01 Private access | AuthService | TC-AUTH-001 | Must |
| FR-AUTH-002 | SN-SEC-01 Private access | AuthService | TC-AUTH-002 | Must |
| FR-AUTH-003 | SN-SEC-01 Private access | AuthService | TC-AUTH-003 | Must |
| FR-AUTH-004 | SN-SEC-01 Private access | AuthService | TC-AUTH-004 | Must |
| FR-AUTH-005 | SN-SEC-01 Private access | AuthService | TC-AUTH-005 | Must |
| FR-GOAL-001 | SN-GOAL-01 One outcome | GoalService | TC-GOAL-001 | Must |
| FR-GOAL-002 | SN-GOAL-01 One outcome | GoalService | TC-GOAL-002 | Must |
| FR-GOAL-003 | SN-GOAL-01 One outcome | GoalService | TC-GOAL-003 | Must |
| FR-GOAL-004 | SN-GOAL-01 One outcome | GoalService | TC-GOAL-004 | Must |
| FR-GOAL-005 | SN-GOAL-01 One outcome | GoalService | TC-GOAL-005 | Must |
| FR-FIN-001 | SN-FIN-01 Conservative forecast | FinancialProfileService | TC-FIN-001 | Must |
| FR-FIN-002 | SN-FIN-01 Conservative forecast | FinancialProfileService | TC-FIN-002 | Must |
| FR-FIN-003 | SN-FIN-01 Conservative forecast | FinancialProfileService | TC-FIN-003 | Must |
| FR-FIN-004 | SN-FIN-01 Conservative forecast | FinancialProfileService | TC-FIN-004 | Must |
| FR-FIN-005 | SN-FIN-01 Conservative forecast | FinancialProfileService | TC-FIN-005 | Must |
| FR-FIN-006 | SN-FIN-01 Conservative forecast | FinancialProfileService | TC-FIN-006 | Must |
| FR-FIN-007 | SN-FIN-01 Conservative forecast | FinancialProfileService | TC-FIN-007 | Must |
| FR-TXN-001 | SN-DATA-01 Low-friction updates | TransactionImportService | TC-TXN-001 | Must |
| FR-TXN-002 | SN-DATA-01 Low-friction updates | TransactionImportService | TC-TXN-002 | Must |
| FR-TXN-003 | SN-DATA-01 Low-friction updates | TransactionImportService | TC-TXN-003 | Must |
| FR-TXN-004 | SN-DATA-01 Low-friction updates | TransactionImportService | TC-TXN-004 | Must |
| FR-TXN-005 | SN-DATA-01 Low-friction updates | TransactionImportService | TC-TXN-005 | Must |
| FR-TXN-006 | SN-DATA-01 Low-friction updates | TransactionImportService | TC-TXN-006 | Must |
| FR-TXN-007 | SN-DATA-01 Low-friction updates | TransactionImportService | TC-TXN-007 | Must |
| FR-TXN-008 | SN-DATA-01 Low-friction updates | TransactionImportService | TC-TXN-008 | Must |
| FR-PACE-001 | SN-PACE-01 Trustworthy weekly limit | PaceEngine | TC-PACE-001 | Must |
| FR-PACE-002 | SN-PACE-01 Trustworthy weekly limit | PaceEngine | TC-PACE-002 | Must |
| FR-PACE-003 | SN-PACE-01 Trustworthy weekly limit | PaceEngine | TC-PACE-003 | Must |
| FR-PACE-004 | SN-PACE-01 Trustworthy weekly limit | PaceEngine | TC-PACE-004 | Must |
| FR-PACE-005 | SN-PACE-01 Trustworthy weekly limit | PaceEngine | TC-PACE-005 | Must |
| FR-PACE-006 | SN-PACE-01 Trustworthy weekly limit | PaceEngine | TC-PACE-006 | Must |
| FR-PACE-007 | SN-PACE-01 Trustworthy weekly limit | PaceEngine | TC-PACE-007 | Must |
| FR-PACE-008 | SN-PACE-01 Trustworthy weekly limit | PaceEngine | TC-PACE-008 | Must |
| FR-PACE-009 | SN-PACE-01 Trustworthy weekly limit | PaceEngine | TC-PACE-009 | Must |
| FR-PACE-010 | SN-PACE-01 Trustworthy weekly limit | PaceEngine | TC-PACE-010 | Must |
| FR-UI-001 | SN-UX-01 Understand pace | DashboardUI | TC-UI-001 | Must |
| FR-UI-002 | SN-UX-01 Understand pace | DashboardUI | TC-UI-002 | Must |
| FR-UI-003 | SN-UX-01 Understand pace | DashboardUI | TC-UI-003 | Must |
| FR-UI-004 | SN-UX-01 Understand pace | DashboardUI | TC-UI-004 | Must |
| FR-UI-005 | SN-UX-01 Understand pace | DashboardUI | TC-UI-005 | Must |
| FR-UI-006 | SN-UX-01 Understand pace | DashboardUI | TC-UI-006 | Must |
| FR-AI-001 | SN-AI-01 Plain-language support | AISummaryAdapter | TC-AI-001 | Should |
| FR-AI-002 | SN-AI-01 Plain-language support | AISummaryAdapter | TC-AI-002 | Must |
| FR-AI-003 | SN-AI-01 Plain-language support | AISummaryAdapter | TC-AI-003 | Must |
| FR-AI-004 | SN-AI-01 Plain-language support | AISummaryAdapter | TC-AI-004 | Must |
| FR-AI-005 | SN-AI-01 Plain-language support | AISummaryAdapter | TC-AI-005 | Must |
| FR-AI-006 | SN-AI-01 Plain-language support | AISummaryAdapter | TC-AI-006 | Must |
| FR-AI-007 | SN-AI-01 Plain-language support | AISummaryAdapter | TC-AI-007 | Must |
| FR-DATA-001 | SN-PRI-01 User control | DataRightsService | TC-DATA-001 | Should |
| FR-DATA-002 | SN-PRI-01 User control | DataRightsService | TC-DATA-002 | Must |
| FR-DATA-003 | SN-PRI-01 User control | DataRightsService | TC-DATA-003 | Must |
| NFR-ACC-001 | SN-PACE-01 Trustworthy weekly limit | PaceEngine | Automated-golden-tests | Must |
| NFR-ACC-002 | SN-PACE-01 Trustworthy weekly limit | PaceEngine | Repeatability-test | Must |
| NFR-PERF-001 | SN-OPS-01 Responsive system | APIAndDeployment | Load-test-LT-01 | Must |
| NFR-PERF-002 | SN-OPS-01 Responsive system | APIAndDeployment | Browser-performance-test | Must |
| NFR-PERF-003 | SN-OPS-01 Responsive system | APIAndDeployment | Integration-timing-test | Must |
| NFR-SEC-001 | SN-SEC-02 Protect financial data | SecurityControls | Configuration-and-code-r | Must |
| NFR-SEC-002 | SN-SEC-02 Protect financial data | SecurityControls | Deployment-scan | Must |
| NFR-SEC-003 | SN-SEC-02 Protect financial data | SecurityControls | Security-test-ST-01 | Must |
| NFR-SEC-004 | SN-SEC-02 Protect financial data | SecurityControls | Session-test-ST-02 | Must |
| NFR-SEC-005 | SN-SEC-02 Protect financial data | SecurityControls | IDOR-test-ST-03 | Must |
| NFR-SEC-006 | SN-SEC-02 Protect financial data | SecurityControls | Code-review-and-injectio | Must |
| NFR-SEC-007 | SN-SEC-02 Protect financial data | SecurityControls | Secret-scan | Must |
| NFR-SEC-008 | SN-SEC-02 Protect financial data | SecurityControls | Upload-security-tests | Must |
| NFR-SEC-009 | SN-SEC-02 Protect financial data | SecurityControls | Dependency-scan | Must |
| NFR-PRI-001 | SN-PRI-01 Data minimization and control | PrivacyControls | Data-inventory-review | Must |
| NFR-PRI-002 | SN-PRI-01 Data minimization and control | PrivacyControls | Log-inspection | Must |
| NFR-PRI-003 | SN-PRI-01 Data minimization and control | PrivacyControls | Payload-inspection | Must |
| NFR-PRI-004 | SN-PRI-01 Data minimization and control | PrivacyControls | Deletion-audit-test | Must |
| NFR-REL-001 | SN-OPS-02 Reliable operation | ReliabilityControls | Transaction-rollback-tes | Must |
| NFR-REL-002 | SN-OPS-02 Reliable operation | ReliabilityControls | Uptime-monitor | Must |
| NFR-REL-003 | SN-OPS-02 Reliable operation | ReliabilityControls | Fault-injection-test | Must |
| NFR-USA-001 | SN-UX-01 Understand pace | UXFlow | Moderated-usability-test | Must |
| NFR-USA-002 | SN-UX-01 Understand pace | UXFlow | Comprehension-test | Must |
| NFR-A11Y-001 | SN-UX-02 Accessible interaction | AccessibleUI | Automated-and-manual-aud | Must |
| NFR-A11Y-002 | SN-UX-02 Accessible interaction | AccessibleUI | Keyboard-and-screen-read | Must |
| NFR-MNT-001 | SN-DEV-01 Maintainable delivery | RepositoryAndCI | CI-pipeline | Must |
| NFR-MNT-002 | SN-DEV-01 Maintainable delivery | RepositoryAndCI | Coverage-report | Must |
| NFR-MNT-003 | SN-DEV-01 Maintainable delivery | RepositoryAndCI | Pull-request-checklist | Must |
| NFR-AIQ-001 | SN-AI-02 Trustworthy explanations | AIValidationLayer | AI-evaluation-test | Must |
| NFR-AIQ-002 | SN-AI-02 Trustworthy explanations | AIValidationLayer | AI-safety-review | Must |
| NFR-AIQ-003 | SN-AI-02 Trustworthy explanations | AIValidationLayer | UI-test | Must |

# Appendix C — Glossary

| **Term** | **Definition** |
|----|----|
| Active goal | The single savings goal currently used by the pace engine. |
| Available cash | Liquid money available for spending or saving as of a user-entered date, excluding the amount already recorded as current goal savings. |
| Balance-as-of date | The date on which the user’s starting available-cash value is accurate. |
| Confirmed income | An income source the user expects with sufficient certainty; included in the forecast. |
| Current goal savings | Money already set aside toward the active goal and therefore not included in available cash. |
| Discretionary Capacity | Forecast Resources minus Goal Gap. |
| EARS | Easy Approach to Requirements Syntax, a structured natural-language method for writing requirements. |
| Forecast Resources | Current Cash plus confirmed future income, less planned future expenses and the reserve buffer. |
| Formula version | Identifier stored with each calculation snapshot to make financial behavior reproducible. |
| Goal Gap | Target amount minus current goal savings, never below zero. |
| Golden test scenario | A manually verified input/output example used as an authoritative automated calculation test. |
| LLM | Large Language Model used only for optional explanations in GoalWise. |
| MVP | Minimum Viable Product required for the course release. |
| Pace status | Completed, Off Pace, Ahead, At Risk, or On Track, calculated using Section 3.3. |
| Planned expense | A future obligation entered by the user and subtracted from forecast resources. |
| Projected Shortfall | Amount by which Goal Gap exceeds Forecast Resources. |
| Reserve buffer | User-confirmed cash amount withheld from safe-to-spend to reduce optimistic guidance. |
| Weekly plan snapshot | The opening allowance fixed for a Monday-through-Sunday local week. |
| Weekly Safe-to-Spend | Conservatively rounded discretionary capacity allocated across remaining weeks. |
