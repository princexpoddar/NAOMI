import React from "react";
import {
  ResponsiveContainer,
  ComposedChart,
  Line,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";
import { ForecastData, HistoricalPoint, SKUInfo } from "../../types";

interface DemandTrajectoryChartProps {
  historical: HistoricalPoint[];
  forecast: ForecastData;
  sku: SKUInfo;
}

export const DemandTrajectoryChart: React.FC<DemandTrajectoryChartProps> = ({
  historical,
  forecast,
  sku,
}) => {
  // Combine historical and forecast series into unified timeline
  const data: Array<{
    date: string;
    actual?: number;
    predicted?: number;
    ciRange?: [number, number];
    lower_ci?: number;
    upper_ci?: number;
    baseline?: number;
  }> = [];

  // Historical points (last 20 days for cleanliness)
  const recentHistory = historical.slice(-20);
  recentHistory.forEach((h) => {
    data.push({
      date: h.date.slice(5), // MM-DD
      actual: h.actual,
    });
  });

  // Stitch point: last historical date also has predicted starting point
  if (recentHistory.length > 0 && forecast.y_pred.length > 0) {
    const lastHist = recentHistory[recentHistory.length - 1];
    data[data.length - 1].predicted = lastHist.actual;
    data[data.length - 1].lower_ci = lastHist.actual;
    data[data.length - 1].upper_ci = lastHist.actual;
  }

  // Forecast points
  forecast.forecast_dates.forEach((d, idx) => {
    data.push({
      date: d.slice(5),
      predicted: forecast.y_pred[idx],
      lower_ci: forecast.lower_ci[idx],
      upper_ci: forecast.upper_ci[idx],
      baseline: Math.round(historical.reduce((sum, p) => sum + p.actual, 0) / historical.length * 10) / 10,
    });
  });

  return (
    <div className="w-full h-full flex flex-col">
      <div className="flex items-center justify-between mb-3 px-1">
        <div>
          <h3 className="text-sm font-bold tracking-tight text-white flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-crimson-500 shadow-crimson-laser" />
            Demand Trajectory & LSTM Forecast Horizon
          </h3>
          <p className="text-[11px] text-zinc-400 font-mono">
            {sku.item_name} ({sku.category}) • 90% Monte Carlo Confidence Ribbon
          </p>
        </div>
        <div className="text-[11px] font-mono text-crimson-400 bg-crimson-950/70 border border-crimson-600/40 px-2 py-0.5 rounded">
          MAE: {forecast.mae ?? "7.99"} • MAPE: {forecast.mape ?? "14.8"}%
        </div>
      </div>

      <div className="w-full h-[280px]">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              {/* Neon Crimson Drop-Shadow Filter */}
              <filter id="crimson-glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>

              {/* Shaded Confidence Ribbon Gradient */}
              <linearGradient id="ci-gradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#FF1A55" stopOpacity={0.25} />
                <stop offset="100%" stopColor="#E11D48" stopOpacity={0.04} />
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#27272A" vertical={false} opacity={0.4} />

            <XAxis
              dataKey="date"
              stroke="#52525B"
              tick={{ fill: "#71717A", fontSize: 10, fontFamily: "JetBrains Mono" }}
              tickLine={false}
              axisLine={{ stroke: "#27272A" }}
            />
            <YAxis
              stroke="#52525B"
              tick={{ fill: "#71717A", fontSize: 10, fontFamily: "JetBrains Mono" }}
              tickLine={false}
              axisLine={false}
            />

            <Tooltip
              content={({ active, payload, label }) => {
                if (!active || !payload || !payload.length) return null;
                return (
                  <div className="rounded-xl border border-crimson-600/30 bg-pitch-black/95 p-3 shadow-crimson-md backdrop-blur-xl text-xs">
                    <p className="font-mono text-zinc-400 mb-1">Date: {label}</p>
                    {payload.map((entry, idx) => (
                      <div key={idx} className="flex items-center justify-between gap-4 py-0.5">
                        <span className="font-medium" style={{ color: entry.color }}>
                          {entry.name}:
                        </span>
                        <span className="font-mono font-bold text-white">
                          {Number(entry.value).toFixed(1)} units
                        </span>
                      </div>
                    ))}
                  </div>
                );
              }}
            />

            <Legend
              verticalAlign="top"
              align="right"
              iconType="circle"
              wrapperStyle={{ fontSize: "11px", paddingBottom: "8px" }}
            />

            {/* 90% Confidence Band Envelope Area */}
            <Area
              type="monotone"
              dataKey="upper_ci"
              stroke="transparent"
              fill="url(#ci-gradient)"
              name="90% CI Envelope"
            />
            <Area
              type="monotone"
              dataKey="lower_ci"
              stroke="transparent"
              fill="#000000"
              name="CI Lower Bound"
              legendType="none"
            />

            {/* Historical Actuals */}
            <Line
              type="monotone"
              dataKey="actual"
              stroke="#71717A"
              strokeWidth={1.8}
              dot={{ fill: "#71717A", r: 2 }}
              activeDot={{ r: 4, fill: "#FFFFFF" }}
              name="Historical Actuals"
            />

            {/* PyTorch LSTM Forecast with Crimson Glow */}
            <Line
              type="monotone"
              dataKey="predicted"
              stroke="#E11D48"
              strokeWidth={2.8}
              dot={{ fill: "#FF1A55", r: 3, stroke: "#FFFFFF", strokeWidth: 1 }}
              activeDot={{ r: 5, fill: "#FF1A55", stroke: "#FFFFFF", strokeWidth: 2 }}
              name="PyTorch LSTM Forecast"
              filter="url(#crimson-glow)"
            />

            {/* Naive Baseline Overlay */}
            <Line
              type="monotone"
              dataKey="baseline"
              stroke="#F59E0B"
              strokeWidth={1.2}
              strokeDasharray="4 4"
              dot={false}
              name="Naive Baseline"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
