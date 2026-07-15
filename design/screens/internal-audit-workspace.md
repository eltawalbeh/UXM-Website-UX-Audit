# UXM Audit — Internal Audit Workspace

## Purpose

This is the operational workspace used by UXM auditors to run a website audit from scope definition through report readiness. It is intentionally denser than the client report, but it follows the same evidence-first system: every assessment should lead to defensible evidence, and every material issue should become a clear finding.

## Design read

**Professional workbench, not an admin dashboard.** The auditor needs quick orientation, an efficient review loop, and confidence that the published report will be complete. Use an editorial shell with a disciplined data workspace inside it—no decorative KPI cards, no hidden status meanings, and no competing primary actions.

## Desktop shell

```text
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ UXM Audit  /  Acme Website Audit          Draft • Updated now      Preview  Publish │
├──────────────┬───────────────────────────────────────────────────────────────────────┤
│ AUDIT        │  Page title + concise status / scope context                           │
│ Overview     │                                                                       │
│ Criteria     │  Primary work area                                                     │
│ Findings     │                                                                       │
│ Scorecard    │                                                                       │
│              │                                                                       │
│ ──────────── │                                                                       │
│ 67% assessed │                                                                       │
│ 12 findings  │                                                                       │
│ 3 High       │                                                                       │
└──────────────┴───────────────────────────────────────────────────────────────────────┘
```

### Shell rules

- **Top bar:** logo/wordmark, audit breadcrumb, audit status, save state, report preview, publish action.
- **Left rail:** fixed at 240px on desktop. It contains audit navigation, not a generic product menu.
- **Main content:** max-width 1440px; canvas background uses `Canvas`, working surfaces use `Surface`.
- **Context panel:** opens only when needed for criterion guidance, filters, or audit settings; do not permanently consume workspace width.
- **Audit health strip:** compact and truthful. It shows assessed applicable criteria, total findings, and Critical/High count. It must not pretend an audit is “healthy” while unresolved high-severity findings exist.

## Navigation model

| Navigation item | Purpose | Primary output |
|---|---|---|
| Overview | Audit command center | Continue the most relevant next action |
| Criteria | Assess applicability and checkpoints | Updated score inputs; linked findings |
| Findings | Review the evidence-backed issue queue | Complete, deduplicated findings |
| Scorecard | Validate score, coverage, and roadmap | Audit ready for report review |
| Settings | Scope, team, audit metadata, export locale | Accurate report context |

## I03 — Audit Overview

### Job

Give the auditor a single calm place to understand audit state and choose what to do next.

### Layout

```text
[Audit title]                                             [Edit scope]
client / website URL / audit date / device scope

[Continue audit — Primary action]      [Add finding]

Progress                     Priority now                Recent findings
67% of applicable            3 High • 0 Critical         UXM-012  High  Navigation...
checks assessed              [Review findings]           UXM-011  Medium Content...

Section health
Home                 80%  ████████░░
Navigation & IA      56%  █████░░░░░
Forms                0%   Not started

Scope note: Desktop Chrome 1280px + Mobile Safari 390px • 6 pages • 3 journeys
```

### Components

- Audit title and metadata row
- One primary `Continue audit` action, resolved from the next incomplete meaningful step
- Secondary `Add finding` action
- Progress module with a real assessed/applicable denominator
- Priority module showing only Critical and High severity counts
- Section-health list with numeric score or `Not started`—never an empty visual bar
- Recent finding list with ID, severity, category, title, and completeness state

### States

| State | What changes |
|---|---|
| New audit | Explain scope is the first task; scorecards remain absent, not zero |
| Active audit | Continue action opens the most recently incomplete criteria section |
| In review | Primary action becomes `Review scorecard` |
| Report-ready | Primary action becomes `Preview report`; publish remains deliberate secondary confirmation |

## I04 — Criteria Library

### Job

Let auditors work through applicable checks with context, speed, and traceability.

### Layout

```text
Criteria                                      [Search criteria] [Filters]
Navigation & Information Architecture          17 / 29 applicable assessed

[All 29] [Core 12] [Conditional 10] [Specialist 7]

┌─────┬──────────────────────────────────────────────┬─────────────┬────────────┬──────┐
│ ID  │ Checkpoint                                   │ Applicability│ Assessment │ Link │
├─────┼──────────────────────────────────────────────┼─────────────┼────────────┼──────┤
│ N01 │ Users can navigate to likely destinations... │ Applicable  │ Pass       │ —    │
│ N02 │ Navigation labels match user trigger words   │ Applicable  │ Issue      │ +    │
│ N03 │ Site map exists where needed                 │ N/A         │ —          │ —    │
└─────┴──────────────────────────────────────────────┴─────────────┴────────────┴──────┘
```

### Interaction rules

- Default section order follows the UXM audit library. Within a section, core checks precede conditional and specialist checks.
- The left section list shows: section name, applicable-assessed count, and material issue count.
- A criterion row uses a compact split control for applicability and a visible status selector. Do not hide the current assessment in a menu only.
- Selecting a row opens the Criterion Detail Drawer; selecting the `+` finding affordance begins a linked finding.
- Filters are explicit: section, journey, category, assessment status, applicability, type, and linked-finding state.
- Search matches titles, intent, and audit guidance.
- Bulk actions are limited to setting applicability for the filtered list. Never bulk-set Pass.

### Assessment controls

```text
Applicability:  [Applicable ▾]  [Not applicable]  [Not verified]
Assessment:     [Pass] [Partial] [Issue]
```

