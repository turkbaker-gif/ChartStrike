import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import MarketOverview from "../components/MarketOverview";
import NewsPanel from "../components/NewsPanel";
import WatchlistTable from "../components/WatchlistTable";
import { getTopGainers, getPullbackWatchlist } from "../api";
import "./Dashboard.css";

function Dashboard() {
  const [topGainers, setTopGainers] = useState([]);
  const [pullbacks, setPullbacks] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    loadAll();
    const interval = setInterval(loadAll, 60000);
    return () => clearInterval(interval);
  }, []);

  async function loadAll() {
    try {
      const [gainersData, pullbacksData] = await Promise.all([
        getTopGainers(),
        getPullbackWatchlist(),
      ]);
      setTopGainers(gainersData.watchlist || []);
      setPullbacks(pullbacksData.watchlist || []);
    } catch (err) {
      console.error("Failed to load watchlists:", err);
    } finally {
      setLoading(false);
    }
  }

  function handleStockClick(symbol) {
    navigate(`/stock/${symbol}`);
  }

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>ChartStrike</h1>
        <span className="last-update">Live HK/CN Market Intelligence</span>
      </header>

      <div className="dashboard-grid">
        {/* Left column: Market Overview */}
        <section className="dashboard-panel">
          <MarketOverview />
        </section>

        {/* Middle column: Top Gainers + Pullback Detected stacked */}
        <div className="middle-column">
          <section className="dashboard-panel">
            <h2>🔥 Top Gainers (HK + CN)</h2>
            {loading ? (
              <p>Loading...</p>
            ) : (
              <WatchlistTable stocks={topGainers} onStockClick={handleStockClick} />
            )}
          </section>

          <section className="dashboard-panel">
            <h2>📉 Pullback Detected</h2>
            {loading ? (
              <p>Loading...</p>
            ) : (
              <WatchlistTable stocks={pullbacks} onStockClick={handleStockClick} showStage={true} />
            )}
          </section>
        </div>

        {/* Right column: News */}
        <section className="dashboard-panel">
          <NewsPanel />
        </section>
      </div>
    </div>
  );
}

export default Dashboard;