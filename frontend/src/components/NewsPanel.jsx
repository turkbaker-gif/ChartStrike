import { useEffect, useState } from "react";
import { getMarketNews } from "../api";

function NewsPanel() {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadNews();
    // Refresh every 2 minutes
    const interval = setInterval(loadNews, 120000);
    return () => clearInterval(interval);
  }, []);

  async function loadNews() {
    try {
      const data = await getMarketNews(20);
      setNews(data.articles || []);
    } catch (err) {
      console.error("Failed to load news:", err);
    } finally {
      setLoading(false);
    }
  }

  if (loading) return <p className="loading-text">Loading headlines...</p>;

  return (
    <div className="news-panel">
      <h2>Market News</h2>
      <ul className="news-list">
        {news.length === 0 ? (
          <li className="news-item">No recent headlines</li>
        ) : (
          news.map((item, idx) => (
            <li key={idx} className="news-item">
              <a href={item.url} target="_blank" rel="noopener noreferrer">
                {item.title}
              </a>
              <span className="news-source">{item.source}</span>
            </li>
          ))
        )}
      </ul>
    </div>
  );
}

export default NewsPanel;