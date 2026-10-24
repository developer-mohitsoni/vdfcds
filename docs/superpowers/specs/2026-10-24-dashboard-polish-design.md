# WindSight UK Dashboard Polish Design

## Intent

Refine the existing dashboard into a clearer operational analytics surface without redesigning its wind-specific identity. Preserve the cream canvas, teal/amber palette, editorial serif headings, data methodology, API behavior, and single-page information flow.

## Approved approach

Use focused operational polish. This is narrower and safer than a visual redesign, while addressing every priority issue in the saved Impeccable critique.

## Interaction design

- Keep the January range form, but show an inline explanation when the date range is invalid.
- When a daily row is focused, show an explicit active-filter notice with a “Back to January” action. The daily action is a labelled 44px button, not an ambiguous arrow.
- Replace the 744-option delivery-hour selector with separate delivery-day and delivery-hour controls, plus previous/next-hour buttons. Controls operate only on timestamps present in the loaded range.
- Forecast-evolution loading and error states use live semantics. The error state includes a retry action.
- Replace the 744-item screen-reader chart list with a concise chart summary containing the visible period, point count, and selected-hour values.

## Information design

- Reduce hero type and vertical spacing so the KPI layer appears sooner.
- Add concise, visible definitions to the five expert accuracy metrics; coverage retains its observed-hours explanation.
- Use GMT consistently throughout the January view.
- Keep all daily metrics available on mobile through a horizontally scrollable table with a sticky Date column.

## Visual and accessibility rules

- Raise muted-text contrast and the minimum functional-text size.
- Provide authored `:focus-visible` rings, 44px interactive targets, tabular numerals, themed selection, and a restrained scrollbar.
- Preserve the contextual graph-paper background; it is an intentional energy-operations motif.
- Reduced-motion mode removes only the dashboard reveal and skeleton shimmer, rather than globally forcing every animation to 0.01ms.
- Remove unused starter-screen CSS that no longer belongs to the dashboard.

## Verification

Behavior changes are test-first. Verify component tests, the full frontend test suite, lint, typecheck, production build, wide/mobile browser layouts, keyboard interaction, state semantics, console output, and one final Impeccable detector scan.

