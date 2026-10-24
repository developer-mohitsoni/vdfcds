import { QueryClient, QueryClientProvider, useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState } from "react";

import { fetchDailyAccuracy, fetchOverview, fetchTimeseries } from "./api/client";
import { DailyTable } from "./components/DailyTable";
import { EvolutionPanel } from "./components/EvolutionPanel";
import { ForecastChart } from "./components/ForecastChart";
import {
  DateRangeControls,
  Header,
  JANUARY_END,
  JANUARY_START,
  KpiGrid,
  LoadingState,
  Methodology,
  StatePanel,
} from "./components/Layout";
import { formatLongDate } from "./lib/format";

function Dashboard() {
  const [range, setRange] = useState({ from: JANUARY_START, to: JANUARY_END });
  const [focusedDay, setFocusedDay] = useState<string | null>(null);
  const [selectedTime, setSelectedTime] = useState<string | null>(null);
  const queryKey = [range.from, range.to];
  const overviewQuery = useQuery({
    queryKey: ["overview", ...queryKey],
    queryFn: () => fetchOverview(range.from, range.to),
  });
  const timeseriesQuery = useQuery({
    queryKey: ["timeseries", ...queryKey],
    queryFn: () => fetchTimeseries(range.from, range.to),
  });
  const dailyQuery = useQuery({
    queryKey: ["daily-accuracy", ...queryKey],
    queryFn: () => fetchDailyAccuracy(range.from, range.to),
  });
  const points = useMemo(() => timeseriesQuery.data?.points ?? [], [timeseriesQuery.data]);

  useEffect(() => {
    if (points.length && !points.some((point) => point.startTime === selectedTime)) {
      setSelectedTime(points[0].startTime);
    }
  }, [points, selectedTime]);

  const isLoading = overviewQuery.isPending || timeseriesQuery.isPending || dailyQuery.isPending;
  const isError = overviewQuery.isError || timeseriesQuery.isError || dailyQuery.isError;

  function retry() {
    void Promise.all([overviewQuery.refetch(), timeseriesQuery.refetch(), dailyQuery.refetch()]);
  }

  return (
    <div className="app-shell" id="top">
      <Header status={overviewQuery.data?.dataStatus.status} />
      <main className="dashboard">
        <section className="review-header" id="overview" aria-labelledby="review-title">
          <div className="review-copy">
            <h1 id="review-title">January wind forecast review</h1>
            <p className="review-intro">How accurately did Great Britain’s day-ahead wind forecast describe the generation that followed?</p>
            <div className="review-meta" aria-label="Review scope">
              <span>January 2026</span>
              <span>Great Britain</span>
              <span>Elexon WINDFOR + FUELHH</span>
            </div>
          </div>
          <div className="review-tools">
            <div className="decision-rule" aria-label="Decision-time rule">
              <span>No-hindsight cutoff</span>
              <strong>D-1 · 09:50 GMT</strong>
              <small>Latest forecast published before the purchasing decision.</small>
            </div>
            <DateRangeControls
              from={range.from}
              to={range.to}
              onApply={(from, to) => {
                setFocusedDay(null);
                setRange({ from, to });
              }}
            />
          </div>
        </section>

        {isLoading ? <LoadingState /> : null}
        {!isLoading && isError ? <StatePanel type="error" onRetry={retry} /> : null}
        {!isLoading && !isError && overviewQuery.data && timeseriesQuery.data && dailyQuery.data ? (
          points.length === 0 ? <StatePanel type="empty" /> : (
            <div className="dashboard-content">
              {overviewQuery.data.dataStatus.status === "stale" ? <div className="stale-banner" role="status">This snapshot predates the complete reporting window. Refresh the Elexon data before relying on it.</div> : null}
              {focusedDay ? (
                <div className="focus-banner" role="status" aria-label="Active date filter">
                  <span>Focused on <strong>{formatLongDate(focusedDay)}</strong></span>
                  <button
                    type="button"
                    onClick={() => {
                      setFocusedDay(null);
                      setRange({ from: JANUARY_START, to: JANUARY_END });
                    }}
                  >
                    Back to January
                  </button>
                </div>
              ) : null}
              <KpiGrid metrics={overviewQuery.data.metrics} />
              <ForecastChart points={points} selectedTime={selectedTime} />
              <DailyTable
                days={dailyQuery.data.days}
                onFocusDay={(date) => {
                  setFocusedDay(date);
                  setRange({ from: date, to: date });
                }}
              />
              <EvolutionPanel points={points} selectedTime={selectedTime} onSelect={setSelectedTime} />
              <Methodology />
            </div>
          )
        ) : null}
      </main>
      <footer><span>WindSight UK</span><span>Elexon WINDFOR + FUELHH · All times GMT</span></footer>
    </div>
  );
}

export function App() {
  const [queryClient] = useState(() => new QueryClient({
    defaultOptions: { queries: { retry: false, staleTime: 5 * 60 * 1000 } },
  }));

  return <QueryClientProvider client={queryClient}><Dashboard /></QueryClientProvider>;
}
