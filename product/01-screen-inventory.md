# UXM Audit — Phase 1 Screen Inventory

## Product boundary

There are two intentional experiences powered by one audit record:

- **Internal Audit Workspace:** a working environment for UXM auditors.
- **Client Report:** a read-only decision document for client stakeholders.

The client report never asks for information that has not been entered or calculated in the internal workspace.

## Roles

| Role | Primary need | Permissions in phase 1 |
|---|---|---|
| UXM Auditor | Conduct, document, score, and publish an audit efficiently | Create and edit all audit data; generate outputs |
| Client Stakeholder | Understand priorities, evidence, impact, and next actions | Read-only report access; export PDF |

## Shared data contract

Every screen reads/writes one `Audit` record comprising: client and website metadata, scope, criterion assessments, findings, evidence, scores, and publication metadata.

## Internal Audit Workspace screens

### I01 — Audit Library

**User:** UXM Auditor  
**Purpose:** Find an existing audit or begin a new one.

**Primary action:** `Create audit`

**Contents:**
- Audit list: client, website, status, owner, updated date, overall score when available
- Status filters: Draft, In review, Published
- Search by client, URL, or audit ID
- Empty state explaining how to start an audit

**Output:** Opens I02 for a new audit or I03 for an existing audit.

**States:** loading, empty, no search results, audit unavailable.

---

### I02 — Create Audit / Define Scope

**User:** UXM Auditor  
**Purpose:** Establish exactly what this audit represents before scoring begins.

**Primary action:** `Create draft audit`

**Required inputs:**
- Client name
- Website or product name
- Base URL
- Audit language default: English or Arabic
- Audit date
- Auditor name

**Scope inputs:**
- Business/site type
- Target market and user context
- Primary journeys to inspect
- Pages / templates in scope
- Devices, browser versions, and resolutions
- Explicit exclusions and unverified areas

**Output:** Creates an audit record and opens I03.

**Rules:** Base URL must be valid; the user may save a clearly labelled draft only after core identity fields exist.

---

### I03 — Audit Overview

**User:** UXM Auditor  
**Purpose:** Act as the audit command center and show progress without becoming a dashboard cemetery.

**Primary actions:** `Review criteria`, `Add finding`, `Review report`

**Contents:**
- Client / website / scope summary
- Audit status and completion progress
- Critical and High finding count
- Applicable criteria completion percentage
- Section health list
- Recent findings queue
- Persistent action bar

**Output:** Navigates to I04, I06, I07, or I08.

**States:** new audit with zero assessments; partial audit; ready for review.

---

### I04 — Criteria Library

**User:** UXM Auditor  
**Purpose:** Select applicable checks and assess the site systematically.

**Primary action:** set `Pass`, `Partial`, `Issue`, `Not applicable`, or `Not verified`.

**Contents:**
- Section navigation with assessed/applicable counts
- Search
- Filters: section, journey, site type, category, status, core/conditional/specialist
- Criterion row: plain-language title, intent, applicability rule, status, linked findings
- Bulk applicability control only within a clearly filtered set

**Output:** Updates the audit score inputs and links to I05/I06.

**Rules:** A criterion marked Issue should prompt—but not force—the auditor to create or link a finding. An Issue without a finding requires an internal note.

---

### I05 — Criterion Detail Drawer

**User:** UXM Auditor  
**Purpose:** Supply concise guidance while reviewing an individual criterion.

**Primary action:** save assessment and notes.

**Contents:**
- Criterion ID, title, intent, category, journey, and source mapping
- Applicable-when guidance
- Assessment guide: what Pass, Partial, and Issue mean
- Notes field
- Linked finding IDs
- Create finding shortcut

**Output:** Returns to I04 with the assessment saved.

---

### I06 — Finding Editor

**User:** UXM Auditor  
**Purpose:** Turn evidence into a defensible client-facing recommendation.

**Primary action:** `Save finding`

**Required inputs:**
- Page / journey and URL
- Category
- Severity
- What we observed
- Why it matters
- Recommendation
- At least one evidence item for published findings

**Evidence tools:**
- Upload or attach screenshot
- Add annotation rectangle, pin, arrow, and label
- Write alt text
- Link relevant criterion IDs

**Optional inputs:** effort, confidence, capture date/time, responsive/device context.

**Output:** Creates or updates stable issue ID `UXM-###`, updates priority roadmap and report data.

**Validation:** Critical/High findings need a recommendation and evidence; URL may be inherited from the audit base URL but must be editable.

---

### I07 — Findings Queue

**User:** UXM Auditor  
**Purpose:** Review quality, completeness, duplicates, and priority before publishing.

