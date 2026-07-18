---
version: alpha
name: UXM Audit
license: Proprietary — UX Mosaic
summary: A bilingual evidence-led UX audit operating system rooted in the UX Mosaic brand.
implementationSource: UXM-Figma-Design-System-Source-of-Truth.md
colors:
  midnight: "#1B1C2F"
  midnight-secondary: "#262947"
  charcoal: "#343936"
  slate: "#607D8B"
  blue: "#007AFF"
  mint: "#A5F3B2"
  mint-ink: "#155E27"
  canvas: "#F7F7F7"
  surface: "#FFFFFF"
  surface-dark: "#262947"
  surface-subtle: "#F5F5F5"
  line: "#DCDCE0"
  line-subtle: "#E8E8EB"
  ink: "#1A1A1F"
  ink-muted: "#607D8B"
  link: "#007AFF"
  logo-blue: "#4175B9"
  critical: "#EF4444"
  critical-soft: "#FFF2F2"
  warning: "#FFBD2E"
  warning-soft: "#FFF7EB"
  success-soft: "#EDFCF0"
  annotation: "#EF4444"
typography:
  display:
    fontFamily: "Thmanyah Sans, Arial, sans-serif"
    fontSize: "40px"
    fontWeight: 700
    lineHeight: "44px"
  heading-1:
    fontFamily: "Thmanyah Sans, Arial, sans-serif"
    fontSize: "28px"
    fontWeight: 600
    lineHeight: "31px"
  heading-2:
    fontFamily: "Thmanyah Sans, Arial, sans-serif"
    fontSize: "24px"
    fontWeight: 600
    lineHeight: "32px"
  heading-3:
    fontFamily: "Thmanyah Sans, Arial, sans-serif"
    fontSize: "20px"
    fontWeight: 500
    lineHeight: "27px"
  body-lg:
    fontFamily: "Thmanyah Sans, Arial, sans-serif"
    fontSize: "18px"
    fontWeight: 400
    lineHeight: "28px"
  body-md:
    fontFamily: "Thmanyah Sans, Arial, sans-serif"
    fontSize: "16px"
    fontWeight: 400
    lineHeight: "24px"
  body-sm:
    fontFamily: "Thmanyah Sans, Arial, sans-serif"
    fontSize: "14px"
    fontWeight: 400
    lineHeight: "22px"
  caption:
    fontFamily: "Thmanyah Sans, Arial, sans-serif"
    fontSize: "13px"
    fontWeight: 400
    lineHeight: "20px"
  overline:
    fontFamily: "Thmanyah Sans, Arial, sans-serif"
    fontSize: "12px"
    fontWeight: 500
  micro:
    fontFamily: "Thmanyah Sans, Arial, sans-serif"
    fontSize: "11px"
    fontWeight: 400
rounded:
  xs: "4px"
  sm: "6px"
  md: "8px"
  lg: "12px"
  xl: "20px"
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
  20: "80px"
  24: "96px"
components:
  button-primary:
    backgroundColor: "{colors.blue}"
    textColor: "{colors.surface}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.sm}"
    minSize: "160px 41px"
    padding: "10px 20px"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.midnight}"
    typography: "{typography.body-sm}"
    rounded: "{rounded.sm}"
    minSize: "160px 41px"
    padding: "10px 20px"
  badge:
    typography: "{typography.overline}"
    rounded: "{rounded.xs}"
    padding: "3px 10px"
---

## Overview

**Design read:** UX Mosaic’s regional, modular brand translated into a precise evidence-led audit operating system. The public website is expressive and persuasive, the operator system is calm and operational, the client portal is reassuring and concise, and the client report is editorial and evidence-first.

The system must communicate one product truth without explanation:

```text
AI accelerates discovery.
Humans validate decisions.
Evidence supports findings.
Readiness governs delivery.
```

### Surface archetypes

