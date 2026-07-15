# UXM Audit — Client Report / English (LTR)

## Design intent

The client report is a calm, evidence-led strategic document. It must answer three questions in order:

1. **What should leadership pay attention to now?**
2. **What proof supports that priority?**
3. **What exact action should the team take?**

It is not an analytics dashboard and not a raw checklist export. Preserve the reference report's screenshot-led, finding-by-finding structure, but improve executive clarity, score transparency, and recommendation quality.

## Global report shell

```text
UXM / Client Name / Website UX Audit                    View roadmap  Export PDF
─────────────────────────────────────────────────────────────────────────────────────
[Current report section]                                Page 05 / 28
```

- Desktop: 12-column editorial grid, warm canvas, white report pages, 48px outer padding.
- PDF: A4 landscape; each major section and each Finding Detail starts on a clean page.
- Web: thin top progress/navigation rail; no permanent side navigation that competes with evidence.
- Any report preview before publication includes a visible `DRAFT` watermark.
- Main report actions are `View roadmap` and `Export PDF`; no marketing CTA competes with the audit content.

---

## C01 — Cover

### Job
Establish confidence, report identity, and audit context without spending a page on decoration.

### Composition

```text
UXM                                                Client logo (optional)

Website UX Audit
[Client website / product name]

A focused review of user experience, discoverability, and conversion readiness.

Website URL                 Report version
Audit date                  Prepared by UXM

[restrained website crop or device visual, evidence-adjacent—not stock imagery]
```

### Rules

- Use client logo only when supplied and approved; UXM mark remains primary report author.
- A website crop may appear only if it is the audited website and is visually legible.
- Do not put a giant score on the cover; decisions come after scope context.
- No generic welcome copy, fake badges, or decorative gradients.

---

## C02 — Executive Snapshot

### Job
Give a stakeholder the decision-ready conclusion in under two minutes.

### Composition

```text
Executive snapshot

72 / 100          Needs targeted improvement
UX Health Score    3 High-priority issues require action

What is working                     What needs attention now
• Clear primary value proposition   1. Navigation contrast obscures key destinations
• Credible service information      2. Required form fields appear only after error
• ...                               3. ...

Scope: 6 pages • 3 journeys • Desktop Chrome + Mobile Safari • 14 Jul 2026
```

### Rules

- Large score numeral is paired with assessment label, coverage statement, and Critical/High count.
- Use two deliberately unequal editorial columns—strengths are concise; priority actions carry more space.
- `What needs attention now` links directly to finding IDs in the roadmap.
- If coverage is incomplete, show `Provisional` beside the score.
- Never use equal KPI tiles or a score ring without explanation.

---

## C03 — Scope & Methodology

### Job
Make the report defensible: explain what was tested, how, and where limits remain.

### Composition

- Scope narrative: client/product, audience assumptions, business/site type.
- Tested journeys and pages.
- Devices, browser versions, resolutions, and capture dates.
- Assessment states: Pass, Partial, Issue, Not applicable, Not verified.
- Explicit exclusions and non-verified scenarios.

### Rules

- Use a concise timeline/structured list, not an oversized paragraph.
- `Not applicable` and `Not verified` are never merged; they mean different things to score coverage.
- Technical strings (URLs, device models, browser versions) are rendered in LTR isolated fields.

---

## C04 — Severity & Category Legend

### Job
Ensure every reader interprets severity and category labels consistently.

### Composition

```text
Severity
[1 Critical] Immediate risk to a core task, trust, or accessibility
[2 High]     Significant friction in a valuable journey
[3 Medium]   Noticeable friction; a workaround exists
[4 Low]      Limited-impact clarity or polish improvement

Issue categories
Usability · Information Architecture · Interface & Visual Design · Content & Microcopy
Trust & Credibility · Forms & Data Entry · Search & Discovery · Accessibility · Technical / Bug
```

### Rules

- Severity always uses rank, label, icon, and color.
- Categories remain neutral; do not color-code them like severity.
- Keep definitions client-readable; no UX jargon without a short explanation.

---

## C05 — Scorecard

### Job
Reveal systemic strengths and weaknesses without reducing the audit to a single grade.

### Composition

```text
Scorecard
72 / 100  Needs targeted improvement      38 of 44 applicable core checks assessed

Section health
Navigation & Information Architecture       56%   17 / 29
Task Orientation                             74%   14 / 19
Writing & Content Quality                    81%   13 / 16

Finding distribution
0 Critical   3 High   6 Medium   3 Low

Coverage notes
Search not applicable • Account recovery not verified
```

### Rules

