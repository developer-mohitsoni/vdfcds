import type { DailyMetric } from "../api/types";
import { formatDate, formatLongDate, formatMw, formatPercent } from "../lib/format";

export function DailyTable({ days, onFocusDay }: { days: DailyMetric[]; onFocusDay: (date: string) => void }) {
  return (
    <section className="panel table-panel">
      <div className="panel-heading compact">
        <div><p className="section-index">02 / Daily detail</p><h2>Accuracy by delivery day</h2></div>
        <span className="table-hint">Choose a day for hourly detail</span>
      </div>
      <div className="table-scroll">
        <table>
          <thead><tr><th>Date</th><th>MAE</th><th>Bias</th><th>WAPE</th><th>Coverage</th><th><span className="sr-only">Action</span></th></tr></thead>
          <tbody>
            {days.map((day) => (
              <tr key={day.date}>
                <td><strong>{formatDate(day.date)}</strong></td>
                <td>{formatMw(day.metrics.maeMw)}</td>
                <td className={day.metrics.meanBiasMw && day.metrics.meanBiasMw > 0 ? "positive" : "negative"}>{formatMw(day.metrics.meanBiasMw)}</td>
                <td>{formatPercent(day.metrics.wapePercent)}</td>
                <td>{formatPercent(day.metrics.coveragePercent)}</td>
                <td><button className="row-action" type="button" aria-label={`Focus day — ${formatLongDate(day.date)}`} onClick={() => onFocusDay(day.date)}>Focus day</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
