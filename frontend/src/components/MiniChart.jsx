import { useEffect, useRef } from "react";
import { createChart, CandlestickSeries } from "lightweight-charts";

function MiniChart({ candles, signal }) {
  const containerRef = useRef(null);
  const chartRef = useRef(null);
  const seriesRef = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    // Clean up previous chart if any
    if (chartRef.current) {
      chartRef.current.remove();
    }

    chartRef.current = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 400,
      layout: {
        background: { color: "#0f172a" },
        textColor: "#cbd5e1",
      },
      grid: {
        vertLines: { color: "#1e293b" },
        horzLines: { color: "#1e293b" },
      },
      timeScale: {
        borderColor: "#334155",
        timeVisible: true,
      },
    });

    seriesRef.current = chartRef.current.addSeries(CandlestickSeries);

    const handleResize = () => {
      if (containerRef.current && chartRef.current) {
        chartRef.current.applyOptions({ width: containerRef.current.clientWidth });
      }
    };
    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!seriesRef.current || !candles || candles.length === 0) {
      console.warn("No candles data for chart");
      return;
    }

    const formatted = candles.map((c) => ({
      time: Math.floor(new Date(c.ts || c.date).getTime() / 1000),
      open: parseFloat(c.open),
      high: parseFloat(c.high),
      low: parseFloat(c.low),
      close: parseFloat(c.close),
    }));

    seriesRef.current.setData(formatted);
    chartRef.current?.timeScale().fitContent();
  }, [candles]);

  return <div ref={containerRef} style={{ width: "100%", height: "400px" }} />;
}

export default MiniChart;