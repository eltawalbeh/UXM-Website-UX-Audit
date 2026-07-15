# UXM Audit — Finding Editor & Evidence Annotation

## Purpose

The Finding Editor converts a reviewer observation into a specific, evidence-backed, actionable client report item. It is the highest-stakes screen in the internal workspace: weak copy, ungrounded claims, and vague recommendations must be prevented here—not discovered during PDF export.

## Design principle

**Evidence first; narrative second; metadata always available.**

The screenshot proves the observation. The written narrative explains the implication. The right-side metadata makes the finding traceable and prioritizable. The editor is a focused work surface, not a long generic form.

## Desktop layout

```text
← Back to findings                                    Draft saved  [Preview] [Save finding]

UXM-012  [2 High] [Navigation & IA]
Navigation labels have insufficient contrast

┌───────────────────────────────────────────────┬───────────────────────────────────────┐
│ Evidence                                      │ Finding context                        │
│                                               │ Page / journey                         │
│ [Screenshot canvas]                           │ Home • Discover                        │
│ [annotation toolbar]                          │ URL                                    │
│                                               │ https://client.com/                    │
│                                               │ Criteria                               │
│ [Evidence caption + alt text]                 │ N02, V14                               │
├───────────────────────────────────────────────┤ Severity     [2 High ▾]                │
│ What we observed                              │ Category     [Navigation & IA ▾]       │
│ [Concise factual observation]                 │ Effort       [Medium ▾]                │
│                                               │ Confidence   [High ▾]                  │
│ Why it matters                                │ Captured     14 Jul 2026, 14:20        │
│ [User + business impact]                      │                                       │
│                                               │ [Delete finding]                       │
│ Recommendation                                │                                       │
│ [Action-led recommendation]                   │                                       │
└───────────────────────────────────────────────┴───────────────────────────────────────┘
```

## Fixed content order

### 1. Finding identity

- Stable ID allocated on creation: `UXM-001`, `UXM-002`, etc.
- ID does not change after severity change, sorting, or report translation.
- Short title is factual, specific, and scannable: `Required fields are not identified before submission`.
- Avoid titles that are merely recommendations, opinions, or vague labels such as `Improve navigation`.

### 2. Evidence

**Required for any published finding.**

#### Evidence canvas

- Large source screenshot at useful resolution.
- Contained by a 1px `Line` border; no fake device frame unless device context materially matters.
- Image is never mirrored in Arabic report mode.
- Auditor can zoom, pan, and fit image to frame.

#### Annotation tools

| Tool | Use | Rule |
|---|---|---|
| Rectangle | Highlight a bounded UI issue | 2px red solid/dashed outline; 4px radius |
| Pin | Number multiple related areas | 20–24px circular marker; links to a caption |
| Arrow | Clarify flow/direction where a box is insufficient | Keep outside important text where possible |
| Text label | Short clarification | Never cover the issue; max one short line |
| Crop / redact | Protect sensitive data | Original evidence remains protected and inaccessible in client output when redacted |

- Annotation red indicates evidence, not severity.
- Use the fewest annotations that make the issue undeniable.
- Multiple independent problems require separate findings, even if visible in one screenshot.

#### Evidence metadata

- Source file name
- Page/screen name
- URL
- Device/browser/resolution
- Capture timestamp
- Alt text: factual description of what the screenshot and annotation show

### 3. What we observed

**Purpose:** State only what the auditor can demonstrate.

**Pattern:** `[Interface element] + [observed condition] + [context]`.

**Good:** `The header navigation labels are pale against the image-based hero background, making the primary destinations difficult to scan on the home page.`

**Avoid:** `The navigation is bad.`

**Length:** 1–3 concise sentences. Do not repeat severity or recommendation here.

### 4. Why it matters

**Purpose:** Connect the observation to user friction and business impact.

**Pattern:** `[Affected user/task] + [resulting friction] + [likely consequence]`.

**Good:** `First-time visitors may miss the service and support destinations, slowing exploration and reducing the likelihood of reaching a relevant conversion path.`

**Avoid:** `This creates a bad user experience.`

**Length:** 1–2 concise sentences.

### 5. Recommendation

**Purpose:** State the smallest actionable resolution that UXM can stand behind.

**Pattern:** `[Action verb] + [specific design/content/change] + [validation condition if useful]`.

**Good:** `Increase header-label contrast against every hero state and validate text contrast at WCAG AA before release.`

