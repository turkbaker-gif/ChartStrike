import { useEffect, useState } from "react";

const INDICES = [
  { code: "HSI", name: "Hang Seng" },
  { code: "HSCEI", name: "HSCEI" },
  { code: "000300", name: "CSI 300" },
  { code: "000001", name: "SSE Composite" },
];

function MarketOverview() {
  const [indices, setIndices] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadIndices();
    const interval = setInterval(loadIndices, 60000); // 1 minute
    return () => clearInterval(interval);
  }, []);

  async function loadIndices() {
    try {
      const res = await fetch("http://127.0.0.1:8000/index-quotes");
      const quotes = await res.json();
      const results = {};
      for (const idx of INDICES) {
        const quote = quotes[idx.code];
        if (quote) {
          results[idx.code] = {
            ...idx,
            price: quote.price,
            change: quote.change,
            changePercent: quote.percent_change,
          };
        }
      }
      setIndices(results);
    } catch (err) {
      console.error("Failed to load indices:", err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <p>Loading indices...</p>;

  return (
    <div className="market-overview">
      <h2>Market Overview</h2>
      <div className="indices-grid">
        {Object.values(indices).map((idx) => (
          <div key={idx.code} className="index-card">
            <div className="index-name">{idx.name}</div>
            <div className="index-price">{idx.price?.toFixed(2)}</div>
            <div className={`index-change ${idx.change >= 0 ? "positive" : "negative"}`}>
              {idx.change > 0 ? "+" : ""}{idx.change?.toFixed(2)} ({idx.changePercent?.toFixed(2)}%)
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default MarketOverview;