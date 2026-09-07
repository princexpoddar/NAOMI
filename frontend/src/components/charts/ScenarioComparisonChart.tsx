import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";
import { SimulationResult } from "../../types";

interface ScenarioComparisonChartProps {
  simulation: SimulationResult;
}

export const ScenarioComparisonChart: React.FC<ScenarioComparisonChartProps> = ({
  simulation,
}) => {
  const data = [
    {
      metric: "Demand (Units)",
      Baseline: simulation.baseline_kpis.demand,
      Shocked: simulation.shocked_kpis.demand,
    },
    {
      metric: "Revenue ($)",
      Baseline: simulation.baseline_kpis.revenue,
      Shocked: simulation.shocked_kpis.revenue,
    },
    {
      metric: "Gross Profit ($)",
      Baseline: simulation.baseline_kpis.gross_profit,
      Shocked: simulation.shocked_kpis.gross_profit,
    },
  ];

  return (
    <div className="w-full h-full flex flex-col">
      <div className="flex items-center justify-between mb-2 px-1">
        <div>
          <h3 className="text-sm font-bold tracking-tight text-white flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-crimson-500 shadow-sm" />
            Counterfactual Shock Impact Comparison
          </h3>
          <p className="text-[11px] text-zinc-400 font-mono">
            Baseline Operating State vs. {simulation.scenario_type}
          </p>
        </div>
      </div>

      <div className="w-full h-[250px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#27272A" vertical={false} opacity={0.35} />

            <XAxis
              dataKey="metric"
              stroke="#52525B"
              tick={{ fill: "#A1A1AA", fontSize: 11, fontFamily: "Inter, sans-serif" }}
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
                    <p className="font-mono text-zinc-300 font-bold mb-1">{label}</p>
                    {payload.map((entry, idx) => (
                      <div key={idx} className="flex items-center justify-between gap-4 py-0.5">
                        <span className="font-medium" style={{ color: entry.color }}>
                          {entry.name}:
                        </span>
                        <span className="font-mono font-bold text-white">
                          {Number(entry.value).toLocaleString(undefined, { maximumFractionDigits: 1 })}
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

            {/* Baseline Bars */}
            <Bar
              dataKey="Baseline"
              name="Baseline State"
              fill="#3F3F46"
              radius={[4, 4, 0, 0]}
            />

            {/* Shocked Scenario Bars */}
            <Bar
              dataKey="Shocked"
              name="Active Shock"
              fill="#E11D48"
              radius={[4, 4, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
