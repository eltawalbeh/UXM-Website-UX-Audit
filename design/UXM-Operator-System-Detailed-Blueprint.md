# UXM Operator System — Detailed Product Blueprint

**Product area:** Authenticated UXM Operator System
**Primary role:** UXM auditor / operator
**Design mode:** Operate — compact, task-first, evidence-led
**Status:** Detailed Stage 1 blueprint for visual approval

## 1. What the Operating System is

The Operator System is the internal working environment where UXM runs the complete audit operation. It is not a marketing dashboard and it is not the client report.

```text
Portfolio
→ Client
→ Project
→ Audit
→ Scope & pages
→ AI First Pass
→ Candidate review
→ Manual criteria review
→ Findings & evidence
→ Score & priorities
→ Delivery readiness
→ Publish / PDF / delivery history
```

The system always protects the same truth boundary:

```text
AI candidate ≠ approved finding
Unverified checkpoint ≠ failed checkpoint
Draft finding ≠ client-visible finding
Report preview ≠ published delivery
```

## 2. Permanent system shell

Every Operator page uses one stable shell so the auditor never loses context.

### 2.1 Primary rail

```text
UX Mosaic mark

Portfolio
Audits
Templates
Deliveries

Operator profile
```

The rail stays intentionally short. Clients and Projects are reached through Portfolio rather than becoming separate competing top-level modules.

### 2.2 Context header

```text
Breadcrumb / current record
Audit or project title + stable ID
Status
Official score state
Readiness state
Contextual actions
```

Examples of contextual actions:

- `New client` on Portfolio.
- `New project` inside Client Detail.
- `Create audit` inside Project Detail.
- `Run First Pass` inside Scope & First Pass.
- `Review report` after findings exist.
- `Publish delivery` only when readiness gates pass.

`Save` and `Discard` appear only while a page has unsaved changes.

### 2.3 Audit workspace sub-navigation

When an audit is open, the page gains one persistent audit-level navigation:

```text
Overview
Scope & Pages
First Pass
Criteria
Findings
Score & Priorities
Readiness
Delivery
```

Candidate Review and Finding Editor are focused work screens opened from those sections, not permanent top-level destinations.

### 2.4 Inspector pattern

Complex pages use an optional right-side inspector for the selected item:

- Desktop: persistent 340–420px inspector.
- Tablet: collapsible side sheet.
- Mobile: full-width sheet below the selected item.

The inspector never hides the evidence canvas on finding-related pages.

---

## 3. Complete Operator page map

| ID | Page | Parent | Primary job |
|---|---|---|---|
| O01 | Portfolio | Rail | Find the client/project/audit needing attention |
| O02 | Client Detail | Portfolio | Manage one client and its projects |
| O03 | Project Detail | Client | Manage one project and its audit history |
| O04 | Create Audit | Project | Create a clean scoped audit from template or URL |
| O05 | Templates | Rail | Browse and understand reusable audit templates |
| O06 | Audit Overview | Audit | Understand current state and next required action |
| O07 | Scope & First Pass | Audit | Confirm product type, bundle, pages, journeys and run AI discovery |
| O08 | Candidate Review | First Pass | Validate or reject one AI candidate |
| O09 | Criteria Review | Audit | Assess applicable UXM checkpoints systematically |
| O10 | Finding Editor + Evidence | Criteria / Findings | Produce a defensible approved finding |
| O11 | Findings Queue | Audit | Review completeness, duplicates and publication state |
| O12 | Score & Priority Review | Audit | Validate score, coverage and implementation priority |
| O13 | Delivery Readiness | Audit | Resolve every publication blocker |
| O14 | Delivery History | Rail / Audit | Track published versions, PDF and delivery record |

---

## 4. Portfolio and account hierarchy

## O01 — Portfolio

**Question answered:** Which client, project, or audit needs attention now?

### Desktop division

```text
┌ Stable rail ┬───────────────────────────────┬──────────────┐
│             │ Search + filters + New client│ Selection    │
│ Portfolio   ├───────────────────────────────┤ inspector    │
│ Audits      │ Client rows                   │              │
│ Templates   │  └ Project rows               │ Next action  │
│ Deliveries  │     └ Current audit/status    │ History      │
└─────────────┴───────────────────────────────┴──────────────┘
```

