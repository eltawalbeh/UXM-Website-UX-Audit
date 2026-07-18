# UXM Figma Design System — Development Source of Truth

**Live file:** `RYgdpeagYxr34nsA8m1Oqe`
**Master page:** `100:2` (`UX Audit - Master`)
**Verified:** 2026-07-19 via Figma Desktop MCP
**Status:** Authoritative for Phase 4.2 and all following frontend slices

## What was verified

The live master page returned **178 active Figma Variables** through `get_variable_defs`. The dedicated Design Development Foundation frames and reusable component sets were then inspected through `get_design_context` and `get_screenshot`.

The generated design context consistently references Figma variables for colors, backgrounds, text, borders, spacing, radii, type scales, line heights, buttons, icons, and status roles. Screen-level implementation must therefore consume the shared token/component layer rather than recreate values per route.

### Foundation nodes

| Foundation | Node |
|---|---:|
| Tokens | `133:262` |
| Typography | `133:349` |
| Components | `133:421` |
| Icons | `133:473` |
| RTL | `133:537` |

### Reusable component sets

| Component | Node | Authoritative variants/states |
|---|---:|---|
| Button | `136:18` | Primary, Secondary, Ghost, Success × Default/Large |
| Badge | `136:35` | Critical, High, Medium, Low, Info, Success, Warning, Neutral |
| Input Field | `136:63` | Default, Focused, Error, Disabled |
| Table Row | `136:114` | Default, Hover, Selected, Header |
| Tab Item | `136:120` | Default, Active |
| Card | `136:167` | Outline, Elevated, Dark |

## Variable inventory

| Namespace | Count | Purpose |
|---|---:|---|
| `color/*` | 40 | Primitive palette |
| `spacing/*` | 23 | Layout spacing |
| `radius/*` | 21 | Component geometry |
| `line-height/*` | 21 | Typography rhythm |
| `type-scale/*` | 19 | Type sizes |
| `button/*` | 8 | Button semantics |
| `brand/*` | 7 | Brand/status roles |
| `letter-spacing/*` | 7 | Type tracking |
| `text/*` | 7 | Text semantics |
| `status/*` | 6 | Feedback backgrounds/text |
| `background/*` | 5 | Surface hierarchy |
| `border/*` | 5 | Default/subtle/focus/error/dark strokes |
| `icon/*` | 5 | Icon color semantics |
| `space/*` | 3 | Component-specific 8/10/14 values |
| `black` | 1 | Primitive black |

## Authoritative core tokens

### Color and surface roles

| Figma variable | Value | Development role |
|---|---:|---|
| `background/dark` | `#1B1C2F` | Primary dark shell |
| `background/dark-secondary` | `#262947` | Secondary dark surface |
| `background/primary` | `#FFFFFF` | Main surface |
| `background/secondary` | `#F7F7F7` | Canvas, selected/hover row |
| `background/surface` | `#F5F5F5` | Disabled/subtle surface |
| `brand/primary` | `#007AFF` | Action, active, selection, focus |
| `brand/primary-muted` | `#4175B9` | Structural/brand-muted blue |
| `brand/success` | `#A5F3B2` | Success/verified state |
| `brand/success-text` | `#155E27` | Text on success |
| `brand/warning` | `#FFBD2E` | Warning/high |
| `brand/error` | `#EF4444` | Error/destructive/critical |
| `text/primary` | `#1A1A1F` | Primary text |
| `text/secondary` | `#343936` | Secondary text |
| `text/tertiary` | `#607D8B` | Metadata/default icons |
| `text/placeholder` | `#9999A6` | Placeholder/disabled text |
| `border/default` | `#DCDCE0` | Inputs and normal controls |
| `border/subtle` | `#E8E8EB` | Cards and table separators |
| `border/focus` | `#007AFF` | Focused input |
| `border/error` | `#EF4444` | Invalid input |

Mint is not a neutral border. Blue is not success. Structural brand blue and interactive blue remain distinct.

### Spacing

The visible foundation scale is:

```text
4xs 4px
3xs 8px
2xs 12px
xs  16px
sm  20px
md  24px
lg  32px
xl  56px
2xl 64px
```

Additional bound spacing variables exist for 1, 2, 3, 6, 10, 14, 28, 40, 48, 80, 96, 112, 120, and 128px use cases. Development must use the generated Figma token layer instead of inventing route-local spacing.

### Radius

