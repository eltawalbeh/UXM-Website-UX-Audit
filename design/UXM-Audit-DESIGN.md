---
version: alpha
name: UXM Audit
license: Proprietary — UXM
summary: Evidence-led editorial precision for bilingual website UX audits.
colors:
  ink: "#16212B"
  ink-muted: "#52616D"
  canvas: "#F5F3EE"
  surface: "#FFFEFB"
  surface-subtle: "#ECEAE4"
  line: "#D8D6CF"
  accent: "#C84A35"
  accent-strong: "#A93626"
  accent-soft: "#FBE9E4"
  link: "#1F5F8B"
  severity-critical: "#A51D2D"
  severity-high: "#B13D2A"
  severity-medium: "#8A5C00"
  severity-low: "#356C50"
  severity-critical-soft: "#FDEBED"
  severity-high-soft: "#FBE9E4"
  severity-medium-soft: "#FFF3D6"
  severity-low-soft: "#EAF5ED"
  annotation: "#C8262D"
  recommendation: "#245E4B"
typography:
  display:
    fontFamily: "Manrope, IBM Plex Sans Arabic, Arial, sans-serif"
    fontSize: "3rem"
    fontWeight: 700
    lineHeight: 1.06
    letterSpacing: "-0.035em"
  heading-lg:
    fontFamily: "Manrope, IBM Plex Sans Arabic, Arial, sans-serif"
    fontSize: "2rem"
    fontWeight: 700
    lineHeight: 1.16
    letterSpacing: "-0.025em"
  heading-md:
    fontFamily: "Manrope, IBM Plex Sans Arabic, Arial, sans-serif"
    fontSize: "1.375rem"
    fontWeight: 700
    lineHeight: 1.25
    letterSpacing: "-0.015em"
  body-md:
    fontFamily: "Manrope, IBM Plex Sans Arabic, Arial, sans-serif"
    fontSize: "1rem"
    fontWeight: 450
    lineHeight: 1.6
    letterSpacing: "0em"
  body-sm:
    fontFamily: "Manrope, IBM Plex Sans Arabic, Arial, sans-serif"
    fontSize: "0.875rem"
    fontWeight: 500
    lineHeight: 1.5
    letterSpacing: "0em"
  label:
    fontFamily: "Manrope, IBM Plex Sans Arabic, Arial, sans-serif"
    fontSize: "0.75rem"
    fontWeight: 700
    lineHeight: 1.3
    letterSpacing: "0.06em"
rounded:
  xs: "4px"
  sm: "8px"
  md: "12px"
  lg: "18px"
  pill: "999px"
spacing:
  1: "4px"
  2: "8px"
  3: "12px"
  4: "16px"
  5: "20px"
  6: "24px"
  8: "32px"
  10: "40px"
  12: "48px"
  16: "64px"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.surface}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.sm}"
    padding: "12px 16px"
  button-primary-hover:
    backgroundColor: "#273842"
    textColor: "{colors.surface}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.sm}"
    padding: "12px 16px"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.sm}"
    padding: "12px 16px"
  chip-critical:
    backgroundColor: "{colors.severity-critical-soft}"
    textColor: "{colors.severity-critical}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "6px 10px"
  chip-high:
    backgroundColor: "{colors.severity-high-soft}"
    textColor: "{colors.severity-high}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "6px 10px"
  chip-medium:
    backgroundColor: "{colors.severity-medium-soft}"
    textColor: "{colors.severity-medium}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "6px 10px"
  chip-low:
    backgroundColor: "{colors.severity-low-soft}"
    textColor: "{colors.severity-low}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "6px 10px"
---

## Overview

**Design read:** UXM Audit is an evidence-led editorial system for business stakeholders and UX professionals. It must feel precise, composed, and premium—more like a well-produced strategic report than a generic SaaS dashboard.

The design has one job: move a stakeholder from **what is wrong** to **why it matters** to **what should happen next**, with evidence always visible. The reference report's spacious, screenshot-first rhythm is retained; its brand, dated density, and ambiguous rating display are not.

### Design personality

- Quietly confident, analytical, and human—not clinical or decorative.
- Warm paper-like canvas with near-white report surfaces; deep ink typography and a restrained terracotta accent.
- Evidence is the visual hero. UI chrome stays quiet.
- Internal workspace is focused and practical; client report is editorial and decision-ready.
- Bilingual by construction: English LTR and Arabic RTL are equal first-class layouts.

### Explicitly avoid

