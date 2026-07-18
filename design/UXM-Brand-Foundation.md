# UXM Brand Foundation — Stage 1

**Status:** Source assets received and foundation locked for design exploration
**Brand:** UX Mosaic
**Product:** UXM Audit
**Descriptor:** Evidence-led UX Audit System
**Languages:** English-first with complete Arabic RTL from the same design system

## 1. Brand architecture

Use the supplied **UX Mosaic** logo unchanged as the corporate endorsement. The audit product is named **UXM Audit** in navigation, page titles, and product communication.

Recommended lockup in product and marketing contexts:

```text
[UX MOSAIC LOGO]
EVIDENCE-LED UX AUDIT SYSTEM
```

The descriptor is live text placed beside or below the logo; it is not baked into or used to redraw the supplied logo artwork. Short contexts may use `UX AUDIT SYSTEM`. The standalone name `UXM Audit` is used for app navigation and browser titles.

## 2. Supplied logo system

| Asset | Dimensions | Intended use |
|---|---:|---|
| `uxmosaic-horizontal-dark.png` | 1630×256 | Light surfaces, desktop headers, report covers |
| `uxmosaic-horizontal-light.png` | 1630×256 | Dark surfaces, public-site hero/footer, login |
| `uxmosaic-vertical-dark.png` | 1090×485 | Light compact/stacked contexts and formal report compositions |
| `uxmosaic-vertical-light.png` | 1090×485 | Dark compact/stacked contexts and formal report compositions |

All four PNGs have transparent backgrounds and full-resolution alpha. Preserve proportions and transparent padding. Do not recolor, stretch, add effects, or detach the blue `O`/underline device.

### Logo color note

The supplied logo files use black or white lettering with an embedded blue of approximately `#4175B9`. The supplied palette identifies `#007AFF` as the digital primary blue. Preserve `#4175B9` inside the supplied logo assets; use `#007AFF` as the product interaction/accent blue. Do not recolor the logo until an official vector master explicitly replaces these exports.

## 3. Brand palette

Source: supplied brand palette reference.

| Token | Source value | Role |
|---|---:|---|
| `brand-slate` | `#607D8B` | Supporting brand field, calm metadata, illustrations; not small text on white |
| `brand-blue` | `#007AFF` | Primary interaction, selected state, links, focus, product emphasis |
| `brand-midnight` | `#1B1C2F` | Main dark brand surface and high-contrast text |
| `brand-charcoal` | `#343936` | Secondary dark neutral, quiet supporting surfaces |
| `brand-mint` | `#A5F3B2` | Positive emphasis, evidence-ready state, highlighted editorial moments |
| `logo-blue` | `#4175B9` | Embedded logo artwork only unless an official vector source states otherwise |

### Verified contrast constraints

| Pair | Contrast | Usage decision |
|---|---:|---|
| `#1B1C2F` on white | 16.75:1 | Primary text, headings, dense UI |
| `#343936` on white | 11.77:1 | Secondary dark text |
| `#A5F3B2` on `#1B1C2F` | 12.81:1 | Positive callout or highlighted dark-surface text |
| `#007AFF` on white | 4.02:1 | Not normal body text; use for large text, controls, focus, decoration |
| `#007AFF` on `#1B1C2F` | 4.17:1 | Not normal body text; use with large/bold treatment or non-text UI |
| `#607D8B` on white | 4.37:1 | Not normal body text; use for large text, borders, icons, surfaces |
| supplied `#4175B9` logo blue on white | 4.70:1 | Suitable within the supplied logo artwork |

Additional accessible text/link variants will be derived during token implementation rather than silently changing the supplied source palette.

## 4. Pattern language

The supplied mosaic pattern is a sequence of modular quarter-circle and arch forms. It expresses the brand idea: individual research, strategy, design, and technology pieces forming one coherent experience.

Use it as a structural brand device:

- full-width transition band between major public-site sections;
- cropped corner/edge composition on login and report cover;
- restrained section divider or empty-state illustration;
- optional print-cover geometry.

