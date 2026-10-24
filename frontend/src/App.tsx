export function App() {
  return (
    <main className="app-shell">
      <div className="ambient ambient-one" />
      <div className="ambient ambient-two" />
      <section className="welcome-card" aria-labelledby="product-title">
        <p className="eyebrow">UK wind intelligence</p>
        <h1 id="product-title">WindSight UK</h1>
        <p className="intro">
          Decision-time forecast accuracy for Great Britain&apos;s wind generation.
        </p>
        <div className="status-row">
          <span className="status-dot" aria-hidden="true" />
          <span>Foundation ready · January 2026 analytics coming next</span>
        </div>
      </section>
    </main>
  );
}
