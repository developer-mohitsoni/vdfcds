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

function Dashboard() {
  const [range, setRange] = useState({ from: JANUARY_START, to: JANUARY_END });
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
        <section className="hero">
          <div className="hero-copy">
            <p className="eyebrow">January 2026 · Great Britain</p>
            <h1>Day-ahead wind, <em>without hindsight.</em></h1>
            <p>Compare the forecast available at the purchasing deadline with what the grid actually produced.</p>
          </div>
          <DateRangeControls from={range.from} to={range.to} onApply={(from, to) => setRange({ from, to })} />
        </section>

        {isLoading ? <LoadingState /> : null}
        {!isLoading && isError ? <StatePanel type="error" onRetry={retry} /> : null}
        {!isLoading && !isError && overviewQuery.data && timeseriesQuery.data && dailyQuery.data ? (
          points.length === 0 ? <StatePanel type="empty" /> : (
            <div className="dashboard-content">
              {overviewQuery.data.dataStatus.status === "stale" ? <div className="stale-banner" role="status">This snapshot predates the complete reporting window. Refresh the Elexon data before relying on it.</div> : null}
              <KpiGrid metrics={overviewQuery.data.metrics} />
              <ForecastChart points={points} selectedTime={selectedTime} />
              <DailyTable days={dailyQuery.data.days} onFocusDay={(date) => setRange({ from: date, to: date })} />
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
