# WindSight UK Design System

## Product character

WindSight UK is an evaluator-first energy intelligence product, not a generic admin dashboard. Its visual world is a **North Sea forecast briefing**: operational, evidence-led, calm, and explicit about what was knowable at the purchasing cutoff.

The primary reading path is:

1. What period and decision rule are being evaluated?
2. How large was the typical miss?
3. Where did forecast and actual generation diverge?
4. Which delivery days drove the result?
5. Which forecast revision was valid at the decision time?
6. How was the analysis constructed?

## Foundations

### Typography

- Family: self-hosted `IBM Plex Sans Variable`, with `Segoe UI` and `sans-serif` fallbacks.
- Headings use moderate weights (approximately 540–580), tight tracking, and sentence case.
- Labels use 650–750 weight only when they describe a control or compact metric.
- Numbers use tabular figures wherever comparison matters.
- Avoid repeated uppercase eyebrow labels, decorative numbering, oversized display type, and gradient text.

### Semantic colour roles

| Role | Token | Value | Usage |
| --- | --- | --- | --- |
| North Sea shell | `--navy-950` | `#071a25` | App chrome, methodology ground |
| Evidence panel | `--navy-900` | `#0b2330` | Decision evidence card |
| Actual / ink | `--ink` | `#102531` | Primary text and actual-generation series |
| Fog ground | `--fog` | `#eaf0f1` | Main page field |
| Paper surface | `--paper` | `#f8fbfa` | Analytical panels and table cells |
| Forecast / ready | `--wind` | `#0d8d84` | Forecast series, primary action, lead metric |
| Forecast highlight | `--wind-bright` | `#3bc1b1` | Live-data indicator |
| Cutoff / risk | `--cutoff` | `#e99138` | D-1 cutoff, selected revision, risk emphasis |
| Muted text | `--muted` | `#52656d` | Supporting copy |
| Structure | `--line` | `#cdd9db` | Dividers and panel borders |

Amber is reserved for decision-time cutoff and risk. Teal means forecast, readiness, or the primary analytical action. Do not introduce arbitrary accent colours.

### Shape, spacing, and depth

- Content width: up to `1420px`, with responsive outer gutters.
- Main vertical rhythm: `1.15rem` between analytical sections.
- Panels: `14px` radius, restrained one-pixel borders, low-contrast shadow.
- Controls: `8px` radius and at least `44px` height.
- Status pills may be fully rounded; analytical cards should not be.
- Depth communicates hierarchy, not decoration. Avoid glass, glow, floating icon tiles, and nested card stacks.

## Composition

### Header and review context

The sticky navy header carries the product mark, section anchors, and data readiness. The opening review block states the evaluation question, January 2026 scope, Elexon sources, date range, and the no-hindsight rule. The amber `D-1 · 09:50 GMT` treatment is the product's signature reference and must remain visually consistent.

### Metrics

MAE is the lead metric on a teal field. RMSE, bias, WAPE, P90 absolute error, and coverage form a quieter comparison rail. Do not render six equivalent KPI cards; the visual hierarchy must communicate which number answers the headline question.

### Charts

- Forecast: teal `#0d8d84`.
- Actual: ink navy `#102c3a`.
- Decision cutoff / selected revision: amber `#e99138`.
- Grid lines are sparse, horizontal, and analytical—not a decorative page texture.
- Tooltips expose timestamp, forecast, actual, signed error, and publication time.
- Chart animation is disabled; the data should read as evidence, not spectacle.

### Daily accuracy table

The desktop table is dense and comparison-oriented. On narrow screens it scrolls horizontally while both Date and Focus day stay pinned, so the promised drill-down action remains discoverable. Sticky cells retain opaque paper backgrounds and a subtle separator shadow.

### Forecast evolution

The evolution panel uses an amber top rule to connect it to the cutoff convention. Delivery day/hour controls precede the revision chart. The dark evidence card states selected forecast, publication time, cutoff, and actual generation without implying that post-cutoff knowledge informed accuracy.

### Methodology

Methodology closes the evidence chain on a navy surface. Use plain descriptive headings—Decision-time forecast, Comparable actuals, Honest gaps—without decorative indices or repeated eyebrow labels.

## Responsive behaviour

- At `1180px`, the review header stacks and the KPI lead separates from its metric rail.
- At `900px`, header navigation becomes horizontally scrollable, metrics reflow, and methodology becomes single-column.
- At `640px`, controls stack, metrics become two columns, panels tighten, and evolution controls become one column.
- Mobile section navigation keeps a visible thin scrollbar and `44px` touch targets.
- The page must never create viewport-level horizontal overflow; only the daily table owns horizontal scrolling.

## Interaction and accessibility

- Every interactive control has a visible focus ring using the cutoff colour.
- Date validation, loading, empty, stale-data, API error, and revision error states remain explicit.
- Reduced-motion preference disables entrance and shimmer animations.
- Navigation uses real anchors and sections expose meaningful labels/headings.
- Colour is not the only carrier of meaning; labels and signed values remain present.

## Guardrails

Do not add stock imagery, decorative illustrations, gradient text, glassmorphism, generic icon cards, tiled line-grid backgrounds, ornamental statistics, repeated uppercase kickers, or equal-weight card collections. New UI should strengthen the decision-time evidence chain and preserve the forecast/actual/cutoff semantics before adding visual novelty.