- Purple/blue AI gradients, glass cards, fake metrics, and empty dashboard decoration.
- Centered marketing-hero layouts, card farms, excessive pills, or arbitrary shadows.
- Pure black/white defaults, low-contrast pale text, tiny annotations, or visual severity communicated by color alone.
- Translating English layouts mechanically into Arabic.

## Colors

### Core palette

| Token | Value | Role |
|---|---:|---|
| Ink | `#16212B` | Headlines, primary text, primary action, score numerals |
| Ink muted | `#52616D` | Secondary body copy and metadata |
| Canvas | `#F5F3EE` | App shell and report background; warm, non-white foundation |
| Surface | `#FFFEFB` | Primary report page, cards, form surfaces |
| Surface subtle | `#ECEAE4` | Dividers, inactive states, grouped neutral fields |
| Line | `#D8D6CF` | Borders and low-emphasis separators |
| Accent | `#C84A35` | UXM emphasis, selected states, deliberate editorial accent |
| Link | `#1F5F8B` | URLs and navigable text; always paired with underlining or icon where helpful |

### Semantic colors

Severity has written labels, numeric order, and iconography in addition to color.

| Severity | Solid | Background | Meaning |
|---|---:|---:|---|
| Critical | `#A51D2D` | `#FDEBED` | Immediate task, trust, or accessibility risk |
| High | `#B13D2A` | `#FBE9E4` | High-value journey friction |
| Medium | `#8A5C00` | `#FFF3D6` | Material friction with a viable workaround |
| Low | `#356C50` | `#EAF5ED` | Limited-impact improvement |

- Annotation red is `#C8262D`; it identifies the observed issue only and is not a severity indicator.
- Recommendation green is `#245E4B`; it identifies an action panel only and is not a positive severity state.
- Do not use saturated color for long body text on colored panels.

## Typography

### Font pairing

- **English and numerals:** `Manrope` for clean, compact professional reading.
- **Arabic:** `IBM Plex Sans Arabic` for long-form clarity, mixed-script stability, and sober modern character.
- Fallback: `Arial, sans-serif`.

Do not force a single Latin font to render Arabic. Use locale-aware font stacks and test genuine Arabic paragraphs, URLs, and Arabic/English mixed metadata.

### Type rules

- Display type appears only on the cover, section dividers, and executive score contexts.
- Use `heading-lg` for report section titles, `heading-md` for finding titles, and `body-md` for all client-facing explanations.
- Labels are short metadata only. In English, use restrained sentence case—not loud all caps. In Arabic, never apply artificial letter spacing.
- Minimum web body size: 16px. Minimum PDF body equivalent: 11pt. Minimum screenshot annotation label: 12px / 9pt.
- Arabic uses a slightly more generous line-height (1.7) where needed; maintain a consistent baseline rhythm.

## Layout

### Report composition

- **Web desktop:** 12-column grid; max content width 1440px; outer page padding 48px.
- **PDF:** A4 landscape is the default. Maintain a 12-column grid, 24px gutters, and a clear 20mm safe margin.
- **Finding detail:** Evidence canvas occupies 8 columns; metadata rail occupies 4 columns. Do not shrink screenshots to make room for verbose prose.
- **Executive pages:** use asymmetry and editorial pacing: score/summary beside priority actions, not equal-sized card rows.
- **Section dividers:** substantial breathing room, one key insight, score, and finding count.

### Responsive behavior

| Width | Layout behavior |
|---|---|
| ≥ 1200px | 12-column grid; persistent metadata rail; evidence and text side-by-side |
| 768–1199px | 8-column grid; metadata wraps above evidence details where necessary |
| < 768px | single column; score/roadmap first, evidence full-width, metadata follows image |

- The internal workspace can use a contextual side panel on desktop, but all primary audit actions remain reachable on narrow screens.
- Client reports retain source order on mobile: summary → evidence → finding details → recommendation.
- Never create horizontal page scrolling.

### Directionality

- The English report is LTR; Arabic report reads RTL from the page shell down to navigation and metadata placement.
- URLs, browser versions, issue IDs such as `UXM-001`, dates in ISO format, and file names render in isolated LTR spans.
- Screenshots, screen coordinates, and web UIs inside screenshots are not mirrored.

## Elevation & Depth

- Default surface treatment is a 1px `Line` border; no shadow.
- Use one restrained shadow only for floating controls, e.g. a popover or annotation toolbar: `0 10px 30px rgba(22,33,43,0.10)`.
- Evidence images are framed by a 1px line and small inner canvas padding; never use heavy device mockups by default.
- Section transitions use space and a slim accent rule—not gradients or large colored blocks.

