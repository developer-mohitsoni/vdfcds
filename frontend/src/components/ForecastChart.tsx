import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { TimeseriesPoint } from "../api/types";
import { formatDateTime, formatMw } from "../lib/format";

interface TooltipPayload {
  payload?: TimeseriesPoint;
}

function ForecastTooltip({ active, payload }: { active?: boolean; payload?: TooltipPayload[] }) {
  const point = payload?.[0]?.payload;
  if (!active || !point) return null;
  return (
    <div className="chart-tooltip">
      <strong>{formatDateTime(point.startTime)}</strong>
      <span><i className="swatch forecast" />Forecast {formatMw(point.forecastMw)}</span>
      <span><i className="swatch actual" />Actual {formatMw(point.actualMw)}</span>
      <span>Error {formatMw(point.errorMw)}</span>
      <small>Published {formatDateTime(point.forecastPublishTime)}</small>
    </div>
  );
}

export function ForecastChart({ points, selectedTime }: { points: TimeseriesPoint[]; selectedTime: string | null }) {
  const selectedPoint = points.find((point) => point.startTime === selectedTime);
  const firstPoint = points[0];
  const lastPoint = points.at(-1);

  return (
    <section className="panel chart-panel" id="performance" aria-label="Forecast performance">
      <div className="panel-heading">
        <div>
          <h2>Forecast vs actual</h2>
          <p>Hourly wind generation available at the day-ahead decision point.</p>
        </div>
        <span className="chart-unit">MW · GMT</span>
      </div>
      <div className="chart-wrap" aria-label="Hourly forecast and actual wind generation chart">
        <ResponsiveContainer width="100%" height={360}>
          <LineChart data={points} margin={{ top: 16, right: 12, bottom: 4, left: 0 }}>
            <CartesianGrid stroke="#d8e2e4" strokeDasharray="2 6" vertical={false} />
            <XAxis
              dataKey="startTime"
              tickFormatter={(value: string) => new Intl.DateTimeFormat("en-GB", { day: "numeric", month: "short", timeZone: "UTC" }).format(new Date(value))}
              minTickGap={44}
              tickLine={false}
              axisLine={false}
            />
            <YAxis tickFormatter={(value: number) => `${Math.round(value / 1000)}k`} width={42} tickLine={false} axisLine={false} />
            <Tooltip content={<ForecastTooltip />} />
            <Legend iconType="plainline" />
            {selectedTime ? <ReferenceLine x={selectedTime} stroke="#e99138" strokeDasharray="4 4" /> : null}
            <Line name="Forecast" dataKey="forecastMw" stroke="#0d8d84" strokeWidth={2.5} dot={false} activeDot={{ r: 5, fill: "#fff", strokeWidth: 3 }} connectNulls={false} isAnimationActive={false} />
            <Line name="Actual" dataKey="actualMw" stroke="#102c3a" strokeWidth={2.25} dot={false} activeDot={{ r: 5, fill: "#fff", strokeWidth: 3 }} connectNulls={false} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
      <p className="sr-only" aria-label="Chart data summary">
        {points.length} hourly observations from {formatDateTime(firstPoint?.startTime ?? null)} to {formatDateTime(lastPoint?.startTime ?? null)}.
        {selectedPoint ? ` Selected hour: ${formatMw(selectedPoint.forecastMw)} forecast, ${formatMw(selectedPoint.actualMw)} actual, ${formatMw(selectedPoint.errorMw)} error.` : ""}
      </p>
    </section>
  );
}
