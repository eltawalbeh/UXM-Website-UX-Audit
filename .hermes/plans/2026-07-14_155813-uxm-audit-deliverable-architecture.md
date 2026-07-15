# UXM Audit Deliverable Architecture — Implementation Plan

> **For Hermes:** Use the UXM Audit Blueprint and implement this plan task-by-task; preserve one source of truth for audit data and generate both client deliverables from it.

**Goal:** Define and validate the actual UXM product deliverable: an internal audit workspace that produces a shareable bilingual web report and a premium PDF report from the same audit data.

**Architecture:** The product has three layers. (1) An internal workspace captures scope, applicable criteria, observations, evidence, severity, and recommendations. (2) A normalized audit data model calculates scores and priority roadmaps. (3) report renderers produce an English LTR or Arabic RTL interactive web report and export-quality PDF without duplicate content entry.

**Tech Stack:** To be selected after the UXM visual system and a clickable prototype are approved. The initial prototype must remain local, self-contained, and launchable on Windows. No backend, account system, or external database is needed in phase 1.

**Source references:**
- `UXM-UX-Audit-Blueprint.md`
- `ExpertReviewCheckpoints.xls`
- `Monshaat UX Expert Review.pdf`
- `Monshaat UX Expert Review AR.pdf`

---

## Product decision — locked default

Build **one UXM Audit application** with two output modes:

1. **Internal Audit Workspace** — used by UXM to conduct, score, manage, and review an audit.
2. **Client Report** — a read-only, shareable report view with PDF export.

The client report must not be manually recreated in PowerPoint, Figma, or a PDF editor. Both views consume the same audit record and findings.

## Non-goals for phase 1

- Multi-user authentication, permissions, billing, client portal accounts, or cloud sync.
- A generic project-management product.
- A rigid requirement to answer every one of the source spreadsheet's 247 questions.
- Automated AI-generated audit conclusions without auditor review.

---

## Deliverable flow

```text
Create audit
  → define client, URL, market, language, device scope, journeys
  → select applicable UXM criteria
  → record checkpoint status and evidence
  → create material findings with annotated screenshots
  → assign category, severity, impact, and recommendation
  → review scorecard and priority roadmap
  → publish client web report / export PDF
```

---

## Canonical audit data model

All interfaces use the same entities. Do not create report-only fields that the internal workspace cannot edit.

### Audit

```json
{
  "id": "audit_2026_001",
  "client": {"name": "Client name", "logo": null},
  "website": {"name": "Website name", "url": "https://example.com"},
  "locale": "en",
  "status": "draft",
  "auditDate": "2026-07-14",
  "reportVersion": "1.0",
  "scope": {
    "journeys": ["Discover", "Understand", "Decide", "Complete"],
    "pages": [],
    "devices": [],
    "browsers": [],
    "exclusions": []
  },
  "auditTeam": [],
  "sectionWeights": {},
  "criteria": [],
  "findings": []
}
```

### Criterion assessment

```json
{
  "criterionId": "nav-01",
  "section": "Navigation & Information Architecture",
  "status": "pass",
  "applicability": "applicable",
  "notes": "",
  "linkedFindingIds": []
}
```

Allowed values:
- `applicability`: `applicable | not_applicable | not_verified`
- `status`: `pass | partial | issue`

### Finding

```json
{
  "id": "UXM-001",
  "number": 1,
  "title": "Primary navigation lacks sufficient contrast",
  "pageName": "Home",
  "journey": "Discover",
  "url": "https://example.com/",
  "category": "interface_visual_design",
  "severity": "high",
  "observed": "Navigation labels do not meet readable contrast against the header background.",
  "whyItMatters": "Visitors may overlook core destinations and abandon exploration.",
  "recommendation": "Increase contrast and confirm the header states meet WCAG AA.",
  "evidence": [],
  "criterionIds": ["nav-01"],
  "effort": "medium",
  "confidence": "high",
  "capturedAt": "2026-07-14T15:00:00+03:00"
}
```

### Evidence item