Visible foundation radii are `4`, `6`, `8`, `12`, `18`, and `20px`.

- Inputs: `4px`
- Buttons: `6px`
- Cards: `8px`
- Modal/major surface: `12px`
- Large branded containers: `18–20px`
- Badges: `4px`, not pill by default

### Typography

The live Figma file displays Inter/Manrope because Figma did not allow the supplied **Thmanyah Sans** font to be linked. That is a tooling placeholder, not the product typography decision.

**Approved development override:** Thmanyah Sans is the primary font for UI, body, display, marketing, English, and Arabic. Cairo, Inter, and Manrope must not appear in the production font stacks. Arial is the final system fallback only.

| Role | Size / weight | Use |
|---|---|---|
| Display | `40px / Bold` | Landing hero headings, Thmanyah Sans |
| Heading 1 | `28px / Semi Bold` | Page titles |
| Heading 2 | `24px / Semi Bold` | Section headings |
| Heading 3 | `20px / Medium` | Card/subsection titles |
| Body Large | `18px / Regular` | Lead text |
| Body | `16px / Regular` | Default body |
| Body Small | `14px / Regular` | Secondary descriptions |
| Caption | `13px / Regular` | Labels, metadata, table cells |
| Overline | `12px / Medium` | Tags, badges, timestamps |
| Micro | `11px / Regular` | Footnotes/status text |

## Component contracts

### Button

- Default: `160 × 41px`; Large: `200 × 49px`.
- Horizontal padding `20px`; vertical padding `10px`; radius `6px`.
- Default type `14px Semi Bold`; large type `16px Semi Bold`.
- Variants: Primary blue, Secondary white, Ghost outlined, Success mint.

### Badge

- Padding `3px 10px`; radius `4px`; `12px Semi Bold`.
- Critical red/white; High and Warning amber/dark; Medium blue/white; Low and Success mint/green; Info gray/dark; Neutral slate/white.

### Input

- Nominal component width `400px`, responsive max-width `100%` in development.
- Control height `44px`, padding `10px 12px`, radius `4px`.
- Default: 1px default border.
- Focused: 2px blue border.
- Error: red border plus 12px error message.
- Disabled: `background/surface` plus placeholder color.

### Table row

- States: Default, Hover, Selected, Header.
- Horizontal padding `16px`, vertical padding `14px`, subtle bottom border.
- Hover/Selected/Header use `background/secondary`.
- Header uses 11px Semi Bold uppercase with `0.44px` tracking.

### Tab

- Default: 14px Medium tertiary.
- Active: 14px Semi Bold blue with 2px blue indicator.
- Padding `4px`, logical layout direction.

### Card

- Padding `20px`; radius `8px`.
- Outline: white + subtle border.
- Elevated: white + `0 2px 4px rgba(0,0,0,.06)`.
- Dark: dark background + dark border + inverse text.

## Icon contract

- 24×24 drawing grid; 2px stroke; soft 1.5px corner treatment.
- Supported rendered sizes: 16, 20, 24, 32px.
- Neutral `#607D8B`; interactive `#007AFF`; error `#EF4444`; success `#155E27`; on-dark white.
- Mirror in RTL: arrows, back/forward, chevrons, external link, logout, sidebar collapse.
- Do not mirror: search, settings, bell, check, download/upload, user/avatar.

## RTL contract

- Sidebar moves to the right.
- Content and table column order follow RTL.
- Labels align right; validation icons change side.
- Numbers, URLs, IDs, code, dates, and filenames remain isolated LTR.
- Logical CSS properties are mandatory.
- Progress flows from the right.
- Evidence screenshots and the UX Mosaic logo are never mirrored.

## Development mapping

- Exact variable snapshot: `prototype/src/ui/figma-variables.json`
- Generated CSS namespace: `prototype/src/ui/figma-tokens.css`
- Stable product aliases: `prototype/src/ui/tokens.css`
- Shared primitives: `prototype/src/ui/components.css`
- Font/RTL foundation: `prototype/src/ui/base.css`
- Icon set: `prototype/src/ui/icons.js`
- Browser specimen: `prototype/design-system.html`
- Contract tests: `prototype/tests/design-system.test.js`

Future routes must use these shared files. A route may compose components, but it must not redefine the token values or create a parallel local design system.

Typography is the deliberate exception to the literal Figma font-family labels: Figma geometry, weights, sizes, and line heights remain authoritative, while the rendered family is always Thmanyah Sans.