### Main content

- Search by client, project, domain, audit ID or owner.
- Filters: owner, project state, audit state, readiness, updated date.
- Hierarchical rows—not equal client cards.
- Client row: client identity, active project count, latest delivery.
- Project row: project title, audit count, current audit state, next action.
- Selection inspector: responsible operator, contact reference, recent activity, open project.

### Primary action

`New client`

### Empty state

Explains the hierarchy `Client → Project → Audit`; no fake accounts or metrics.

---

## O02 — Client Detail

**Question answered:** What work does UXM manage for this client?

### Layout

```text
Client identity + account status + New project
─────────────────────────────────────────────
Client context            | Contacts / notes
Projects and audit history| Recent deliveries
```

### Contents

- Client identity and internal account reference.
- Approved client display name and optional brand assets.
- Primary contact references—not public unless explicitly approved.
- Projects list with project state, audit count and latest delivery.
- Internal notes separated visually from client-visible data.
- Delivery history summary.

### Primary action

`New project`

### Safeguard

Deleting a client with projects is blocked; archive is the safe default.

---

## O03 — Project Detail

**Question answered:** What audits and deliveries belong to this project?

### Layout

```text
Project identity + linked client + Create audit
──────────────────────────────────────────────
Project context / default URL / product type
Audit history list
Delivery timeline
```

### Contents

- Client link and project identity.
- Default URL/product reference.
- Confirmed or suggested product type.
- Project status and owner.
- Audit history with template, scope, status, score state and version.
- Delivered report/PDF history.

### Primary action

`Create audit`

### Audit row actions

`Open audit` · `Duplicate as new audit` · `Archive`

Duplication copies scope configuration only; it never copies findings, evidence, AI output or delivery history.

---

## O04 — Create Audit

**Question answered:** What exactly are we auditing?

### Page model

A four-step setup flow; one step per screen region rather than one enormous form.

```text
1. Source       URL or project default
2. Product type Suggested type → human confirmation
3. Template     Government / Corporate / E-commerce / SaaS / Content
4. Scope        Bundle + pages + journeys + locale
```

### Final summary before create

- Client and project.
- Audit title and stable draft ID.
- Base URL.
- Product type.
- Template checkpoint count.
- Scope bundle and selected pages.
- Default report language.
- Explicit exclusions and not-verifiable flows.

### Primary action

`Create draft audit`

### Safeguards

- Product type suggestion is editable.
- Template and bundle are different concepts and never collapsed.
- A new audit begins `Not scored` with zero findings and zero evidence.

---

## O05 — Templates

**Question answered:** Which reusable UXM checklist foundation fits this project?

### Layout

```text
Template index                  Template detail
───────────────────────         ─────────────────
Government / Civic              Purpose
Corporate / Marketing   →       Included sections
E-commerce                      Checkpoint count
SaaS / Digital Product          Applicability notes
Content / Publisher             Create audit action
```

### Contents

- Version and last-updated metadata.
- Product-type fit.
- Included sections and official checkpoint count.
- What the template does not imply.
- `Create audit from template` action after project selection.

No fake usage metrics or “most popular” labels.

---

## 5. Audit workspace

## O06 — Audit Overview

**Question answered:** What should I do next, and what is blocked?

### Desktop division

```text
Audit context header
Audit sub-navigation
────────────────────────────────────────────────
Next-action queue (65%)     Official state (35%)
                            Scope coverage
                            Score state
                            Readiness blockers
```

### Next-action queue order

1. Confirm/complete scope.
2. Review First Pass candidates.
3. Resolve criteria requiring manual review.
4. Complete finding evidence.
5. Resolve not-verified checkpoints.
6. Review score and priorities.
7. Clear readiness blockers.
8. Publish delivery.

### Official state panel

- `Not scored` until one applicable criterion is assessed.
- Coverage: assessed / applicable.
- Approved finding count.
- Critical / High count.
- Not verified count.
- Readiness status and exact blockers.

No decorative chart appears before the queue.

---

## O07 — Scope & First Pass

**Question answered:** What will the system inspect, and what did the AI actually visit?

### Page division