```json
{
  "id": "evidence_001",
  "image": "assets/evidence/UXM-001.png",
  "alt": "Home page header with the low-contrast navigation labels outlined in red.",
  "annotations": [
    {"type": "rect", "x": 0.1, "y": 0.2, "width": 0.4, "height": 0.1, "label": "1"}
  ]
}
```

---

## Report scoring and priority rules

### Score

- Pass = 1 point
- Partial = 0.5 point
- Issue = 0 points
- Not applicable and not verified are excluded from a denominator.
- `section score = achieved points / applicable assessed criteria × 100`
- Overall score is a weighted average of only the applicable sections.

### Priority

- Critical and High findings always appear in **Fix now**, independently of overall score.
- Medium findings appear in **Fix next**.
- Low findings and approved opportunities appear in **Enhance later**.
- If a criterion is `issue` but creates no material client-facing finding, it must retain an internal note explaining why.

---

# Implementation tasks

## Task 1: Establish application and report boundaries

**Objective:** Turn the product decision into a screen inventory and prevent scope drift.

**Files:**
- Create: `product/01-screen-inventory.md`
- Create: `product/02-user-flows.md`

**Steps:**
1. Define the two roles: UXM auditor and client stakeholder.
2. List every phase-1 screen, its user, main action, inputs, outputs, and empty/error state.
3. Map the flow from audit creation to published report.
4. Mark which operations must be possible in Arabic and which must remain language-neutral (URLs, evidence file names, IDs).

**Acceptance criteria:** No screen exists without a stated purpose or data source; every finding entered by an auditor appears in the client report without re-entry.

---

## Task 2: Define the UXM visual system before UI screens

**Objective:** Establish the design tokens and component language that makes this unmistakably UXM while retaining the report's evidence-first editorial feel.

**Files:**
- Create: `design/UXM-Audit-DESIGN.md`
- Create: `design/assets/README.md`

**Steps:**
1. Confirm UXM logo assets and brand tokens; use documented placeholders only until assets are available.
2. Define semantic colors for surfaces, text, borders, severity, category, and annotations.
3. Define English and Arabic font pairs, type scale, spacing, radius, icon rules, and responsive breakpoints.
4. Define reusable components: severity chip, category chip, issue ID, score ring, score bar, evidence frame, annotation marker, recommendation panel, metadata row, roadmap item.
5. Add accessibility rules: AA contrast, color-plus-text severity encoding, keyboard behavior, image alt text, and direction-aware layouts.

**Acceptance criteria:** A designer/developer can build every report screen using the tokens and components without inventing visual behavior per screen.

---

## Task 3: Design the Internal Audit Workspace flow

**Objective:** Create the operational UI that lets UXM conduct a real audit efficiently.

**Files:**
- Create: `design/screens/internal-audit-workspace.md`
- Create: `design/screens/audit-finding-editor.md`

**Screens:**
1. Audit list / dashboard
2. Create audit and scope definition
3. Scope and journey matrix
4. Criteria library with section, applicability, and status filters
5. Criterion review drawer
6. Finding editor with annotation canvas
7. Findings queue with severity and category filters
8. Scorecard / priority review
9. Publish / export readiness screen

**Rules:**
- The workspace is dense enough for professionals, but never dashboard clutter.
- An auditor can create a finding in no more than one primary flow: choose criterion → add evidence → state observation/impact/recommendation → assign severity.
- IDs are stable and assigned automatically.
- Use actual field labels, not placeholder copy.

**Acceptance criteria:** An auditor can complete one finding with screenshot, category, severity, and recommendation, then see it affect the score and roadmap.

---

## Task 4: Design the Client Report flow

**Objective:** Design a premium, decision-ready client report that follows the reference report's strongest principles without copying its brand.

**Files:**
- Create: `design/screens/client-report-en.md`
- Create: `design/screens/client-report-ar.md`

**English screens:**
1. Cover
2. Executive snapshot
3. Scope and methodology
4. Severity/category legend
5. Scorecard
6. Priority roadmap
7. Section divider
8. Finding detail
9. Conclusion and validation next steps
10. Closing