**Avoid:** `Make it clearer.`

**Length:** one primary recommendation. Use a numbered plan only when remediation requires ordered steps.

## Context rail

The right-side rail keeps report metadata traceable without making it the visual focus.

### Required fields

| Field | Rule |
|---|---|
| Page / journey | Select from audit scope; allow a new page only with explicit name/URL |
| URL | Pre-filled from selected page, editable, rendered LTR in Arabic |
| Category | One primary category; use the UXM category vocabulary |
| Severity | Critical, High, Medium, Low; label + rank + icon + color |
| Linked criteria | One or more UXM checkpoint IDs; use searchable selector |
| Evidence | At least one item prior to publishing |

### Optional fields

- Effort: Small / Medium / Large
- Confidence: High / Medium / Low
- Capture date/time
- Device/browser/resolution
- Internal implementation note (never published unless explicitly promoted)

### Category set

- Usability
- Information Architecture
- Interface & Visual Design
- Content & Microcopy
- Trust & Credibility
- Forms & Data Entry
- Search & Discovery
- Accessibility
- Technical / Bug
- Opportunity

## Severity selection

```text
1 Critical — Fix immediately; core task, trust, or accessibility risk
2 High     — Fix in the priority release; substantial journey friction
3 Medium   — Plan into the next improvement cycle
4 Low      — Improve when capacity allows
```

### Guardrails

- Severity includes its rank and written definition at selection time.
- Critical/High requires evidence, a complete impact statement, and an actionable recommendation.
- Severity selection prompts for a quick review when a finding is downgraded from Critical/High.
- `Opportunity` is a category, not a severity; it still receives a severity only when its omission causes evidenced friction.

## Save, validation, and quality states

### Autosave

- Autosave field edits with a visible `Saving` → `Saved` state.
- Do not imply an image upload or annotation export has completed until it actually has.

### Before a finding can be report-ready

- Title exists and is specific.
- Page/journey, URL, category, and severity exist.
- At least one evidence item exists with alt text.
- Observation, impact, and recommendation are complete.
- At least one checkpoint is linked, unless the auditor explicitly marks it as an unlisted specialist finding and supplies a reason.

### Quality warnings

| Condition | Warning |
|---|---|
| Observation has no factual statement | `Describe the observed interface condition before publishing.` |
| Impact is vague | `Explain which task or user is affected and why it matters.` |
| Recommendation lacks an action verb | `Start with the specific action required to resolve this finding.` |
| Evidence has no alt text | `Add a concise description of what this annotated evidence shows.` |
| Screenshot contains possible personal data | `Review and redact sensitive information before publishing.` |
| Similar finding exists | `This may overlap with UXM-00X. Compare before keeping both.` |

## English and Arabic content model

Every client-facing text field is language-aware:

```text
Title:             [English] [Arabic]
What we observed:  [English] [Arabic]
Why it matters:    [English] [Arabic]
Recommendation:    [English] [Arabic]
Evidence alt text: [English] [Arabic]
```

- Phase 1 may allow one working language during drafting, but a report cannot publish in a locale with incomplete required fields.
- Arabic fields are edited RTL. URLs, issue IDs, browser versions, and file names stay LTR.
- Do not translate severity/category values freehand; use controlled locale labels.

## Mobile editor behavior

- Evidence occupies the first screen; metadata appears in a labelled bottom sheet or after the narrative.
- Annotation toolbar becomes a bottom action strip with labelled controls; gesture-only annotation is prohibited.
- Autosave state remains visible.
- `Save finding` stays reachable at the bottom while a field is being edited; it does not cover form content.

## Accessibility requirements

- Canvas tools have text labels and keyboard alternatives for adding/moving/deleting annotations.
- Annotation pins have accessible names such as `Annotation 1: low-contrast header navigation`.
- Form field errors are connected to the specific field and announced to assistive technology.
- Keyboard order: identity → evidence → observation → impact → recommendation → context fields → save.
- No essential validation relies on red/green color.

## Finding detail output mapping

| Editor field | Client report output |
|---|---|
| Stable ID + title | Finding heading |
| Severity + category | Metadata chips |
| Page/journey/URL | Context rail |
| Evidence + annotations + alt text | Evidence frame |
| What we observed | Observation block |
| Why it matters | Impact block |
| Recommendation | Recommendation panel |
| Device/capture data | Capture metadata |
| Effort/confidence | Optional implementation context |
