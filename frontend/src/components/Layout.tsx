import { useEffect, useState } from "react";

import type { Metrics } from "../api/types";
import { formatMw, formatPercent } from "../lib/format";

export const JANUARY_START = "2026-01-01";
export const JANUARY_END = "2026-01-31";

function BrandMark() {
  return (
    <svg viewBox="0 0 48 48" role="img" aria-label="WindSight mark">
      <path d="M7 17.5h20.5c4.2 0 6.5-2.1 6.5-5.1 0-2.8-2.1-4.9-4.8-4.9-2.4 0-4.2 1.4-4.8 3.5" />
      <path d="M5 24h31.5c4.1 0 6.5 2.2 6.5 5.2 0 2.8-2.1 5-4.9 5-2.4 0-4.1-1.3-4.8-3.4" />
      <path d="M8 30.5h14.5c3.8 0 5.9 2 5.9 4.8s-2.1 5.2-5 5.2c-2.3 0-4-1.3-4.6-3.3" />
    </svg>
  );
}

export function Header({ status }: { status?: "ready" | "stale" }) {
  return (
    <header className="site-header">
      <a className="brand" href="#top" aria-label="WindSight UK home">
        <span className="brand-mark"><BrandMark /></span>
        <span>
          <strong>WindSight</strong>
          <small>United Kingdom</small>
        </span>
      </a>
      <div className={`data-badge ${status === "stale" ? "is-stale" : ""}`} role="status" aria-live="polite">
        <span className="pulse" />
        {status === "stale" ? "Snapshot needs refresh" : "Official data ready"}
      </div>
    </header>
  );
}

export function DateRangeControls({
  from,
  to,
  onApply,
}: {
  from: string;
  to: string;
  onApply: (from: string, to: string) => void;
}) {
  const [draftFrom, setDraftFrom] = useState(from);
  const [draftTo, setDraftTo] = useState(to);

  useEffect(() => {
    setDraftFrom(from);
    setDraftTo(to);
  }, [from, to]);

  const isInvalidRange = Boolean(draftFrom && draftTo && draftFrom > draftTo);

  return (
    <form
      className="date-controls"
      onSubmit={(event) => {
        event.preventDefault();
        onApply(draftFrom, draftTo);
      }}
    >
      <label>
        <span>From date</span>
        <input aria-label="From date" aria-describedby={isInvalidRange ? "date-range-error" : undefined} type="date" min={JANUARY_START} max={JANUARY_END} value={draftFrom} onChange={(event) => setDraftFrom(event.target.value)} />
      </label>
      <span className="date-separator" aria-hidden="true">→</span>
      <label>
        <span>To date</span>
        <input aria-label="To date" aria-describedby={isInvalidRange ? "date-range-error" : undefined} type="date" min={JANUARY_START} max={JANUARY_END} value={draftTo} onChange={(event) => setDraftTo(event.target.value)} />
      </label>
      {isInvalidRange ? <p className="date-error" id="date-range-error" role="alert">From date must be on or before To date.</p> : null}
      <button type="submit" disabled={!draftFrom || !draftTo || isInvalidRange}>Apply date range</button>
    </form>
  );
}

export function KpiGrid({ metrics }: { metrics: Metrics }) {
  const cards = [
    ["Mean absolute error", formatMw(metrics.maeMw), "Average size of the hourly miss", "primary"],
    ["Root mean square error", formatMw(metrics.rmseMw), "Typical miss, weighted toward large errors", ""],
    ["Mean bias", formatMw(metrics.meanBiasMw), metrics.meanBiasMw !== null && metrics.meanBiasMw > 0 ? "Average signed error · over-forecast" : "Average signed error · under-forecast", metrics.meanBiasMw !== null && metrics.meanBiasMw > 0 ? "risk" : ""],
    ["WAPE", formatPercent(metrics.wapePercent), "Absolute error as a share of actual output", ""],
    ["P90 absolute error", formatMw(metrics.p90AbsoluteErrorMw), "90% of hourly misses are below this", ""],
    ["Data coverage", formatPercent(metrics.coveragePercent), `${metrics.completeHours} of ${metrics.expectedHours} hours`, "coverage"],
  ];

  return (
    <section className="kpi-grid" aria-label="Forecast accuracy summary">
      {cards.map(([label, value, note, tone]) => (
        <article className={`kpi-card ${tone ? `kpi-${tone}` : ""}`} key={label}>
          <p>{label}</p><strong>{value}</strong><span>{note}</span>
        </article>
      ))}
    </section>
  );
}

export function LoadingState() {
  return (
    <div className="loading-layout" data-testid="dashboard-loading" role="status" aria-label="Loading dashboard">
      <div className="skeleton hero-skeleton" />
      <div className="skeleton-row">{Array.from({ length: 6 }, (_, index) => <div className="skeleton card-skeleton" key={index} />)}</div>
      <div className="skeleton chart-skeleton" />
    </div>
  );
}

export function StatePanel({ type, onRetry }: { type: "empty" | "error"; onRetry?: () => void }) {
  const isError = type === "error";
  return (
    <section className="state-panel" role={isError ? "alert" : "status"} aria-label={isError ? "API error" : "No data"}>
      <span className="state-icon">{isError ? "!" : "∅"}</span>
      <div>
        <h2>{isError ? "Unable to load dashboard data" : "No observations in this range"}</h2>
        <p>{isError ? "The analytics service did not respond. Check the backend and try once more." : "Choose another January date range to inspect available wind records."}</p>
      </div>
      {onRetry ? <button type="button" onClick={onRetry}>Try again</button> : null}
    </section>
  );
}

export function Methodology() {
  return (
    <section className="methodology">
      <div><p className="section-index">Methodology</p><h2>Built for the decision that was actually possible.</h2></div>
      <div className="method-grid">
        <article><span>01</span><h3>Decision-time forecast</h3><p>Latest WINDFOR revision published by D-1 at 09:50 GMT—never hindsight.</p></article>
        <article><span>02</span><h3>Comparable actuals</h3><p>Two FUELHH WIND half-hours averaged into each hourly observation.</p></article>
        <article><span>03</span><h3>Honest gaps</h3><p>Missing observations stay missing and are excluded from accuracy metrics.</p></article>
      </div>
      <details>
        <summary>Limitations and interpretation</summary>
        <p>Elexon wind generation covers metered wind visible to the system operator. Positive error means over-forecast; negative error means under-forecast. This dashboard evaluates forecast quality—it does not recommend or execute trades.</p>
      </details>
    </section>
  );
}
