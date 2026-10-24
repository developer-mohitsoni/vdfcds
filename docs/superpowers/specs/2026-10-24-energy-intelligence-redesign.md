# WindSight UK Energy Intelligence Redesign

## Product and audience

WindSight UK is a public Full-Stack Software Engineer challenge for a hiring evaluator. The evaluator must understand four things quickly: the problem, the no-hindsight mechanism, the analytical evidence, and the quality of the implementation.

The dashboard remains an Operate surface. It must be immediately usable as an analytics product, while its structure tells a coherent engineering story.

## Direction contract

### World — North Sea Forecast Briefing

The visual system draws from UK offshore-energy reporting, marine forecast publications, and clean infrastructure intelligence. It is not a trading-terminal costume and not a marketing landing page.

- Deep North Sea navy forms the navigation shell and evidence anchors.
- Fog-white and cool mineral surfaces carry dense analytical content.
- Wind teal identifies forecasts and valid/ready states.
- Ink navy identifies actual generation and primary text.
- Cutoff amber is reserved for the D-1 09:50 decision boundary, warnings, and over-forecast risk.
- Fine rules, compact labels, and tabular numerals evoke an authored technical briefing without imitating paper or instrument chrome.

### Typography

Use self-hosted IBM Plex Sans Variable for interface text, headings, controls, and data. Hierarchy comes from weight, width, spacing, and alignment—not a decorative display face. Numeric values use tabular figures.

### First viewport

The first viewport is a working product thesis:

1. Sticky product header with WindSight identity, section navigation, and official-data status.
2. Compact review header: “January wind forecast review”, one-sentence purpose, January range controls, and a visible no-hindsight rule.
3. Evidence summary with one leading MAE measure and an aligned secondary metric rail.
4. The forecast-versus-actual chart begins within the first desktop viewport so the claim is immediately backed by evidence.

### Visitor path

1. Understand what period and decision rule are being evaluated.
2. Read the headline accuracy and bias.
3. Inspect the hourly chart.
4. Focus a delivery day in the daily evidence table.
5. Inspect the forecast revision trail around the cutoff.
6. Verify sources, transformation, error convention, and limitations.

### Signature move — cutoff ribbon

The D-1 09:50 GMT boundary is a consistent amber signal across the product: a concise rule in the overview, the selected-hour reference in performance, and the explicit reference line plus eligibility narrative in Forecast Evolution. It behaves as evidence, not decoration.

### Raised disciplines from the Impeccable concept round

- **Claim → evidence:** every major claim sits directly beside its metric, chart, or methodology proof.
- **Revision route clarity:** Forecast Evolution reads as a progression toward a decision boundary, borrowing the discipline—not the visual costume—of transit wayfinding.
- **Calibrated hierarchy:** data lines, labels, and active states use consistent visual rank rather than arbitrary color.
- **Annotation margin:** methodology and limitations behave like concise technical annotations attached to the evidence they qualify.

### Honest risk

Dark energy dashboards can drift into generic trading-terminal styling. The design avoids that by keeping work areas on calm light surfaces, using standard web controls, and reserving navy for the shell and evidence anchors.

## Information architecture

- Header anchors: Overview, Performance, Daily accuracy, Decision trail, Methodology.
- Overview contains period controls, data provenance, decision rule, and KPI hierarchy.
- Performance contains chart, legend, selected-time context, and accessible summary.
- Daily accuracy keeps every metric available with a clear focus action.
- Decision trail contains day/hour navigation, revision chart, cutoff explanation, and selected-revision evidence.
- Methodology presents the reproducible pipeline: WINDFOR selection, D-1 cutoff, FUELHH hourly aggregation, metric convention, and limitations.

## Responsive behavior

- Wide desktop: compact top navigation, asymmetric overview, one-row metric rail, full analytical width.
- Intermediate: navigation remains usable, overview stacks, metrics form a 3-column grid.
- Mobile: simplified header, horizontal section navigation, single-column overview and metrics, scrollable daily table with sticky Date, stacked evolution controls and evidence card.
- No page-level horizontal overflow at 390px.

## State design

- Loading uses structural skeletons matching the new hierarchy.
- Empty state explains how to choose a valid January range.
- Main API and revision-history failures identify recovery actions.
- Stale data and focused-day filters use distinct, accessible banners.
- Focus, hover, active, disabled, and reduced-motion states follow the same system.

## Constraints

- Preserve all API contracts, calculations, content truth, and current functionality.
- Do not introduce authentication, database persistence, export, ML, trading execution, or fabricated performance claims.
- Do not use stock imagery, decorative illustration, gradient text, glass cards, generic icon tiles, or dashboard-template card repetition.