- **Public website — Decide / Learn:** one product idea per section, strong editorial rhythm, real product imagery when available.
- **Login — Configure:** focused, low-friction, no marketing detour.
- **Operator system — Operate:** queues, selection, state, evidence, and actions dominate; no hero or decorative dashboard.
- **Client portal — Monitor:** published status and deliverables are glanceable; internal audit complexity is absent.
- **Client report — Decide / Learn:** evidence and recommendations form a decision document, not a workspace printout.

### Brand architecture

- Corporate endorsement: supplied **UX Mosaic** logo.
- Product name: **UXM Audit**.
- Descriptor: **Evidence-led UX Audit System**.
- The descriptor is live text. Never redraw or modify the supplied logo to add it.

## Colors

### Source palette

| Token | Value | Role |
|---|---:|---|
| Midnight | `#1B1C2F` | Primary dark brand field and core ink |
| Charcoal | `#343936` | Supporting dark neutral |
| Slate | `#607D8B` | Calm brand field, iconography, non-text structure |
| Blue | `#007AFF` | Brand interaction and selection accent |
| Mint | `#A5F3B2` | Verified-ready emphasis and editorial highlight |
| Logo blue | `#4175B9` | Embedded supplied logo artwork only |

### Bound semantic colors

- `brand/primary #007AFF` is the Figma-bound action, link, focus, selected, and active-navigation color.
- `brand/primary-muted #4175B9` is the structural/brand-muted blue and remains distinct from interaction blue.
- `brand/success #A5F3B2` pairs with `brand/success-text #155E27`.
- `background/secondary #F7F7F7`, `background/surface #F5F5F5`, `border/default #DCDCE0`, and `border/subtle #E8E8EB` are the operational neutral system.

### Semantic color discipline

- Severity always uses written label + rank/icon in addition to color.
- Mint means verified/ready only. It never means “AI confidence” or generic decoration inside the operator system.
- Blue means action/navigation/selection, not success.
- Annotation red identifies the observed evidence location; it does not replace the severity label.
- `Not verified` is neutral and explicitly excluded from score.

## Typography

### Family

Figma shows Inter/Manrope only because Thmanyah Sans could not be linked there. The approved product override is **Thmanyah Sans for every English and Arabic surface**. Cairo, Inter, and Manrope are not production families.

Development stacks:

```css
--uxm-font-ui: "Thmanyah Sans", Arial, sans-serif;
--uxm-font-display: "Thmanyah Sans", Arial, sans-serif;
```

The exact bound scale is Display 40, H1 28, H2 24, H3 20, Body Large 18, Body 16, Body Small 14, Caption 13, Overline 12, and Micro 11px. See `UXM-Figma-Design-System-Source-of-Truth.md`.

### Rules

- Display/heading letter spacing applies to Latin only. Arabic sets `letter-spacing: 0` and uses line-height around 1.65–1.75 for paragraphs.
- Public-site display type may use weight 900. Product and report headings default to 700.
- Avoid all-caps for long navigation or interface labels. Small English eyebrow labels may use restrained uppercase; Arabic never imitates tracking or caps.
- Minimum web body: 16px. Minimum client PDF body: 11pt. Minimum annotation label: 12px / 9pt.
- URLs, issue IDs, file names, browser versions, and ISO dates render in isolated LTR spans.

## Layout

### Shared grid

- Wide web: 12 columns, max width 1440px, outer padding 48px.
- Medium: 8 columns, padding 32px.
- Narrow: 4 columns/single content flow, padding 20px.
- Never create horizontal page scrolling.

### Surface-specific composition

- **Public website:** alternating midnight/light editorial chapters; the mosaic pattern appears at transitions and edges, not behind long text.
- **Operator system:** stable navigation rail + contextual header + flexible work canvas. Audit context remains visible without consuming the entire first viewport.
- **Client portal:** simple account/project hierarchy, published reports first, no internal workflow controls.
- **Report web:** persistent compact context rail at wide widths; it folds into a summary block before content on narrow screens.
- **Report PDF:** A4 landscape, 12-column grid, 20mm safe margin; evidence/prose ratio approximately 60/40.

