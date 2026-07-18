# UXM Audit — Asset Register

## Current status

Approved UX Mosaic logo exports and the Mosaic pattern reference are retained under `design/assets/` and copied into `prototype/assets/`. The development package contains Thmanyah Sans 400/500/700/900 webfonts as the approved family for English and Arabic. The supplied logo artwork remains unchanged; `#4175B9` stays embedded in the logo while `#007AFF` is the Figma-bound product interaction color.

## Approved UXM source assets

| Asset | Location | Required use |
|---|---|---|
| Horizontal light/dark logos | `prototype/assets/brand/uxmosaic-horizontal-*.png` | Public header/footer, operator shell, shared report |
| Vertical light/dark logos | `prototype/assets/brand/uxmosaic-vertical-*.png` | Compact and formal report compositions |
| Mosaic pattern source | `prototype/assets/brand/mosaic-pattern-source.png` | Restrained public/login/report brand geometry |
| Thmanyah Sans 400/500/700/900 | `prototype/assets/fonts/thmanyah-sans/` | Approved primary typography for all English and Arabic surfaces |

## Per-audit client assets

| Asset | Required? | Notes |
|---|---|---|
| Client logo | Optional | SVG/PNG, applied only to cover/report identification |
| Website screenshots | Required for published findings | Original capture plus immutable annotated derivative |
| Website URL and product name | Required | Must be verified at audit creation |
| Screenshot alt descriptions | Required | Stored with evidence, not added manually in a PDF later |

## File naming

```text
assets/brand/uxm-logo-primary.svg
assets/brand/uxm-logo-mono.svg
assets/clients/<client-slug>/logo.svg
assets/evidence/<audit-id>/UXM-001-source.png
assets/evidence/<audit-id>/UXM-001-annotated.png
```

## Rules

- Keep original screenshot captures immutable; export annotations into a derivative file or structured annotation data.
- Never include a client logo without permission or an audit context.
- Do not place screenshots as decorative filler.
- Every evidence screenshot must retain an accessible text description.
