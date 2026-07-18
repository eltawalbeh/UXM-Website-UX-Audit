# UXM Figma Final Design Recheck — Node 100:2

**Review mode:** Layout/design only. Placeholder fact data and draft copy intentionally ignored for acceptance; development will replace both with verified production content.

## Confirmed final corrections

- Arabic RTL internal OS labels were translated while IDs, URLs, dimensions, and scores remain LTR tokens.
- Arabic Portfolio relative-time labels and operator-role label were localized.
- English desktop Candidate Review inspector was reflowed horizontally:
  - Header/status no longer overlap.
  - Evidence gaps and duplicate warning have separate full-width rows.
  - Human Notes has its own row.
  - Decision buttons now fit the inspector width.
- How UXM Works retains five dominant public stages with compact secondary detail.
- Hero uses `HUMAN REVIEW STATUS`.
- English/Arabic mobile and tablet directions remain present.

## One remaining design defect

### Desktop Candidate Review — vertical clipping

The inspector panel was expanded from 702px to 848px, but the parent screen remains 900px high. The bottom decision area now fits horizontally but extends below the visible frame.

Observed in the final screenshot:

- The top edges of the decision buttons appear at the bottom boundary.
- The complete Reject / Edit / Promote action row is not visible.
- No visible internal scrollbar or sticky decision footer communicates access to the clipped controls.

### Required correction

Use one of these solutions:

1. Keep the decision bar sticky inside the inspector and make only the content above it scroll.
2. Reduce vertical spacing/content height so the complete footer fits inside the 900px frame.
3. Add a clearly visible internal inspector scrollbar while keeping the decision footer pinned.

Preferred: **sticky decision footer + scrollable inspector body**.

## Final verification — Candidate Vertical Actions

Verified directly from the updated live Figma frame:

- The inspector now has a visible internal scrollbar.
- The decision footer is pinned at the bottom.
- Reject, Edit as Draft Finding, and Promote to Review are fully visible.
- No vertical clipping remains in the action row.

The two labels inside the dark AI observation card are now separated into distinct rows. No touching or overlap remains. The sticky footer and all three decision actions remain fully visible.

## Color system final verification

Verified from the final live Figma frames:

- Neutral Portfolio rows and tables use neutral Slate/gray strokes.
- Selected/action states use interaction blue.
- Published, passed, and verified states retain Mint semantics.
- Candidate Review default panels are neutral; the selected candidate remains blue.
- Delivery Readiness blocked rows are neutral/red rather than Mint.
- Warning, blocked, pending, passed, and active states are visually distinct.
- English and Arabic RTL surfaces preserve the same semantic color system.

The UXM color system is approved.

## Final decision

| Area | Status |
|---|---|
| Product architecture | Pass |
| Public/mobile/RTL surfaces | Pass |
| Arabic internal OS layout | Pass |
| Evidence-first design | Pass |
| Tablet OS layouts | Pass |
| Desktop Candidate inspector width | Pass |
| Desktop Candidate inspector height/actions | Pass |
| Overall design direction | **Approved for development** |

Fact data and final copy remain intentional scaffolding and will be replaced with verified production content during development.