- Pass / Partial / Issue use written labels and simple icons; color reinforces only.
- `Issue` opens a lightweight prompt: `Create finding`, `Link existing`, or `Keep as internal note`.
- An `Issue` with no finding displays an amber internal-note requirement, never a false-green completed state.

### Empty and error states

- **No scope set:** show a scope reminder with `Edit scope`, not an empty table.
- **No filters match:** preserve filters, show clear reset action.
- **Section not started:** show the applicable count and a `Start section` action.
- **Not verified:** require a short reason, e.g. access not provided / test account unavailable.

## I05 — Criterion Detail Drawer

### Job

Give audit guidance without forcing the auditor to leave their current review flow.

### Desktop position

Right-side overlay, 440px wide; table remains visible behind it.

### Contents

1. Checkpoint ID and full title
2. Category, journey, core/conditional/specialist tags
3. `Why it matters` / audit intent
4. `Applicable when` rule
5. Pass, Partial, and Issue guidance
6. Source mapping to the original spreadsheet where relevant
7. Assessment and applicability controls
8. Auditor notes
9. Linked findings list and `Create linked finding`

### Rules

- The drawer is dismissible only after changes are saved or discarded explicitly.
- The original sheet's wording is shown as traceability metadata, not as the primary client-facing text.
- A linked finding opens in the editor in a new focused state; the criterion context is preserved.

## I07 — Findings Queue

### Job

Review issue quality and client-report readiness before numbers distract from evidence.

### Layout

```text
Findings                                      [Search] [Filter] [Add finding]
[All 12] [Critical 0] [High 3] [Medium 6] [Low 3] [Needs attention 2]

Fix now
UXM-012  High  Navigation & IA       Home / Discover        Evidence ✓  Recommendation ✓
UXM-009  High  Forms & Data Entry    Apply / Complete       Evidence ✓  Recommendation !

Fix next
UXM-011  Medium Content & Microcopy  Services / Understand  Evidence ✓  Recommendation ✓
```

### Components

- Severity lanes ordered Critical → High → Medium → Low, with `Opportunity` shown separately after issue severity lanes.
- Finding row: ID, severity chip, category, title, page/journey, evidence status, recommendation status, updated date.
- `Needs attention` filter includes missing evidence, missing recommendation, duplicate warning, and untranslated client copy.
- A row click opens the Finding Editor, not a read-only modal.
- Drag sorting is prohibited; priority follows severity, then auditor review date. This avoids accidental reordering that changes audit meaning.

### States

- **No findings:** show `Assess criteria` and `Add finding` options; never imply a clean audit solely because none have been written.
- **Report blockers:** fixed non-alarmist banner with count and direct links to incomplete items.
- **Duplicate candidate:** discreet comparison panel; auditor can merge or retain separately with a reason.

## I08 — Scorecard & Priority Review

### Job

Explain score coverage, expose risk, and assemble the implementation conversation before publication.

### Layout

```text
UX Health Score  72 / 100   Needs targeted improvement
38 of 44 applicable core checks assessed • 4 not verified

[Critical 0] [High 3] [Medium 6] [Low 3]

Section scores                              Priority roadmap
Navigation & IA          56%                Fix now
Task Orientation         74%                UXM-012  Improve navigation contrast...
Content                  81%                UXM-009  Clarify required form fields...

Coverage & limits
- Search was not applicable
- Account recovery was not verified: no test user
```

### Rules

- Overall score appears with a short assessment label and coverage statement.
- Critical/High totals sit immediately beside the score and cannot be hidden by charts.
- Section score rows show percentage, count of assessed/applicable criteria, and a direct link to the relevant section.
- Roadmap is derived from findings and shown in `Fix now`, `Fix next`, `Enhance later` groups.
- Audit scope limitations are always visible on this page and exported into the client report.
- If coverage is incomplete, score is visually qualified with `Provisional` rather than presented as a definitive grade.

## I09 — Publish / Export Readiness

### Job

Make publication a controlled quality gate rather than a button at the end of a form.

### Layout

```text
Report readiness                                      [Preview English] [Preview Arabic]

✓ Audit identity and scope
✓ 44 applicable checks assessed
! 2 findings need a recommendation
✓ Evidence attached to 12 findings
! Arabic translation incomplete for 1 finding

[Save as in review]                                  [Publish report]
```

### Rules

- Every row explains the state and links to the exact corrective action.
- Preview is available at any time with a clearly visible `Draft` watermark.
- `Publish report` is disabled only for blocking gaps; non-blocking warnings stay visible.
- Selecting Arabic invokes RTL and translation validation; report fields must not silently fall back to English.

## Mobile behavior

- Navigation rail collapses to a labelled drawer; no icon-only mystery navigation.
- Criteria table becomes stacked review cards with title, applicability, assessment, and linked finding count; filters remain accessible.
- Finding queue maintains severity lane order and uses a one-column list.
- The annotation canvas is usable at narrow sizes with zoom/pan controls; desktop is preferred for precise multi-region annotation.
- Publish and save actions remain fixed at the bottom only while an edit form is open; otherwise they stay in the top action bar.

## Workspace accessibility requirements

- All assessment controls are keyboard reachable with visible focus.
- Status updates announce through an ARIA live region in the implementation.
- Table rows have proper labels and do not rely on color to expose Issue/Pass state.
- Shortcut tooltips never contain essential-only information.
- Dense desktop controls retain clear target boundaries and 32px minimum row actions; touch controls use 44px targets.
