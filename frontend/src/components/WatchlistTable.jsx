function WatchlistTable({ stocks, onStockClick, showStage = false }) {
  if (!stocks.length) return <p>No stocks found.</p>;

  return (
    <table className="watchlist-table">
      <thead>
        <tr>
          <th>Symbol</th>
          <th>Gain %</th>
          {showStage && <th>Stage</th>}
          {showStage && <th>Pullback %</th>}
        </tr>
      </thead>
      <tbody>
        {stocks.map((stock) => (
          <tr key={stock.symbol} onClick={() => onStockClick(stock.symbol)} className="watchlist-row">
            <td><strong>{stock.symbol}</strong></td>
            <td className={stock.percent_change >= 3 ? "positive" : ""}>
              {stock.percent_change?.toFixed(2)}%
            </td>
            {showStage && <td>{stock.stage || "—"}</td>}
            {showStage && <td>{stock.pullback_percent?.toFixed(2)}%</td>}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default WatchlistTable;