- Section rows have name, visible percentage, assessed/applicable count, and a small bar.
- Show only sections included in the audit scope; do not display irrelevant sections as zero.
- Critical/High distribution sits adjacent to the score.
- Every chart has a text equivalent in the web report and a caption in PDF.

---

## C06 — Priority Roadmap

### Job
Turn the audit into an ordered improvement conversation.

### Composition

```text
Priority roadmap

Fix now
[UXM-012] [2 High] Improve header navigation contrast
Home · Discover · Expected impact: clearer route discovery

Fix next
[UXM-009] [3 Medium] Identify required form fields before submission
Apply · Complete · Expected impact: fewer form errors

Enhance later
[UXM-004] [4 Low] Clarify tooltip labels
```

### Rules

- Groups: `Fix now` = Critical + High; `Fix next` = Medium; `Enhance later` = Low / approved opportunities.
- Each roadmap item links to its finding detail and shows title, issue ID, page/journey, impact summary, and severity.
- Do not show arbitrary estimated business ROI unless a tested model/data source supports it.
- Keep the top 3 `Fix now` items visible without scrolling on standard desktop where possible.

---

## C07 — Section Divider / Summary

### Job
Create a pause before related detailed findings and explain the pattern they share.

### Composition

```text
Navigation & Information Architecture
56% section health • 4 findings

The site provides recognizable top-level destinations, but low contrast and inconsistent labels
make the first exploration step harder than necessary.

Key strength: ...                    Key risk: ...
```

### Rules

- Spacious editorial page, one score, one paragraph, one strength, one risk.
- Do not repeat full scorecard content.
- Use section title and insight—not a generic image or decorative divider.

---

## C08 — Finding Detail

### Job
Prove one issue, explain its consequence, and prescribe a direct next step.

### Composition

```text
UXM-012                                      [2 High] [Navigation & Information Architecture]
Navigation labels have insufficient contrast
Home / Discover                               https://client.com/

┌───────────────────────────────────────────────────────┬───────────────────────────┐
│ Annotated evidence screenshot                          │ What we observed          │
│ • red outline / numbered markers                       │ [factual statement]       │
│ • descriptive alt text available in web report         │                           │
│                                                       │ Why it matters            │
│                                                       │ [user + business impact] │
│                                                       │                           │
│                                                       │ Recommendation            │
│                                                       │ [action-led resolution]  │
└───────────────────────────────────────────────────────┴───────────────────────────┘
Device / browser / capture time          View page ↗        Previous / Next finding
```

### Rules

- Screenshot occupies approximately two-thirds of the page; the narrative rail gets one-third.
- Evidence annotation is red and has no relationship to severity color.
- The narrative order is fixed: `What we observed` → `Why it matters` → `Recommendation`.
- Finding title must describe the condition, not merely the solution.
- Show URL in full in web report with copy affordance; PDF may wrap at safe separators but must remain complete.
- `Previous / Next` follows report order and remains accessible by keyboard.
- Do not combine unrelated problems into a single finding for page-count efficiency.

---

## C09 — Conclusion & Validation Next Steps

### Job
Close with a usable plan after the immediate remediation work is complete.

### Composition

- Issue distribution summary by severity and category.
- Repeating experience patterns observed across findings.
- Suggested validation: usability test, funnel measurement, accessibility re-check, or post-release analytics review.
- A concise next-engagement recommendation that follows from demonstrated findings; no generic sales pitch.

### Rules

- The conclusion summarises; it does not introduce unsubstantiated new issues.
- Use prose + a simple distribution visual, not a dense set of charts.
- Mention audit limitations again only if they materially affect interpretation.

---

## C10 — Closing

### Job
End the report cleanly in a format suitable for PDF and web.

### Composition

```text
UXM
Thank you

Website UX Audit • [Client / Website] • [Report date]
```

### Rules

- No stock photography or oversized slogan.
- Use the approved UXM logo when available; until then, text wordmark only.
- Provide report version/reference for traceability.

---

## Client report interactions

| Interaction | Behavior |
|---|---|
| Roadmap item | Opens matching Finding Detail, preserving return context |
| Section score | Opens Section Summary, then related findings |
| Export PDF | Exports selected language + audit version from same report data |
| Copy URL | Copies full audited page URL, not the report URL |
| Evidence image | Zooms to inspect; alt text remains available |
| Language switch | Opens equivalent locale report only after localized fields are ready |

## Mobile behavior

- Reading order: Snapshot → Roadmap → scorecard / scope → sections → findings → conclusion.
- Finding Detail stacks: identity → evidence → observation → impact → recommendation → metadata.
- A compact sticky footer contains `Roadmap` and `Export PDF`; never obscures report content.
- Full URL, evidence caption, and recommendation must remain expandable without truncation.