```text
Scope configuration (left/top)
────────────────────────────────────────────
Product type → Template → Bundle
Pages / journeys / exclusions
Run First Pass
────────────────────────────────────────────
Run evidence and status (right/bottom)
Visited URLs · skipped URLs · provider state
Candidate count · unavailable/error detail
```

### Scope configuration

- Confirm product type.
- Show active template and checkpoint foundation.
- Choose commercial scope bundle:
  - Full website.
  - Selected pages.
  - General health check.
  - Contact experience.
- Add/remove same-origin pages.
- Define journeys and exclusions.
- Show selected checkpoint subset and out-of-scope count.

### Run states

`Ready` → `Running` → `Candidates ready` / `No candidates` / `AI unavailable` / `Provider error`

### Primary action

`Run AI First Pass`

### Safeguard

Starting a new run never deletes approved findings or changes the official score.

---

## O08 — Candidate Review

**Question answered:** Is this AI observation valid enough to become a human-reviewed draft?

### Three-pane layout

```text
Candidate queue  | Evidence/source canvas | Review inspector
280px            | Flexible 45–55%       | 360–420px
```

### Candidate queue

- Stable candidate ID `AIFP-###`.
- Checkpoint ID and page.
- Confidence label.
- Evidence-gap warning.
- Duplicate-risk warning.
- Review status.

### Evidence/source canvas

- Visited page URL and capture/source reference.
- Highlighted observed region when available.
- Checkpoint intent and applicability.
- Candidate observation beside—not over—the source.

### Review inspector

- Observation.
- Rationale.
- Proposed severity.
- Confidence.
- Evidence gaps.
- Duplicate risk.
- Human notes.

### Fixed decision bar

`Reject` · `Edit as draft` · `Promote for evidence review`

No action here changes score, readiness or report publication.

---

## O09 — Criteria Review

**Question answered:** Which UXM checkpoints were observed, and how were they assessed?

### Layout

```text
Section navigation | Criteria table / list       | Detail drawer
220px              | Flexible                    | 380px optional
```

### Filters

- Search.
- Section.
- Journey.
- Page/template.
- Status.
- Core / Conditional / Specialist.
- Linked finding / unlinked issue.

### Criterion row

```text
ID · checkpoint title · applicability · assessment · linked finding · note warning
```

Assessment controls:

`Pass` · `Partial` · `Issue` · `Not applicable` · `Not verified`

### Detail drawer

- Intent and source mapping.
- Applicable-when guidance.
- Assessment guidance.
- Internal notes.
- Linked findings.
- `Create finding` shortcut.

### Safeguards

- `Not applicable` and `Not verified` stay outside the score denominator.
- An `Issue` without a finding requires an internal note.
- Bulk actions operate only on an explicitly filtered set.

---

## O10 — Finding Editor + Evidence

**Question answered:** Can this finding be defended, understood and acted upon?

### Evidence-first layout

```text
Evidence canvas 60–65%       Finding inspector 35–40%
──────────────────────       ───────────────────────
Source screenshot            Page / journey / URL
Crop                         Checkpoint links
Annotation tools             Severity / effort
Pins / arrows / labels       Observation
Alt text                     Impact
Capture metadata             Recommendation
                              Publishability checks
```

### Evidence canvas

- Immutable source screenshot.
- Finding-specific crop.
- Rectangle, pin, arrow and label controls.
- Zoom and reset.
- Annotation color fixed to the UXM evidence standard.
- Alt description required for client-visible evidence.

### Structured inspector

1. What we observed.
2. Why it matters.
3. Recommended action.
4. Category and severity.
5. Checkpoint links.
6. Page, journey, URL and device.
7. Capture metadata.
8. Optional effort and confidence.

### Actions

`Save draft` · `Mark evidence complete` · `Return to findings`

### Publishability checklist

- Source URL exists.
- Page and journey exist.
- Observation, impact and recommendation are complete.
- Severity/category selected.
- Screenshot, crop, annotation and alt text exist.

---

## O11 — Findings Queue

**Question answered:** Which approved findings are ready, duplicated or incomplete?

### Layout

```text
Queue controls and filters
Critical / High priority lane
All findings table
Selection inspector / completeness detail
```

### Columns

