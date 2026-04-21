import { useParams } from "react-router-dom";
import { useEffect, useState } from "react";
import "./StockDetail.css";

import {
  getFullAnalysis,
  getCandles,
  getChecklist,
  getCatalyst,
  getExplanation,
  getIntelligence,
  getQuote,
  getSimulatedTradeForSignal,
  createSimulatedTrade,
  getSignalsBySymbol,
} from "../api";
import MiniChart from "../components/MiniChart";

function StockDetail() {
  const { symbol } = useParams();
  const [analysis, setAnalysis] = useState(null);
  const [candles, setCandles] = useState([]);
  const [checklist, setChecklist] = useState(null);
  const [catalyst, setCatalyst] = useState(null);
  const [explanation, setExplanation] = useState(null);
  const [intelligence, setIntelligence] = useState(null);
  const [liveQuote, setLiveQuote] = useState(null);
  const [selectedTrade, setSelectedTrade] = useState(null);
  const [signalId, setSignalId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [noSignal, setNoSignal] = useState(false);   // <-- new state

  useEffect(() => {
    loadAllData();
    const interval = setInterval(() => {
      loadQuote();
      if (signalId) {
        loadTrade(signalId);
      }
    }, 30000);
    return () => clearInterval(interval);
  }, [symbol, signalId]);

  async function loadAllData() {
    setLoading(true);
    setNoSignal(false);
    try {
      // Try to get signals, but don't fail if none exist
      let id = null;
      try {
        const signals = await getSignalsBySymbol(symbol, 1);
        id = signals[0]?.id;
        setSignalId(id);
      } catch (err) {
        // 404 or other error – just means no signals
        console.log(`No signals found for ${symbol}, loading data-only view.`);
        setNoSignal(true);
      }

      // Always load quote and candles (they don't depend on signal)
      await loadQuote();

      if (id) {
        // Full signal exists – load everything
        const [
          full,
          candlesData,
          checklistData,
          catalystData,
          explanationData,
          intelligenceData,
        ] = await Promise.all([
          getFullAnalysis(id),
          getCandles(id, 50),
          getChecklist(id),
          getCatalyst(id),
          getExplanation(id),
          getIntelligence(id),
        ]);

        setAnalysis(full);
        setCandles(candlesData);
        setChecklist(checklistData);
        setCatalyst(catalystData);
        setExplanation(explanationData);
        setIntelligence(intelligenceData);
        await loadTrade(id);
      } else {
        // No signal – load only candles and news
        // We can still fetch candles using LocalDataService directly?
        // For now, we can leave candles empty or fetch from a generic endpoint.
        // As a fallback, we can just skip the chart or show empty state.
        console.log(`No signal for ${symbol} – chart and news only.`);
        // Optionally, you could still fetch candles using a direct symbol endpoint
        // e.g., const candlesData = await getCandlesBySymbol(symbol, 50);
        // For now, we'll set empty candles and let the chart show "no data".
        setCandles([]);
      }

      // Catalyst/news can be fetched even without a signal
      try {
        const catalystData = await getCatalyst(null); // Wait, getCatalyst expects signalId. Need a symbol-based version.
        // Since getCatalyst uses signalId, we can't call it without a signal.
        // We'll skip for now or create a symbol-based catalyst endpoint later.
      } catch {
        // ignore
      }

    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  async function loadQuote() {
    try {
      const quote = await getQuote(symbol);
      setLiveQuote(quote);
    } catch (err) {
      console.error("Quote failed:", err);
    }
  }

  async function loadTrade(id) {
    if (!id) return;
    try {
      const trade = await getSimulatedTradeForSignal(id);
      setSelectedTrade(trade);
    } catch (err) {
      console.error("Trade fetch failed:", err);
    }
  }

  async function handleStartSimulatedTrade() {
    if (!signalId) return;
    try {
      const trade = await createSimulatedTrade(signalId, {
        account_size: 10000,
        risk_percent: 1,
        max_portfolio_risk_percent: 6,
      });
      setSelectedTrade(trade);
    } catch (err) {
      console.error("Failed to start simulated trade:", err);
    }
  }

  if (loading) return <div className="loading">Loading {symbol}...</div>;

  return (
    <div className="stock-detail">
      <header className="detail-header">
        <h1>{symbol}</h1>
        {liveQuote && (
          <div className="live-quote-header">
            <span className="price">{liveQuote.price}</span>
            <span className={`change ${liveQuote.change >= 0 ? "positive" : "negative"}`}>
              {liveQuote.change > 0 ? "+" : ""}{liveQuote.change} ({liveQuote.percent_change}%)
            </span>
          </div>
        )}
      </header>

      <div className="detail-grid">
        <div className="chart-section">
          <MiniChart key={candles.length} candles={candles} signal={analysis?.signal} />
        </div>

        <div className="info-panels">
          {noSignal && (
            <div className="panel">
              <h3>No Active Signal</h3>
              <p>This stock does not have any current trading signals.</p>
              <p style={{ marginTop: "8px", fontSize: "14px", color: "#94a3b8" }}>
                You can still view the chart and news headlines below.
              </p>
            </div>
          )}

          {/* Trade Plan – only if signal exists */}
          {analysis && (
            <div className="panel">
              <h3>Trade Plan</h3>
              <div className="grid">
                <div>Entry: {analysis.signal.entry_low} – {analysis.signal.entry_high}</div>
                <div>Stop: {analysis.signal.stop_price}</div>
                <div>Target 1: {analysis.signal.target_1}</div>
                <div>Target 2: {analysis.signal.target_2}</div>
              </div>
            </div>
          )}

          {/* Simulation – only if signal exists */}
          {analysis && (
            <div className="panel">
              <h3>Simulation</h3>
              {selectedTrade ? (
                <div>
                  <div>Status: {selectedTrade.status}</div>
                  <div>Entry: {selectedTrade.entry_price}</div>
                  <div>PnL: {selectedTrade.pnl_amount}</div>
                  <div>R: {selectedTrade.pnl_r_multiple}</div>
                </div>
              ) : (
                <button onClick={handleStartSimulatedTrade}>Start Simulated Trade</button>
              )}
            </div>
          )}

          {/* Trade Readiness – only if signal exists */}
          {checklist && (
            <div className="panel">
              <h3>Trade Readiness</h3>
              <div className={`verdict ${checklist.verdict}`}>{checklist.verdict.toUpperCase()}</div>
              <ul>
                {checklist.checklist.map((item, i) => (
                  <li key={i} className={item.status}>
                    {item.name}: {item.message}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Explanation – only if signal exists */}
          {explanation && (
            <div className="panel">
              <h3>System Explanation</h3>
              <p>{explanation.summary}</p>
            </div>
          )}

          {/* AI Review – only if signal exists */}
          {analysis?.ai_review && (
            <div className="panel">
              <h3>AI Review</h3>
              <div className="verdict">{analysis.ai_review.verdict}</div>
              <p>{analysis.ai_review.analysis}</p>
            </div>
          )}

          {/* Catalyst/News – we can show this even without a signal? Currently getCatalyst requires signalId. */}
          {/* You may want to create a symbol-based catalyst endpoint later. */}
          {catalyst && (
            <div className="panel">
              <h3>Catalyst</h3>
              <p>{catalyst.ai_interpretation || catalyst.summary}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default StockDetail;