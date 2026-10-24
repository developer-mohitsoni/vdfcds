import { render, screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { App } from "./App";

const overview = {
  period: { from: "2026-01-01", to: "2026-01-31" },
  metrics: {
    maeMw: 15,
    rmseMw: 18.5,
    meanBiasMw: -5,
    wapePercent: 8.4,
    p90AbsoluteErrorMw: 30,
    expectedHours: 3,
    completeHours: 3,
    coveragePercent: 100,
  },
  dataStatus: {
    status: "ready",
    generatedAt: "2026-02-03T12:00:00Z",
    schemaVersion: "1.0",
    completeHours: 3,
  },
};

const points = [
  {
    startTime: "2026-01-01T00:00:00Z",
    forecastMw: 110,
    actualMw: 100,
    errorMw: 10,
    forecastPublishTime: "2025-12-31T08:30:00Z",
    decisionCutoff: "2025-12-31T09:50:00Z",
  },
  {
    startTime: "2026-01-02T00:00:00Z",
    forecastMw: 180,
    actualMw: 200,
    errorMw: -20,
    forecastPublishTime: "2026-01-01T08:30:00Z",
    decisionCutoff: "2026-01-01T09:50:00Z",
  },
];

const daily = {
  period: overview.period,
  days: [
    { date: "2026-01-01", metrics: { ...overview.metrics, maeMw: 10 } },
    { date: "2026-01-02", metrics: { ...overview.metrics, maeMw: 20 } },
  ],
};

const evolution = {
  startTime: "2026-01-01T00:00:00Z",
  decisionCutoff: "2025-12-31T09:50:00Z",
  selectedPublishTime: "2025-12-31T08:30:00Z",
  selectedForecastMw: 110,
  actualMw: 100,
  revisions: [
    {
      publishTime: "2025-12-31T08:00:00Z",
      generationMw: 105,
      eligibleAtCutoff: true,
      selected: false,
    },
    {
      publishTime: "2025-12-31T08:30:00Z",
      generationMw: 110,
      eligibleAtCutoff: true,
      selected: true,
    },
  ],
};

function jsonResponse(body: unknown): Promise<Response> {
  return Promise.resolve({
    ok: true,
    status: 200,
    json: () => Promise.resolve(body),
  } as Response);
}

function installSuccessfulApi(overrides?: { empty?: boolean; evolutionError?: boolean }) {
  return vi.spyOn(globalThis, "fetch").mockImplementation((input) => {
    const url = typeof input === "string" ? input : input instanceof URL ? input.toString() : input.url;
    if (url.includes("/overview")) {
      return jsonResponse(
        overrides?.empty
          ? {
              ...overview,
              metrics: {
                ...overview.metrics,
                maeMw: null,
                rmseMw: null,
                completeHours: 0,
                coveragePercent: 0,
              },
            }
          : overview,
      );
    }
    if (url.includes("/timeseries")) {
      return jsonResponse({
        period: overview.period,
        points: overrides?.empty ? [] : points,
      });
    }
    if (url.includes("/daily-accuracy")) {
      return jsonResponse(overrides?.empty ? { ...daily, days: [] } : daily);
    }
    if (url.includes("/forecast-evolution")) {
      if (overrides?.evolutionError) {
        return Promise.reject(new Error("Revision service unavailable"));
      }
      return jsonResponse(evolution);
    }
    throw new Error(`Unexpected request: ${url}`);
  });
}

describe("WindSight dashboard", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.restoreAllMocks();
    vi.unstubAllGlobals();
  });

  it("renders KPI metrics and forecast-versus-actual data", async () => {
    installSuccessfulApi();

    render(<App />);

    expect(await screen.findByText("15 MW")).toBeInTheDocument();
    expect(within(screen.getByLabelText("Forecast accuracy summary")).getByText("8.4%")).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Forecast vs actual" })).toBeInTheDocument();
    expect(screen.getByLabelText("Chart data summary")).toHaveTextContent("2 hourly observations");
    expect(screen.queryAllByRole("listitem")).toHaveLength(0);
  });

  it("connects the evaluator overview to analytical evidence", async () => {
    installSuccessfulApi();
    render(<App />);
    await screen.findByText("15 MW");

    const navigation = screen.getByRole("navigation", { name: "Dashboard sections" });
    expect(within(navigation).getByRole("link", { name: "Performance" })).toHaveAttribute("href", "#performance");
    expect(within(navigation).getByRole("link", { name: "Decision trail" })).toHaveAttribute("href", "#decision-trail");
    expect(screen.getByLabelText("Decision-time rule")).toHaveTextContent("D-1 · 09:50 GMT");
    expect(screen.getByRole("region", { name: "Forecast performance" })).toHaveAttribute("id", "performance");
  });

  it("explains an invalid draft date range", async () => {
    installSuccessfulApi();
    const user = userEvent.setup();
    render(<App />);
    await screen.findByText("15 MW");

    await user.clear(screen.getByLabelText("From date"));
    await user.type(screen.getByLabelText("From date"), "2026-01-02");
    await user.clear(screen.getByLabelText("To date"));
    await user.type(screen.getByLabelText("To date"), "2026-01-01");

    expect(screen.getByText("From date must be on or before To date.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Apply date range" })).toBeDisabled();
  });

  it("applies a changed date range to API requests", async () => {
    const fetchMock = installSuccessfulApi();
    const user = userEvent.setup();
    render(<App />);
    await screen.findByText("15 MW");

    const fromInput = screen.getByLabelText("From date");
    const toInput = screen.getByLabelText("To date");
    await user.clear(fromInput);
    await user.type(fromInput, "2026-01-02");
    await user.clear(toInput);
    await user.type(toInput, "2026-01-02");
    await user.click(screen.getByRole("button", { name: "Apply date range" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("from=2026-01-02&to=2026-01-02"),
        expect.anything(),
      ),
    );
  });

  it("focuses the dashboard when a daily table row is selected", async () => {
    installSuccessfulApi();
    const user = userEvent.setup();
    render(<App />);

    await user.click(await screen.findByRole("button", { name: "Focus day — 2 January 2026" }));

    expect(screen.getByLabelText("From date")).toHaveValue("2026-01-02");
    expect(screen.getByLabelText("To date")).toHaveValue("2026-01-02");
    expect(screen.getByRole("status", { name: "Active date filter" })).toHaveTextContent("2 January 2026");

    await user.click(screen.getByRole("button", { name: "Back to January" }));
    expect(screen.getByLabelText("From date")).toHaveValue("2026-01-01");
    expect(screen.getByLabelText("To date")).toHaveValue("2026-01-31");
  });

  it("loads forecast evolution for the selected delivery hour", async () => {
    const fetchMock = installSuccessfulApi();
    const user = userEvent.setup();
    render(<App />);

    const daySelect = await screen.findByLabelText("Delivery day");
    await user.selectOptions(daySelect, "2026-01-02");

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("startTime=2026-01-02T00%3A00%3A00Z"),
        expect.anything(),
      ),
    );
    expect(await screen.findByText("Selected revision")).toBeInTheDocument();
  });

  it("steps through delivery hours without a long selector", async () => {
    const fetchMock = installSuccessfulApi();
    const user = userEvent.setup();
    render(<App />);

    await user.click(await screen.findByRole("button", { name: "Next delivery hour" }));

    await waitFor(() =>
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("startTime=2026-01-02T00%3A00%3A00Z"),
        expect.anything(),
      ),
    );
  });

  it("offers retry when revision history fails", async () => {
    installSuccessfulApi({ evolutionError: true });
    const user = userEvent.setup();
    render(<App />);

    const alert = await screen.findByRole("alert", { name: "Revision history error" });
    expect(within(alert).getByText("Revision history is unavailable.")).toBeInTheDocument();
    await user.click(within(alert).getByRole("button", { name: "Retry revision history" }));
  });

  it("shows a loading state while API requests are pending", () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(
      () => new Promise<Response>(() => undefined),
    );

    render(<App />);

    expect(screen.getByTestId("dashboard-loading")).toBeInTheDocument();
  });

  it("shows an empty state when the selected range has no observations", async () => {
    installSuccessfulApi({ empty: true });

    render(<App />);

    expect(await screen.findByRole("status", { name: "No data" })).toBeInTheDocument();
  });

  it("shows a retryable error state when the API cannot be reached", async () => {
    vi.spyOn(globalThis, "fetch").mockRejectedValue(new Error("Network unavailable"));

    render(<App />);

    expect(await screen.findByRole("alert")).toHaveTextContent("Unable to load dashboard data");
    expect(screen.getByRole("button", { name: "Try again" })).toBeInTheDocument();
  });
});
