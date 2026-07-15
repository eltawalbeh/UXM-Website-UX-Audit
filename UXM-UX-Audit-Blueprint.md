# UXM Website UX Audit — Blueprint v1

## 1. Purpose
Create a repeatable, client-ready UXM audit system for websites. It must turn a structured expert review into a premium visual report—not a generic checklist—and support English (LTR) and Arabic (RTL) output from the same audit data.

## 2. Source analysis

### 2.1 Audit criteria source
`ExpertReviewCheckpoints.xls` contains **247 checkpoints** across nine sections:

| Section | Checkpoints |
|---|---:|
| Home Page | 20 |
| Task Orientation | 44 |
| Navigation & Information Architecture | 29 |
| Forms & Data Entry | 23 |
| Trust & Credibility | 13 |
| Writing & Content Quality | 23 |
| Page Layout & Visual Design | 38 |
| Search | 20 |
| Help, Feedback & Error Tolerance | 37 |
| **Total** | **247** |

The workbook's original output is a raw score, answered-question count, and section score. It is a valid research base, but it is old (last updated 2014) and includes conditional/e-commerce-specific checks. UXM must preserve the intent but avoid applying irrelevant checks to every site.

### 2.2 Reference report source
The Monshaat report has a clear client-report rhythm:
1. Cover
2. Introduction
3. Severity / usability rating scale
4. Issue-category legend
5. Audit environment and device/browser information
6. Report-format explainer
7. Section divider
8. One issue per page, repeated
9. Conclusion / issue distribution
10. Closing page

Every issue page uses the same anatomy:
- Large annotated website screenshot
- Issue number
- Category label
- Four-level severity scale
- Problem statement
- Solution / direct recommendation
- Screen or page name
- Date/time captured
- Deep link to the audited page

## 3. UXM audit model

### 3.1 Eligibility first
Before scoring a checkpoint, the auditor marks it:
- **Pass** — meets the criterion
- **Issue** — does not meet the criterion; create a finding when material
- **Partial** — partly meets it
- **Not applicable** — irrelevant to the website, product type, or tested flow
- **Not verified** — needs access, data, or a test state not available

This avoids the source sheet's main weakness: treating every one of 247 checks as relevant to every site.

### 3.2 UXM severity scale
Use four levels, keeping the clarity of the reference but making the language client-ready:

| Level | Meaning | Action |
|---|---|---|
| Critical | Prevents a core task, introduces a serious trust/accessibility risk, or can cause material loss | Fix before launch / immediately |
| High | Causes substantial friction in a high-value journey or affects many users | Fix in the next priority release |
| Medium | Noticeable friction, confusion, or inconsistency; workaround exists | Plan into the next improvement cycle |
| Low | Cosmetic or small clarity improvement with limited task impact | Fix when capacity allows |

### 3.3 UXM issue categories
Retain the reference report's useful taxonomy, with clearer labels:
- **Usability** — task completion, comprehension, interaction friction
- **Information Architecture** — navigation, hierarchy, grouping, findability
- **Interface & Visual Design** — hierarchy, components, readability, responsive layout
- **Content & Microcopy** — labels, messages, descriptions, language clarity
- **Trust & Credibility** — legitimacy, transparency, pricing/policy confidence
- **Forms & Data Entry** — input, validation, errors, checkout/application flows
- **Search & Discovery** — search, browse, filters, results
- **Accessibility** — keyboard, contrast, semantics, zoom, assistive technology
- **Technical / Bug** — broken or unexpected behaviour
- **Opportunity** — feature or experience improvement, not a defect

### 3.4 Score logic
Scores should be transparent and never hide critical findings.
- Each applicable checkpoint gets: Pass = 1, Partial = 0.5, Issue = 0.
- `Section score = achieved points / applicable checkpoints × 100`.
- Overall score is a weighted average of applicable sections.
- Critical and High findings are displayed separately at the top of the report; a good numerical score does not neutralize them.
- Weights are selected by site type / scope. For example, Forms and Trust gain weight for e-commerce, government, finance, and lead-generation journeys; Search is weighted only when search exists and matters.

## 4. Client report blueprint

### P01 — Cover
- Brand: UXM + client logo
- “Website UX Audit”
- Website URL / product name
- Audit date, language, report version
- Restrained device visual or subtle webpage crop

### P02 — Executive snapshot
- Overall UX score and assessment label
- Number of findings by severity
- Top 3 actions
- Audit scope: journeys, device sizes, browser(s), and pages checked
- A short plain-language verdict: where the site is strong and where it is losing users

### P03 — Methodology & scope
- What was tested and what was not
- Expert-review process
- Device/browser/resolution, test dates, and accessibility assumptions
- “Not applicable” and “not verified” explanation

