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
  const data: Array<{
    date: string;
    actual?: number;
    predicted?: number;
    lower_ci?: number;
    upper_ci?: number;
    baseline?: number;
  }> = [];

  const recentHistory = historical.slice(-18);
  recentHistory.forEach((h) => {
    data.push({
      date: h.date.slice(5),
      actual: h.actual,
    });
  });

  if (recentHistory.length > 0 && forecast.y_pred.length > 0) {
    const lastHist = recentHistory[recentHistory.length - 1];
    data[data.length - 1].predicted = lastHist.actual;
    data[data.length - 1].lower_ci = lastHist.actual;
    data[data.length - 1].upper_ci = lastHist.actual;
  }

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
      <div className="flex items-center justify-between mb-2">
        <div>
          <h3 className="text-sm font-semibold tracking-tight text-white">
            Demand Forecast & 90% Confidence Interval
          </h3>
          <p className="text-[11px] text-zinc-400">
            {sku.item_name} • Historical sales vs. model forecast
          </p>
        </div>
      </div>

      <div className="w-full h-[260px] min-h-[260px]">
        <ResponsiveContainer width="100%" height="100%" minHeight={260}>
          <ComposedChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="2 2" stroke="#1E293B" vertical={false} opacity={0.6} />

            <XAxis
              dataKey="date"
              stroke="#475569"
              tick={{ fill: "#94A3B8", fontSize: 10, fontFamily: "JetBrains Mono" }}
              tickLine={false}
              axisLine={{ stroke: "#1E293B" }}
            />
            <YAxis
              stroke="#475569"
              tick={{ fill: "#94A3B8", fontSize: 10, fontFamily: "JetBrains Mono" }}
              tickLine={false}
              axisLine={false}
            />

            <Tooltip
              content={({ active, payload, label }) => {
                if (!active || !payload || !payload.length) return null;
                return (
                  <div className="rounded-lg border border-slate-800 bg-[#111827] p-2.5 shadow-xl text-xs">
                    <p className="font-mono text-slate-400 mb-1">{label}</p>
                    {payload.map((entry, idx) => (
                      <div key={idx} className="flex items-center justify-between gap-3 py-0.5">
                        <span className="text-slate-300" style={{ color: entry.color }}>
                          {entry.name}:
                        </span>
                        <span className="font-mono font-bold text-white">
                          {Number(entry.value).toFixed(1)}
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
              wrapperStyle={{ fontSize: "11px", paddingBottom: "6px" }}
            />

            {/* Confidence Band Envelope */}
            <Area
              type="monotone"
              dataKey="upper_ci"
              stroke="transparent"
              fill="#3B82F6"
              fillOpacity={0.12}
              name="90% Confidence Band"
            />
            <Area
              type="monotone"
              dataKey="lower_ci"
              stroke="transparent"
              fill="#0B0F19"
              name="CI Lower Bound"
              legendType="none"
            />

            {/* Historical Actuals */}
            <Line
              type="monotone"
              dataKey="actual"
              stroke="#64748B"
              strokeWidth={1.5}
              dot={{ fill: "#94A3B8", r: 1.5 }}
              name="Historical Actuals"
            />

            {/* Forecast Line */}
            <Line
              type="monotone"
              dataKey="predicted"
              stroke="#3B82F6"
              strokeWidth={2.2}
              dot={{ fill: "#3B82F6", r: 2.5 }}
              name="Demand Forecast"
            />

            {/* Baseline */}
            <Line
              type="monotone"
              dataKey="baseline"
              stroke="#F59E0B"
              strokeWidth={1.2}
              strokeDasharray="3 3"
              dot={false}
              name="Baseline Average"
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
