import { useQuery } from "@tanstack/react-query";
import {
  CartesianGrid,
  Line,
  LineChart,
  ReferenceDot,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import { fetchForecastEvolution } from "../api/client";
import type { TimeseriesPoint } from "../api/types";
import { formatDateTime, formatMw } from "../lib/format";

export function EvolutionPanel({ points, selectedTime, onSelect }: { points: TimeseriesPoint[]; selectedTime: string | null; onSelect: (value: string) => void }) {
  const evolutionQuery = useQuery({
    queryKey: ["forecast-evolution", selectedTime],
    queryFn: () => fetchForecastEvolution(selectedTime!),
    enabled: Boolean(selectedTime),
  });
  const data = evolutionQuery.data;
  const selectedRevision = data?.revisions.find((revision) => revision.selected);

  return (
    <section className="panel evolution-panel">
      <div className="panel-heading">
        <div><p className="section-index">03 / Decision trail</p><h2>Forecast evolution</h2><p>See what changed before—and after—the purchasing cutoff.</p></div>
        <label className="hour-select">
          <span>Delivery hour</span>
          <select aria-label="Delivery hour" value={selectedTime ?? ""} onChange={(event) => onSelect(event.target.value)}>
            {points.map((point) => <option key={point.startTime} value={point.startTime}>{formatDateTime(point.startTime)}</option>)}
          </select>
        </label>
      </div>
      {evolutionQuery.isPending ? <div className="inline-loading">Loading revision history…</div> : null}
      {evolutionQuery.isError ? <div className="inline-error">Revision history is unavailable.</div> : null}
      {data ? (
        <div className="evolution-grid">
          <div className="evolution-chart">
            <ResponsiveContainer width="100%" height={260}>
              <LineChart data={data.revisions} margin={{ top: 20, right: 18, bottom: 8, left: 0 }}>
                <CartesianGrid stroke="#dfe5df" strokeDasharray="2 6" vertical={false} />
                <XAxis dataKey="publishTime" tickFormatter={(value: string) => new Intl.DateTimeFormat("en-GB", { hour: "2-digit", minute: "2-digit", timeZone: "UTC" }).format(new Date(value))} tickLine={false} axisLine={false} minTickGap={24} />
                <YAxis width={42} tickLine={false} axisLine={false} />
                <Tooltip labelFormatter={(value) => formatDateTime(typeof value === "string" ? value : null)} formatter={(value) => [formatMw(Number(value)), "Forecast"]} />
                <ReferenceLine x={data.decisionCutoff} stroke="#d6843d" strokeDasharray="5 4" label={{ value: "09:50 cutoff", fill: "#9b5c27", position: "insideTopRight" }} />
                <Line dataKey="generationMw" name="Forecast revision" stroke="#267b70" strokeWidth={2.5} dot={{ r: 3, fill: "#fff", strokeWidth: 2 }} isAnimationActive={false} />
                {selectedRevision ? <ReferenceDot x={selectedRevision.publishTime} y={selectedRevision.generationMw} r={6} fill="#d6843d" stroke="#fff" strokeWidth={2} /> : null}
              </LineChart>
            </ResponsiveContainer>
          </div>
          <aside className="decision-card">
            <span className="decision-label">Selected revision</span>
            <strong>{formatMw(data.selectedForecastMw)}</strong>
            <dl>
              <div><dt>Published</dt><dd>{formatDateTime(data.selectedPublishTime)}</dd></div>
              <div><dt>Cutoff</dt><dd>{formatDateTime(data.decisionCutoff)}</dd></div>
              <div><dt>Actual</dt><dd>{formatMw(data.actualMw)}</dd></div>
            </dl>
            <p>Only information available by the cutoff contributes to accuracy.</p>
          </aside>
        </div>
      ) : null}
    </section>
  );
}
