import { useQuery } from "@tanstack/react-query";
import { useMemo } from "react";
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
  const selectedIndex = points.findIndex((point) => point.startTime === selectedTime);
  const selectedDay = selectedTime?.slice(0, 10) ?? points[0]?.startTime.slice(0, 10) ?? "";
  const days = useMemo(() => Array.from(new Set(points.map((point) => point.startTime.slice(0, 10)))), [points]);
  const dayPoints = points.filter((point) => point.startTime.startsWith(selectedDay));

  function selectDay(day: string) {
    const firstPoint = points.find((point) => point.startTime.startsWith(day));
    if (firstPoint) onSelect(firstPoint.startTime);
  }

  return (
    <section className="panel evolution-panel">
      <div className="panel-heading">
        <div><p className="section-index">03 / Decision trail</p><h2>Forecast evolution</h2><p>See what changed before—and after—the purchasing cutoff.</p></div>
        <div className="delivery-controls">
          <label className="delivery-select">
            <span>Delivery day</span>
            <select aria-label="Delivery day" value={selectedDay} onChange={(event) => selectDay(event.target.value)}>
              {days.map((day) => <option key={day} value={day}>{new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", timeZone: "UTC" }).format(new Date(`${day}T00:00:00Z`))}</option>)}
            </select>
          </label>
          <label className="delivery-select">
            <span>Delivery hour</span>
            <select aria-label="Delivery hour" value={selectedTime ?? ""} onChange={(event) => onSelect(event.target.value)}>
              {dayPoints.map((point) => <option key={point.startTime} value={point.startTime}>{new Intl.DateTimeFormat("en-GB", { hour: "2-digit", minute: "2-digit", hourCycle: "h23", timeZone: "UTC" }).format(new Date(point.startTime))} GMT</option>)}
            </select>
          </label>
          <div className="hour-stepper">
            <button type="button" aria-label="Previous delivery hour" disabled={selectedIndex <= 0} onClick={() => onSelect(points[selectedIndex - 1].startTime)}>Previous</button>
            <button type="button" aria-label="Next delivery hour" disabled={selectedIndex < 0 || selectedIndex >= points.length - 1} onClick={() => onSelect(points[selectedIndex + 1].startTime)}>Next</button>
          </div>
        </div>
      </div>
      {evolutionQuery.isPending ? <div className="inline-loading" role="status">Loading revision history…</div> : null}
      {evolutionQuery.isError ? <div className="inline-error" role="alert" aria-label="Revision history error"><span>Revision history is unavailable.</span><button type="button" onClick={() => void evolutionQuery.refetch()}>Retry revision history</button></div> : null}
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
