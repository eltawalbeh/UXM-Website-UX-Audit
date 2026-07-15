# UXM Audit — Asset Register

## Current status

No approved UXM brand assets were found inside this project workspace when Task 2 was completed. The interface must therefore use a text-only `UXM` wordmark until supplied; do not invent an icon, logo mark, or client logo.

## Required UXM source assets

| Asset | Preferred format | Required use |
|---|---|---|
| UXM primary logo | SVG + transparent PNG fallback | Report cover, closing page, workspace header |
| UXM monochrome logo | SVG | Small contexts, print, dark/light surfaces |
| UXM favicon/app mark | SVG/PNG | Local application and browser tab |
| Approved brand font license/files, if not web-hosted | WOFF2 | Optional replacement for the documented font system |
| Brand photography/illustration direction | Reference images or a short brief | Cover and section-divider visuals only |

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
