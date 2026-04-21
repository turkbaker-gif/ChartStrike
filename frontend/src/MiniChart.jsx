import { useEffect, useRef } from "react";
import {
  createChart,
  CandlestickSeries,
  LineSeries,
} from "lightweight-charts";

function MiniChart({ candles = [], signal = null }) {
  const containerRef = useRef(null);
  const chartRef = useRef(null);
  const candleSeriesRef = useRef(null);
  const entryLowRef = useRef(null);
  const entryHighRef = useRef(null);
  const stopRef = useRef(null);
  const target1Ref = useRef(null);
  const target2Ref = useRef(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const chart = createChart(containerRef.current, {
      width: containerRef.current.clientWidth,
      height: 320,
      layout: {
        background: { color: "#020617" },
        textColor: "#cbd5e1",
      },
      grid: {
        vertLines: { color: "#1e293b" },
        horzLines: { color: "#1e293b" },
      },
      rightPriceScale: {
        borderColor: "#334155",
      },
      timeScale: {
        borderColor: "#334155",
        timeVisible: true,
        secondsVisible: false,
      },
      crosshair: {
        mode: 1,
      },
    });

    const candleSeries = chart.addSeries(CandlestickSeries);

    const entryLowLine = chart.addSeries(LineSeries, {
      color: "#3b82f6",
      lineWidth: 1,
      priceLineVisible: false,
      lastValueVisible: false,
    });

    const entryHighLine = chart.addSeries(LineSeries, {
      color: "#60a5fa",
      lineWidth: 1,
      priceLineVisible: false,
      lastValueVisible: false,
    });

    const stopLine = chart.addSeries(LineSeries, {
      color: "#ef4444",
      lineWidth: 1,
      priceLineVisible: false,
      lastValueVisible: false,
    });

    const target1Line = chart.addSeries(LineSeries, {
      color: "#22c55e",
      lineWidth: 1,
      priceLineVisible: false,
      lastValueVisible: false,
    });

    const target2Line = chart.addSeries(LineSeries, {
      color: "#16a34a",
      lineWidth: 1,
      priceLineVisible: false,
      lastValueVisible: false,
    });

    chartRef.current = chart;
    candleSeriesRef.current = candleSeries;
    entryLowRef.current = entryLowLine;
    entryHighRef.current = entryHighLine;
    stopRef.current = stopLine;
    target1Ref.current = target1Line;
    target2Ref.current = target2Line;

    const handleResize = () => {
      if (containerRef.current && chartRef.current) {
        chartRef.current.applyOptions({
          width: containerRef.current.clientWidth,
        });
      }
    };

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
      chart.remove();
    };
  }, []);

  useEffect(() => {
    if (!candleSeriesRef.current) return;

    const formattedCandles = (candles || [])
      .filter((c) => c.ts && c.open != null && c.high != null && c.low != null && c.close != null)
      .map((c) => ({
        time: Math.floor(new Date(c.ts).getTime() / 1000),
        open: Number(c.open),
        high: Number(c.high),
        low: Number(c.low),
        close: Number(c.close),
      }));

    candleSeriesRef.current.setData(formattedCandles);

    if (!formattedCandles.length) return;

    const linePoints = (price) =>
      formattedCandles.map((c) => ({
        time: c.time,
        value: Number(price),
      }));

    if (signal?.entry_low != null) {
      entryLowRef.current?.setData(linePoints(signal.entry_low));
    } else {
      entryLowRef.current?.setData([]);
    }

    if (signal?.entry_high != null) {
      entryHighRef.current?.setData(linePoints(signal.entry_high));
    } else {
      entryHighRef.current?.setData([]);
    }

    if (signal?.stop_price != null) {
      stopRef.current?.setData(linePoints(signal.stop_price));
    } else {
      stopRef.current?.setData([]);
    }

    if (signal?.target_1 != null) {
      target1Ref.current?.setData(linePoints(signal.target_1));
    } else {
      target1Ref.current?.setData([]);
    }

    if (signal?.target_2 != null) {
      target2Ref.current?.setData(linePoints(signal.target_2));
    } else {
      target2Ref.current?.setData([]);
    }

    chartRef.current?.timeScale().fitContent();
  }, [candles, signal]);

  return <div ref={containerRef} style={{ width: "100%", height: 320 }} />;
}

export default MiniChart;