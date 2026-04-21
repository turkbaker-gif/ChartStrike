import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

export async function getIndexQuote(code) {
  const res = await api.get(`/index-quote/${encodeURIComponent(code)}`);
  return res.data;
}

export async function getTopGainers() {
  const res = await api.get("/hk/watchlist"); // This already returns HK + CN if backend updated
  return res.data;
}

export async function getPullbackWatchlist() {
  const res = await api.get("/pullback-watchlist");
  return res.data;
}

export async function getRankedSignals() {
  const res = await api.get("/ranked-signals");
  return res.data;
}

export async function getFullAnalysis(signalId) {
  const res = await api.get(`/signals/${signalId}/full-analysis`);
  return res.data;
}

export async function getCandles(signalId, limit = 50) {
  const res = await api.get(`/signals/${signalId}/candles?limit=${limit}`);
  return res.data;
}

export async function getTradeDashboard() {
  const res = await api.get("/trade-dashboard");
  return res.data;
}

export async function getAnalytics() {
  const res = await api.get("/analytics");
  return res.data;
}

export async function getPortfolioRisk(accountSize, maxPortfolioRiskPercent) {
  const res = await api.get(
    `/portfolio-risk?account_size=${accountSize}&max_portfolio_risk_percent=${maxPortfolioRiskPercent}`
  );
  return res.data;
}

export async function getChecklist(signalId) {
  const res = await api.get(`/signals/${signalId}/checklist`);
  return res.data;
}

export async function getCatalyst(signalId) {
  const res = await api.get(`/signals/${signalId}/catalyst`);
  return res.data;
}

export async function getSimulatedTradeForSignal(signalId) {
  const res = await api.get(`/signals/${signalId}/simulated-trade`);
  return res.data;
}

export async function createSimulatedTrade(signalId, payload) {
  const res = await api.post(`/signals/${signalId}/simulate`, payload);
  return res.data;
}

export async function getQuote(symbol) {
  const encodedSymbol = encodeURIComponent(symbol);
  const res = await api.get(`/quote/${encodedSymbol}`);
  return res.data;
}

export async function getIntelligence(signalId) {
  const res = await api.get(`/signals/${signalId}/intelligence`);
  return res.data;
}

export async function getScannerFeed(limit = 50) {
  const res = await api.get(`/scanner-feed?limit=${limit}`);
  return res.data;
}

export async function getExplanation(signalId) {
  const res = await api.get(`/signals/${signalId}/explanation`);
  return res.data;
}

export async function getMarketNews(limit = 20) {
  const res = await api.get(`/market-news?limit=${limit}`);
  return res.data;
}

export async function getSignalsBySymbol(symbol, limit = 10) {
  const res = await api.get(`/signals/by-symbol/${encodeURIComponent(symbol)}?limit=${limit}`);
  return res.data;
}

export async function getHKWatchlist() {
  const res = await api.get("/hk/watchlist");
  return res.data;
}

export default api;