**Arabic screens:** The same information architecture in intentional RTL—not a mechanical mirror. Maintain isolated LTR rendering for URLs, issue IDs, browser versions, and numeric technical data.

**Acceptance criteria:** A stakeholder can understand the top business risks in under two minutes and open any detailed finding for proof and recommended action.

---

## Task 5: Convert the source criteria to a UXM checkpoint library

**Objective:** Transform the 247-row historical checklist into an applicable, modern audit library.

**Files:**
- Create: `data/uxm-checkpoints.v1.json`
- Create: `data/uxm-checkpoints.v1.md`
- Test: `tests/checkpoint-library.test.*` (technology chosen in build phase)

**Steps:**
1. Preserve all original criteria in a traceable source mapping.
2. Merge duplicates and rewrite outdated wording in UXM language.
3. Add tags for site type, journey, surface, category, and applicability condition.
4. Add modern criteria for responsive/mobile behavior, accessibility, performance feedback, consent/privacy, and contemporary conversion patterns.
5. Mark criteria as `core`, `conditional`, or `specialist`.
6. Validate every criterion has: ID, title, intent, category, section, applicableWhen, assessment guidance, and source mapping.

**Acceptance criteria:** An auditor can filter the library to a website type and see a focused, defensible set of checks rather than all 247 indiscriminately.

---

## Task 6: Build a local clickable prototype

**Objective:** Validate the product workflow before adding persistence or report-export complexity.

**Files (exact stack will be chosen after Tasks 1–4):**
- Create: `app/…`
- Create: `tests/…`
- Create: `START-UXM-AUDIT.bat`

**Required prototype behaviors:**
1. Open a seeded audit.
2. Change a criterion from Pass to Issue.
3. Create and edit a finding.
4. Change severity and observe the roadmap and scores update.
5. Toggle English / Arabic and verify RTL presentation.
6. Open the read-only client report from the same seeded data.

**Verification:** Run local smoke tests, then exercise the complete flow in a browser at localhost on desktop and a narrow mobile viewport.

---

## Task 7: Run a real pilot audit and calibrate

**Objective:** Prove the system works on a real website before productizing it.

**Files:**
- Create: `pilots/<client-slug>/audit.json`
- Create: `pilots/<client-slug>/evidence/…`
- Create: `pilots/<client-slug>/pilot-retrospective.md`

**Steps:**
1. Select one real website and define scope.
2. Conduct an audit using the workspace.
3. Review false positives, irrelevant criteria, awkward data-entry steps, scoring anomalies, and report readability.
4. Apply only demonstrated changes to the checkpoint library and prototype.
5. Produce English and Arabic report outputs for review.

**Acceptance criteria:** The report is client-ready, every finding has evidence, and UXM can repeat the process for a second site with no structural rework.

---

## Validation checklist

- [ ] Same audit data powers workspace, English report, Arabic report, and PDF export.
- [ ] No all-sites-must-answer-247 requirement.
- [ ] Each reported issue has evidence, impact, and direct recommendation.
- [ ] Critical/High issues cannot be buried by aggregate scores.
- [ ] Arabic layout is genuinely RTL with protected LTR technical tokens.
- [ ] Severity is understandable without color.
- [ ] Audit can be completed and reviewed on Windows through a self-contained local project folder.
- [ ] A pilot audit proves the full journey before any client use.

## Risks and mitigations

| Risk | Mitigation |
|---|---|
| Old source criteria are not universally relevant | Applicability rules, site-type tags, and N/A exclusion from scoring |
| A polished report becomes manual presentation work | Single data model and renderer-driven outputs |
| Score creates false confidence | Surface Critical/High findings independently and explain scoring scope |
| RTL is treated as a late translation | Design Arabic report alongside English during Task 4 |
| Scope expands into a full SaaS | Keep phase 1 local and single-user; defer auth/cloud sync |

## Immediate starting point

Start **Task 1** next: create the screen inventory and user flows. It is the smallest decision-critical artifact and prevents us from designing screens with unclear functions or data ownership.
