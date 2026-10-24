# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

The primary audience is a hiring evaluator reviewing a Full-Stack Software Engineer challenge. They need to understand the product purpose, analytical integrity, UX quality, and engineering judgment quickly, without losing access to the underlying operational detail.

## Product Purpose

WindSight UK compares January 2026 Great Britain day-ahead wind-generation forecasts with actual generation. It shows forecast accuracy and decision-time risk using only the forecast information that was available before the purchasing cutoff.

Success means an evaluator can identify the problem, trust the methodology, inspect the evidence, and recognise a production-quality full-stack implementation within one guided dashboard experience.

## Positioning

The product evaluates the forecast that was genuinely actionable at D-1 09:50 GMT rather than selecting revisions with hindsight. This decision-time constraint is the product's defining mechanism.

## Operating Context

The dashboard is a public hiring-challenge deliverable and an analytical product demonstration. The primary flow moves from high-level forecast quality, through hourly and daily evidence, into the forecast revision trail and the exact data methodology.

## Capabilities and Constraints

- January 2026 only, with 744 expected hourly periods.
- Official Elexon WINDFOR forecasts and FUELHH WIND actuals.
- Forecast cutoff is D-1 at 09:50 GMT.
- Error convention is forecast minus actual; positive error means over-forecast.
- Metrics are MAE, RMSE, mean bias, WAPE, P90 absolute error, and data coverage.
- Existing date filtering, daily focus, forecast evolution, loading, empty, stale-data, and API-error behavior must remain functional.
- React with TypeScript frontend; FastAPI backend; versioned snapshot; no database.
- Authentication, CSV export, heatmaps, ML forecasting, and trading execution remain outside v1.

## Brand Commitments

- Product name: WindSight UK.
- Voice: concise, analytical, credible, and explicit about limitations.
- The interface must feel specific to UK wind forecast intelligence, not like a generic dashboard template.
- The approved direction is an evaluator-first Energy Intelligence Product: technical enough to be credible, but structured as a clear product and engineering story.

## Evidence on Hand

- A reproducible January 2026 Elexon snapshot and provenance metadata in `data/processed/`.
- Backend analytics endpoints and tests covering cutoff selection, hourly aggregation, metrics, validation, and snapshot behavior.
- Frontend tests covering metrics, filters, daily focus, revision selection, loading, empty, and error states.
- No customer testimonials, commercial claims, trading outcomes, or proprietary benchmark data; future work must not fabricate them.

## Product Principles

1. Prove the no-hindsight mechanism before adding decoration.
2. Make analytical evidence scannable without hiding its definitions or limitations.
3. Let the evaluator see both product thinking and engineering rigor.
4. Preserve honest gaps and explicit data provenance.
5. Prefer project-specific energy intelligence language over generic SaaS conventions.

## Accessibility & Inclusion

The dashboard must remain keyboard-operable, screen-reader legible, responsive from 390px mobile through wide desktop, and compliant with WCAG AA contrast and target-size expectations.

