import type {
  DailyAccuracyResponse,
  ForecastEvolutionResponse,
  OverviewResponse,
  TimeseriesResponse,
} from "./types";

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL ?? "").replace(/\/$/, "");

async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: { Accept: "application/json" },
  });
  if (!response.ok) {
    throw new Error(`API request failed with status ${response.status}`);
  }
  return response.json() as Promise<T>;
}

function rangeQuery(from: string, to: string): string {
  return new URLSearchParams({ from, to }).toString();
}

export function fetchOverview(from: string, to: string) {
  return getJson<OverviewResponse>(`/api/v1/overview?${rangeQuery(from, to)}`);
}

export function fetchTimeseries(from: string, to: string) {
  return getJson<TimeseriesResponse>(`/api/v1/timeseries?${rangeQuery(from, to)}`);
}

export function fetchDailyAccuracy(from: string, to: string) {
  return getJson<DailyAccuracyResponse>(`/api/v1/daily-accuracy?${rangeQuery(from, to)}`);
}

export function fetchForecastEvolution(startTime: string) {
  const query = new URLSearchParams({ startTime }).toString();
  return getJson<ForecastEvolutionResponse>(`/api/v1/forecast-evolution?${query}`);
}
