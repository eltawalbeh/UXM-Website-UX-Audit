# UXM Audit — Phase 1 User Flows

## Flow A — Create and scope an audit

**Actor:** UXM Auditor  
**Starting point:** I01 Audit Library

```text
I01 Audit Library
  → select Create audit
I02 Create Audit / Define Scope
  → enter client + website identity
  → define site type, market, journeys, pages, devices, browser, exclusions
  → select default report language
  → save Create draft audit
I03 Audit Overview
```

### Decisions and safeguards

- If the URL is invalid, keep the auditor on I02 and explain the required format.
- If an audit is saved without full scope, label it Draft; it cannot be published.
- Scope inputs determine which checkpoint groups are suggested, not forced.

### Completion condition

A new audit ID exists with client, website, base URL, audit date, auditor, and scope summary.

---

## Flow B — Configure applicability and assess criteria

**Actor:** UXM Auditor  
**Starting point:** I03 Audit Overview

```text
I03 Audit Overview
  → select Review criteria
I04 Criteria Library
  → filter by section / journey / site type
  → mark criterion Applicable, Not applicable, or Not verified
  → for Applicable: select Pass, Partial, or Issue
  → optional: open I05 Criterion Detail for guidance and notes
  → return to I04
I03 Audit Overview reflects progress and provisional section score
```

### Decisions and safeguards

- Not applicable is excluded from the score denominator.
- Not verified is excluded from the score denominator but appears in scope transparency and readiness warnings.
- An Issue without a linked finding needs an internal note.
- Conditional criteria require an applicability decision before assessment.

### Completion condition

Applicable criteria have a recorded status; section progress and provisional scores update immediately.

---

## Flow C — Capture and document a finding

**Actor:** UXM Auditor  
**Starting point:** I04 Criteria Library, I03 Audit Overview, or I07 Findings Queue

```text
From an Issue criterion or Add finding
  → I06 Finding Editor
  → assign page / journey / URL
  → select category and severity
  → upload or attach screenshot
  → add annotation(s) and alt description
  → write: What we observed
  → write: Why it matters
  → write: Recommendation
  → link one or more criteria
  → save finding
I07 Findings Queue
  → linked Issue assessment and roadmap update
```

### Decisions and safeguards

- Stable `UXM-###` ID is allocated at creation and never changes after sort/reprioritization.
- Duplicate warning appears when page, criterion, and title are similar to an existing finding.
- Critical/High cannot be marked publish-ready without evidence and a direct recommendation.
- Screenshot annotations must not obscure the issue being demonstrated.

### Completion condition

The finding appears in the queue, affects the severity distribution and roadmap, and is linked to its underlying criteria.

---

## Flow D — Review scores and prioritize work

**Actor:** UXM Auditor  
**Starting point:** I03 Audit Overview or I07 Findings Queue

```text
I03 / I07
  → select Review scorecard
I08 Scorecard & Priority Review
  → inspect section scores and coverage
  → inspect Critical / High items
  → inspect Fix now / Fix next / Enhance later
  → resolve missing-data warnings
  → mark ready for report review
I09 Publish / Export Readiness
```

### Decisions and safeguards

- Overall score never suppresses Critical/High issues.
- Warning if a score is displayed with too little coverage.
- Warning if any client-facing finding lacks evidence, impact, or recommendation.
- Auditor can return to I04 or I06 directly from a warning.

### Completion condition

The audit is marked `in_review` and all report-blocking fields are complete.

---

## Flow E — Publish English client report

**Actor:** UXM Auditor, then Client Stakeholder  
**Starting point:** I09 Publish / Export Readiness

```text
I09
  → choose English
  → confirm completion checklist
  → Publish client report
C01 Cover
  → C02 Executive Snapshot
  → C03 Scope & Methodology
  → C04 Severity & Category Legend
  → C05 Scorecard
  → C06 Priority Roadmap
  → C07 Section Summary
  → C08 Finding Detail (repeat per finding)
  → C09 Conclusion
  → C10 Closing
```

### Client navigation

```text
Executive Snapshot → Priority Roadmap → Finding Detail → next / previous finding
Scorecard → Section Summary → related Finding Detail
Any detail view → return to roadmap
```

### Completion condition

A read-only English report has a stable URL/path and can be exported to PDF without manual content reconstruction.

---

## Flow F — Publish Arabic RTL client report

**Actor:** UXM Auditor, then Client Stakeholder  
**Starting point:** I09 Publish / Export Readiness

```text
I09
  → choose Arabic
  → verify translated report fields and RTL readiness
  → Publish client report
Arabic C01 → Arabic C10 (same information architecture)
```

### RTL requirements

- Reading order, text alignment, metadata rail, and previous/next controls are RTL.
- URLs, `UXM-###`, browser versions, image filenames, and technical numerals are protected LTR runs.
- Screenshots remain visually untouched.
- A missing Arabic translation produces a readiness warning; English placeholders must not appear in a published Arabic report.

### Completion condition

Arabic report matches the English report's audit facts, score, severity, and findings while reading naturally as an Arabic document.

---

## Flow G — Export PDF

**Actor:** UXM Auditor or Client Stakeholder with allowed access  
**Starting point:** any client report screen

```text
Client Report
  → Export PDF
  → selected report locale and current audit version render
  → browser/download delivers PDF
  → auditor checks cover, scorecard, one finding detail, and conclusion
```

### Safeguards

- Export uses the same report data, locale, and audit version currently being viewed.
- URLs and evidence captions remain readable in PDF output.
- Export preserves page breaks: cover, major report sections, and each Finding Detail begin cleanly.

### Completion condition

PDF is visually consistent with the client report and is fit to send without manual redesign.

---

## System state transitions

```text
Draft
  → In progress         (scope exists and audit work begins)
  → In review           (scorecard has been reviewed)
  → Published           (readiness gates pass; report output generated)
  → Archived            (manual close; remains read-only)
```

## Report readiness gates

| Gate | Required before publish |
|---|---|
| Audit identity | Client, website/product, base URL, date, auditor |
| Scope | At least one journey/page or explicit limited-scope statement |
| Assessment | At least one applicable assessed criterion |
| Findings | Each report finding has category, severity, observation, impact, recommendation, evidence |
| Score transparency | Coverage, N/A, and not-verified states are available to the report |
| Language | All client-facing strings exist in selected locale; Arabic passes RTL validation |

## First vertical-slice acceptance test

A UXM auditor must be able to complete this exact journey before phase 1 is considered functional:

```text
Create “Demo Website Audit”
  → scope the Home and Contact pages on desktop Chrome
  → mark a Navigation criterion as Issue
  → create UXM-001 with an annotated screenshot
  → assign High severity and an implementable recommendation
  → see it appear under Fix now
  → publish English report
  → open the report and confirm UXM-001 has matching evidence, text, severity, and URL
  → change report locale to Arabic and confirm directionality without missing translations
```