## Shapes

- Default controls: 8px radius.
- Report content surfaces: 12px radius only when they require a contained surface; the report page itself remains flat.
- Severity/category chips: full pill radius, compact, one line.
- Screenshot annotations: 2px solid or dashed outline, 4px radius, numbered pins at 20–24px. Use red for observed evidence and an explanatory caption outside the screenshot.
- Icons use a single 1.75px rounded stroke family. Use familiar icons only; pair unfamiliar symbols with labels.

## Components

### Severity chip

`[1 Critical]`, `[2 High]`, `[3 Medium]`, or `[4 Low]`.

- Always include rank + written severity + optional alert icon.
- Never show only a four-color bar or an unexplained `1 2 3 4` row.
- Use the matching semantic background and text token.

### Category chip

Neutral outlined chip with a familiar icon and full label, e.g. `Information Architecture` or `Content & Microcopy`. Category color must not compete with severity color.

### Issue identity

Show stable ID, then concise factual title:

```text
UXM-014  |  Navigation labels have insufficient contrast
```

The ID is monospaced only if a dedicated monospace fallback is available; otherwise use the body label style. It must remain LTR in Arabic.

### Score ring and score bar

- Overall score is a large numeral plus a concise assessment label, not a ring alone.
- Section scores use restrained bars with a visible numeric percentage.
- Scores show coverage: `38 of 44 applicable checks assessed`.
- Critical/High count stays visible adjacent to any score.

### Evidence frame

- Use the source screenshot at a useful scale with crisp 1px border.
- Add red dashed/solid outline only around the exact observed issue.
- Add numbered pin(s) if multiple areas need discussion.
- Every image requires alt text that explains what the annotation is demonstrating.
- Support pre/post evidence as distinct frames; never overlay a recommendation mockup on top of the evidence.

### Finding narrative

Maintain this fixed order:

1. `What we observed`
2. `Why it matters`
3. `Recommendation`

The observation is factual, impact ties to task/business effect, and recommendation starts with an action verb. These are visibly distinct blocks, not a wall of text.

### Recommendation panel

- Green-tinted left/right edge depending on locale plus plain-language heading `Recommendation` / `التوصية`.
- Use a quiet surface; it must read as a proposed action, not a success state.
- One primary recommendation per finding. Break larger work into numbered implementation steps only when necessary.

### Internal workspace controls

- Status selector: explicit text options `Pass`, `Partial`, `Issue`, `Not applicable`, `Not verified`.
- Critical actions use confirmation only where data will be discarded or publication occurs.
- Review rows prioritize criterion title, applicability, status, linked finding count, and evidence—not generic progress widgets.
- Empty states state what is missing and show one clear next action.

## Do's and Don'ts

### Do

- Let a screenshot, clear finding title, and priority lead every detail page.
- Use full real labels: `What we observed`, `Why it matters`, `Recommendation`.
- Build visual rhythm with wide evidence, short prose blocks, section pacing, and whitespace.
- Preserve a client’s visual evidence accurately; annotations must be precise and minimal.
- Make desktop and mobile report layouts intentional, not merely scaled.
- Test Arabic content in real paragraphs, long finding titles, URLs, and mixed-language metadata.

### Don't

- Do not use generic SaaS KPI tiles as the main Executive Snapshot.
- Do not repeat the same equal-height card grid throughout the report.
- Do not use color alone to communicate severity, status, or completeness.
- Do not truncate URLs, recommendation text, or Arabic labels without a visible way to view the full value.
- Do not treat a score as a verdict when Critical/High findings exist.
- Do not put dense data tables in the client report; reserve audit density for the internal workspace.

## Accessibility & quality gates

- All normal text / background combinations must meet WCAG AA 4.5:1 minimum; large display text must meet 3:1 minimum.
- Interactive targets are at least 44×44px on touch surfaces; desktop dense rows retain 32px minimum with sufficient separation.
- All controls have visible keyboard focus using a 2px `Accent` outline with 2px offset.
- Do not use automatic animation on report pages. Any UI motion is brief, subtle, and respects `prefers-reduced-motion`.
- Exported PDFs preserve readable order, text selection, image alt text where platform-supported, and clean page breaks between finding details.

## Brand asset status

No UXM logo, icon, or approved brand asset was present in the current project workspace when this system was authored. Until supplied, use the text wordmark `UXM` in Manrope 700 with no invented symbol. The visual system is intentionally asset-neutral so the approved UXM mark can be inserted later without structural redesign.