### P04 — Severity and category legend
- Four severity levels
- Category labels and icons
- Clear statement that priority considers task impact, reach, and business risk

### P05 — Scorecard
- Overall score
- Section scores from the applicable UXM framework
- Severity distribution
- Optional journey-health scorecards: discover → understand → decide → complete → recover

### P06 — Priority roadmap
- **Fix now:** Critical / High
- **Fix next:** Medium
- **Enhance later:** Low / opportunities
- Each action shows issue ID, page/journey, recommendation, owner suggestion, and expected impact

### P07 onward — Findings
One issue per page/screen on desktop PDF and one expandable finding in the web report.

**Finding anatomy:**
1. `UXM-001` stable issue ID
2. Severity chip and category chip
3. Page / journey / URL
4. Annotated evidence screenshot
5. “What we observed” — concise factual statement
6. “Why it matters” — user and business impact
7. “Recommendation” — direct, implementable action
8. Optional effort and confidence indicators
9. Capture date and tested device

### Final pages
- Section-level patterns and strengths
- KPI / validation suggestions after implementation
- Closing / next-step call to action

## 5. UXM visual direction

### Preserve from the reference report
- Calm, editorial PDF structure—not a busy dashboard
- Strong section dividers
- One finding per page, allowing evidence and recommendation to breathe
- Screenshot-led evidence with explicit issue annotation
- Persistent issue number, category, severity, page name, timestamp, and URL
- Closing distribution summary

### Improve for UXM
- Replace Monshaat teal-only brand treatment with UXM's own system and logo
- Use modern type scale, larger body text, and stronger contrast
- Use a colorblind-safe severity system: color plus written label plus number/icon; never color alone
- Replace “Problem / Solution” with `What we observed / Why it matters / Recommendation`
- Add Executive Snapshot and Priority Roadmap before detailed findings
- Add section scores based on applicable—not blindly all—criteria
- Add page/journey URL and screenshot alt-text or textual evidence for accessibility
- Eliminate ambiguous numerical scale display such as “1 2 3 4” without a clearly selected state

### Suggested layout rules
- A4 landscape or 16:9 presentation-style report; one decision after another, no dense dashboard grids
- 12-column desktop grid; wide evidence canvas (about two-thirds) + concise metadata rail (about one-third)
- Body copy in 11–12pt PDF equivalent; no tiny annotations
- Minimum contrast target: WCAG AA for text and interactive web-report UI
- Image annotations: red outline/callout for the observed issue; use numbered markers for multiple areas; never obscure the evidence
- Recommendations use a neutral or UXM accent panel—not green/red as the sole meaning carrier

## 6. Arabic / RTL rules
- The Arabic report must be a true RTL layout—not English pages merely mirrored.
- Right-align Arabic titles, paragraphs, labels, finding metadata, and visual flow.
- Keep numbers, URLs, product names, browser versions, and code-like strings LTR inside isolated spans/fields.
- Mirror the evidence rail and metadata rail, but do not mirror website screenshots themselves.
- Maintain Arabic-first labels in Arabic output; do not leave English placeholders such as “Home page” or “Click here to view the page.”
- Use an Arabic typeface designed for sustained reading and matching Latin companion font; validate line height, punctuation, and mixed Arabic/English strings.
- Verify every layout at both desktop PDF width and mobile web-report width.

## 7. Product structure for a reusable UXM system

### Internal audit workspace
- Client and project information
- Scope / pages / journeys
- Filtered 247-checkpoint library
- Checkpoint status, evidence, notes, and linked findings
- Findings database with unique IDs
- Automatic section scores, priority queue, and report data

### Client-facing report
- Shareable web report first
- Export-quality PDF generated from the same data
- English and Arabic output modes
- No editing of report copy in two disconnected places

## 8. First implementation sequence
1. Convert the Excel criteria into a structured, modern UXM checkpoint library with applicability rules.
2. Define UXM brand tokens (logo, color, typography, spacing, icons) before creating screens.
3. Design the client report in English first: Cover, Executive Snapshot, Scorecard, Roadmap, Finding Detail, Conclusion.
4. Create the Arabic RTL variant as a deliberately designed counterpart.
5. Build an internal audit-entry flow that produces the report data.
6. Test the full system on one real website and adjust the criteria, scoring, and report language before productizing it.

## 9. Decisions already made
- The English PDF is the structural and visual reference.
- The Arabic PDF establishes RTL delivery requirements, but UXM will improve its localization discipline.
- The Excel sheet is the source of criteria—not the final UXM experience or scoring method.
- UXM will use a filtered, applicable checklist and a screenshot-led, finding-by-finding client report.