Do not use it as wallpaper behind dense text, in every card, or as repeated decoration inside the operator workspace. The system UI should inherit its geometry through subtle corner shapes, section rhythm, and cropped boundaries—not become a pattern gallery.

## 5. Typography direction

### Primary family

Use the supplied **Thmanyah Sans** family as the distinctive bilingual product family, subject to visual testing in real English and Arabic layouts.

Included weights:

- 400 Regular
- 500 Medium
- 700 Bold
- 900 Black

### Fallbacks

```css
font-family: "Thmanyah Sans", "IBM Plex Sans Arabic", "Manrope", Arial, sans-serif;
```

### Usage

- Public website hero/editorial headings: Thmanyah Sans 700/900.
- Navigation, labels, product UI: Thmanyah Sans 500/700.
- Long report and evidence descriptions: Thmanyah Sans 400; IBM Plex Sans Arabic remains the Arabic fallback if reading tests show an issue.
- Technical IDs, URLs, dates, and file names: isolated LTR spans; no artificial Arabic letter spacing.

Do not introduce the supplied serif families in Stage 1. UXM needs one confident typographic voice before any editorial accent family is considered.

## 6. Visual direction

**Design read:** UX Mosaic’s regional, modular brand translated into a precise enterprise audit product. The public website may be expressive and pattern-led; the operator system is calm and disciplined; the client report is editorial and evidence-led.

### Keep from the existing UX Mosaic site

- dark midnight fields contrasted with clean light sections;
- bold, direct typography;
- mosaic geometry as a recognizable brand signature;
- blue and mint as deliberate emphasis;
- English-first structure with regional/MENA credibility.

### Improve for the audit product

- reduce all-caps usage in long interface labels;
- replace generic card grids with stronger editorial hierarchy and task-oriented lists;
- use evidence images and audit status—not decorative metrics—as the visual hero;
- create a quieter operator shell than the marketing website;
- design Arabic RTL independently and test mixed-script metadata;
- use tighter, more sophisticated spacing and fewer oversized rounded containers.

## 7. Surface-specific expression

| Surface | Brand intensity | Visual behavior |
|---|---:|---|
| Public website | High | Dark/light editorial rhythm, bold statements, pattern bands, real product imagery |
| Login | Medium | Focused split or framed composition with one cropped pattern moment |
| Operator system | Low | Midnight/white foundations, compact blue actions, mint only for verified-ready states |
| Client portal | Medium-low | Calm overview, clear published status, report/PDF access, no internal operational complexity |
| Client report/PDF | Medium | Evidence-led editorial pages, restrained brand cover/dividers, high legibility |

## 8. Content placeholders

Client logos, testimonials, named case studies, and outcome metrics remain intentionally empty until approved content is supplied. The design may reserve flexible modules labelled internally as placeholders, but the public prototype must not display fake logos, invented organizations, fabricated metrics, or lorem ipsum.

Safe temporary public copy:

- `Selected work available on request`
- `Client stories coming soon`
- `Evidence-led audits for government, corporate, and digital-service teams`

## 9. Source files retained in the project

```text
design/assets/brand/source/
├── brand-palette-reference.png
├── logo-composition-reference.png
├── mosaic-pattern-source.png
├── uxmosaic-horizontal-dark.png
├── uxmosaic-horizontal-light.png
├── uxmosaic-vertical-dark.png
└── uxmosaic-vertical-light.png

design/assets/fonts/thmanyah-sans/
├── thmanyah-sans.css
├── thmanyahsans-Regular.woff2
├── thmanyahsans-Medium.woff2
├── thmanyahsans-Bold.woff2
└── thmanyahsans-Black.woff2
```

## 10. Immediate Stage 1 deliverables

1. Apply this brand foundation to the master design tokens.
2. Produce the complete product information architecture and visual blueprint for public site, login, operator system, client portal, and report.
3. Build a verified bilingual typography specimen using Thmanyah Sans.
4. Produce first-direction compositions for the public website, operator workspace, and client report.
5. Review the direction visually before bulk implementation.