**Primary actions:** `Edit`, `Reprioritize`, `Merge duplicate`, `Open report preview`

**Contents:**
- Sortable findings list by severity, category, journey, section, status, and issue ID
- Evidence-present and recommendation-present indicators
- Completeness warnings
- Critical/High lane at the top

**Output:** Opens I06 or I08.

---

### I08 — Scorecard & Priority Review

**User:** UXM Auditor  
**Purpose:** Validate the numerical score against material business risks.

**Primary actions:** `Review report preview`, `Mark ready to publish`

**Contents:**
- Overall score and methodology note
- Section scores based only on applicable assessed criteria
- Severity distribution
- Fix now / Fix next / Enhance later roadmap
- Not applicable and not verified counts
- Warnings for unassessed applicable criteria or incomplete findings

**Output:** Opens I09.

**Rules:** Critical/High items remain visible regardless of the overall score.

---

### I09 — Publish / Export Readiness

**User:** UXM Auditor  
**Purpose:** Prevent incomplete or misleading reports from reaching a client.

**Primary actions:** `Publish client report`, `Export PDF`

**Contents:**
- Report language selector: English / Arabic
- Audit metadata check
- Completion checklist
- Open issues and missing evidence warnings
- Public/share URL state for the prototype

**Output:** Opens C01 in the selected language and generates the PDF output.

**Blocking rules:** Published report requires scope, at least one assessed applicable criterion, and all published findings to have category, severity, observation, impact, recommendation, and evidence.

## Client Report screens

### C01 — Cover

**User:** Client Stakeholder  
**Purpose:** Establish report identity and confidence.

**Contents:** UXM mark, client identity, Website UX Audit, audited URL/product, report version, audit date, language, refined visual crop or restrained device image.

**Primary action:** `View executive snapshot`

---

### C02 — Executive Snapshot

**User:** Client Stakeholder  
**Purpose:** Explain the business conclusion in under two minutes.

**Contents:** overall score, plain-language assessment, top three strengths, top three actions, severity totals, scope summary.

**Primary action:** `View priority roadmap`

---

### C03 — Scope & Methodology

**User:** Client Stakeholder  
**Purpose:** Make the report defensible and expectations clear.

**Contents:** tested journeys/pages/devices, exclusions, audit dates, assessment logic, and limitations.

---

### C04 — Severity & Category Legend

**User:** Client Stakeholder  
**Purpose:** Define the language used throughout the report.

**Contents:** four severity levels, category labels, and score interpretation.

---

### C05 — Scorecard

**User:** Client Stakeholder  
**Purpose:** Reveal patterns without hiding individual risks.

**Contents:** overall score, section scores, severity distribution, coverage and N/A notes.

**Primary action:** `View roadmap` or select a section.

---

### C06 — Priority Roadmap

**User:** Client Stakeholder  
**Purpose:** Turn findings into an ordered implementation discussion.

**Contents:** Fix now, Fix next, Enhance later; each item shows issue ID, title, page/journey, expected impact, and a link to evidence.

**Primary action:** `Open finding`

---

### C07 — Section Divider / Section Summary

**User:** Client Stakeholder  
**Purpose:** Provide a readable transition into related findings.

**Contents:** section score, short interpretation, key strength, key risk, finding count.

---

### C08 — Finding Detail

**User:** Client Stakeholder  
**Purpose:** Provide proof and a practical resolution for one issue.

**Contents:**
- Stable issue ID
- Severity and category labels
- Page, journey, and URL
- Annotated screenshot with textual alt description
- What we observed
- Why it matters
- Recommendation
- Optional effort/confidence
- Device and capture metadata

**Primary action:** previous / next finding; return to roadmap.

---

### C09 — Conclusion & Validation Next Steps

**User:** Client Stakeholder  
**Purpose:** Close the audit with a path to measurable improvement.

**Contents:** issue distribution, recurring patterns, recommended validation/KPI actions after implementation, suggested next engagement.

---

### C10 — Closing

**User:** Client Stakeholder  
**Purpose:** Professional end page for the PDF and web flow.

**Contents:** UXM contact/brand treatment and concise closing line.

## Internationalization rules

- C01–C10 have an English LTR and Arabic RTL presentation using the same audit data.
- In Arabic, titles, body copy, metadata rail, roadmap order, and navigation direction are RTL.
- Issue IDs, URLs, browser versions, file names, and technical numeric values remain isolated LTR tokens.
- Screenshots are not mirrored.
- English placeholder labels are prohibited in Arabic output.

## Phase-1 screen count

- Internal workspace: 9 screens + one criterion detail drawer
- Client report: 10 screens
- Shared components: created later from the UI patterns above
