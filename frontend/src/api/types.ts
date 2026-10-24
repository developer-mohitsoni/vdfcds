export interface Period {
  from: string;
  to: string;
}

export interface Metrics {
  maeMw: number | null;
  rmseMw: number | null;
  meanBiasMw: number | null;
  wapePercent: number | null;
  p90AbsoluteErrorMw: number | null;
  expectedHours: number;
  completeHours: number;
  coveragePercent: number;
}

export interface DataStatus {
  status: "ready" | "stale";
  generatedAt: string;
  schemaVersion: string;
  completeHours: number;
}

export interface OverviewResponse {
  period: Period;
  metrics: Metrics;
  dataStatus: DataStatus;
}

export interface TimeseriesPoint {
  startTime: string;
  forecastMw: number | null;
  actualMw: number | null;
  errorMw: number | null;
  forecastPublishTime: string | null;
  decisionCutoff: string;
}

export interface TimeseriesResponse {
  period: Period;
  points: TimeseriesPoint[];
}

export interface DailyMetric {
  date: string;
  metrics: Metrics;
}

export interface DailyAccuracyResponse {
  period: Period;
  days: DailyMetric[];
}

export interface EvolutionRevision {
  publishTime: string;
  generationMw: number;
  eligibleAtCutoff: boolean;
  selected: boolean;
}

export interface ForecastEvolutionResponse {
  startTime: string;
  decisionCutoff: string;
  selectedPublishTime: string | null;
  selectedForecastMw: number | null;
  actualMw: number | null;
  revisions: EvolutionRevision[];
}