- Stable `UXM-###` ID.
- Severity.
- Title.
- Page / journey.
- Linked checkpoints.
- Evidence state.
- Recommendation state.
- Client visibility.
- Publication status.

### Actions

`Open` · `Reprioritize` · `Merge duplicate` · `Exclude from report`

Exclusion requires an internal reason and never deletes the finding.

---

## O12 — Score & Priority Review

**Question answered:** Does the numerical result match the material UX risk and the implementation order?

### Layout

```text
Official score + coverage context
──────────────────────────────────────────
Section health                 Severity view
Priority roadmap
Fix now | Fix next | Enhance later
Warnings and unresolved coverage
```

### Rules

- Score is calculated only from applicable assessed checkpoints.
- Critical/High findings remain visible regardless of score.
- `Not verified` appears as a coverage limitation, never as a failure.
- Every roadmap item links back to a finding and evidence.

### Primary action

`Continue to readiness`

---

## O13 — Delivery Readiness

**Question answered:** What exactly prevents this audit from reaching the client?

### Gate groups

1. Audit identity.
2. Scope and exclusions.
3. Assessment coverage.
4. Findings completeness.
5. Evidence completeness.
6. Score transparency.
7. English report readiness.
8. Arabic RTL readiness when selected.
9. PDF generation readiness.

### Layout

```text
Readiness decision
Blocked / Ready for client
──────────────────────────────────────────
Gate checklist                 Selected blocker detail
Each failed gate links         Exact missing fields
back to its repair page        Repair action
```

### Actions

When blocked: `Resolve blocker`
When ready: `Review report` · `Publish client report`

The system never offers an enabled Publish action while any mandatory gate fails.

---

## O14 — Delivery History

**Question answered:** What was delivered, when, in which language and version?

### Contents

- Delivery version.
- Audit and project link.
- English / Arabic locale.
- Published timestamp.
- Operator.
- Official score state at publication.
- Report URL state.
- PDF filename and generation state.
- Delivery note.

### Actions

`Open report` · `Download PDF` · `Create new version`

A new version starts from the current approved audit record; historical deliveries stay immutable.

---

## 6. System-wide states

Every page must visibly support the states relevant to its job:

```text
Loading
Empty
No search results
Validation error
Network/API error
Permission denied
AI unavailable
Not scored
Not verified
Evidence pending
Readiness blocked
Ready for client
Delivered
Archived
```

Errors preserve operator work. Blocked actions explain the exact missing requirement and provide a direct repair path.

## 7. Responsive behavior

### Desktop ≥1200px

- Full 238px rail.
- Context header.
- Main canvas.
- Optional inspector.

### Tablet 768–1199px

- Compact rail using supplied vertical logo.
- Inspector becomes collapsible side sheet.
- Audit sub-navigation may scroll inside its own region, never at page level.

### Mobile <768px

- Top app bar + navigation drawer.
- Context summary directly beneath app bar.
- Audit sub-navigation becomes a labelled selector.
- Evidence comes before prose.
- Tables become structured list rows; essential IDs/statuses remain visible.
- No horizontal page scrolling at 390px.

## 8. Arabic RTL behavior

- Rail moves to the right.
- Navigation and workflow language is fully translated.
- Evidence images and supplied logos are never mirrored.
- IDs, URLs, file names and technical metadata use isolated LTR runs.
- Candidate Review order becomes inspector → evidence → queue only when it improves reading flow; evidence remains visually central.
- Finding Editor remains evidence-first.

## 9. What the client never sees

```text
AI candidates
Rejected candidates
Internal notes
Draft findings
Excluded findings
Unverified working details
Provider errors
Operator names unless explicitly included in delivery metadata
Readiness repair controls
```

The Client Portal receives only assigned published deliveries. The Client Report receives only the approved client-facing audit version.

## 10. Production implementation order

```text
1. Shared Operator shell and role guard
2. Portfolio → Client → Project
3. Create Audit + Templates
4. Audit Overview + Scope & Pages
5. First Pass + Candidate Review
6. Criteria Review
7. Finding Editor + Evidence
8. Findings Queue
9. Score & Priorities
10. Readiness + Report preview
11. Delivery History
12. Responsive + complete Arabic RTL
```

This order preserves a vertical working path instead of producing fourteen disconnected screens.