### Finding detail

- Evidence is the visual hero.
- Wide: evidence canvas 7–8 columns, prose/metadata 4–5 columns using `minmax(0, …)`.
- Narrow: source order is summary → evidence → observation/impact → recommendation → metadata.
- Full-page evidence is only acceptable for hierarchy/scroll/page-level findings. Default to finding-specific crops.

### Directionality

- Arabic shell, navigation, lists, metadata rail, and reading order are RTL.
- Screenshots and coordinates are never mirrored.
- Technical values use `dir="ltr"` and `unicode-bidi: isolate`.

## Elevation & Depth

- Default product/report surfaces use a 1px border, not shadow.
- One restrained shadow is reserved for overlays, popovers, and floating annotation tools: `0 16px 40px rgba(27, 28, 47, 0.12)`.
- Public marketing panels may use a softer ambient shadow only on light sections.
- No glassmorphism, frosted layers, neon glow, or gradient sheen.

## Shapes

- Default controls: 8px radius.
- Dialogs and major report surfaces: 12–20px only when containment is necessary.
- Pills are reserved for statuses, filters, and compact metadata—not every label.
- Mosaic quarter-circle geometry is a brand transition device, not a universal card shape.
- Screenshot annotations use 2px solid/dashed outlines, 4px radius, and 20–24px numbered pins.
- Icons use one rounded 1.75–2px stroke family. Unfamiliar icons require text labels or tooltips.

## Components

### Navigation

- Public navigation: horizontal and restrained; one primary conversion action.
- Operator navigation: role/task-based—Portfolio, Templates, Audits, Deliveries—not feature marketing.
- Client navigation: Projects, Reports, Deliveries, Account.
- Current location must be conveyed by color and structure/text, not color alone.

### Buttons

- One primary action per decision area.
- Midnight is the default high-emphasis action on light surfaces.
- Accessible blue is reserved for product actions and selected contexts.
- Destructive actions require written labels and confirmation.
- Disabled/readiness-blocked actions explain why via adjacent text or tooltip.

### Status and readiness

Distinct written states:

```text
Not scored · Draft · AI candidate · In human review · Evidence pending
Evidence complete · Ready for client · Delivered · Not verified
```

Do not compress score, readiness, completion, and health into one ambiguous badge.

### Evidence frame

- Show the finding-specific annotated crop first.
- Provide source capture access without replacing the crop.
- Include URL/page/journey/capture/device metadata in a compact rail.
- Missing evidence is a visible blocking state, never a generic image placeholder.

### Tooltips and compact actions

- Icon-only actions are permitted only for familiar repeat actions and must have accessible labels, keyboard focus, and tooltips.
- Share, PDF, delivery, and public-link actions obey readiness state.
- Action rails are contextual, not permanently present across every screen.

## Do's and Don'ts

### Do

- Let evidence, state, and next action create hierarchy.
- Carry the existing UX Mosaic midnight/blue/mint/pattern signature into the product with reduced intensity.
- Use real audit content and explicit placeholders; never fabricate clients or metrics.
- Treat English and Arabic as equal designed experiences.
- Keep Critical/High findings visible regardless of aggregate score.
- Separate measured facts, human-approved observations, AI candidates, and not-verified items.

### Don't

- Do not copy UX Audit Pro’s visual identity or unsupported analysis claims.
- Do not use purple AI gradients, glassmorphism, equal card farms, fake heatmaps, fake personas, or decorative numbers.
- Do not print the operator workspace as the client report.
- Do not expose internal drafts, rejected candidates, private evidence, or not-verified checks in the client portal.
- Do not let unapproved AI candidates affect score, readiness, report, PDF, or delivery.
- Do not use the pattern as wallpaper or place it behind dense content.
