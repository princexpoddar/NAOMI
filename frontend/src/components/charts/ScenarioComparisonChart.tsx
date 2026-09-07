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
      metric: "Demand",
      Baseline: simulation.baseline_kpis.demand,
      Simulated: simulation.shocked_kpis.demand,
    },
    {
      metric: "Revenue ($)",
      Baseline: simulation.baseline_kpis.revenue,
      Simulated: simulation.shocked_kpis.revenue,
    },
    {
      metric: "Profit ($)",
      Baseline: simulation.baseline_kpis.gross_profit,
      Simulated: simulation.shocked_kpis.gross_profit,
    },
  ];

  return (
    <div className="w-full h-full flex flex-col justify-between">
      <div className="mb-2">
        <h3 className="text-sm font-semibold tracking-tight text-white">
          Scenario Impact vs. Baseline
        </h3>
        <p className="text-[11px] text-zinc-400">
          Financial impact of active simulation parameters
        </p>
      </div>

      <div className="w-full h-[250px] min-h-[250px]">
        <ResponsiveContainer width="100%" height="100%" minHeight={250}>
          <BarChart data={data} margin={{ top: 10, right: 10, left: -15, bottom: 0 }}>
            <CartesianGrid strokeDasharray="2 2" stroke="#27272A" vertical={false} opacity={0.4} />

            <XAxis
              dataKey="metric"
              stroke="#52525B"
              tick={{ fill: "#A1A1AA", fontSize: 11 }}
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
                  <div className="rounded-lg border border-zinc-800 bg-[#121215] p-2.5 shadow-lg text-xs">
                    <p className="font-mono text-zinc-400 font-bold mb-1">{label}</p>
                    {payload.map((entry, idx) => (
                      <div key={idx} className="flex items-center justify-between gap-3 py-0.5">
                        <span className="text-zinc-400">{entry.name}:</span>
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

            <Bar
              dataKey="Baseline"
              name="Baseline"
              fill="#3F3F46"
              radius={[3, 3, 0, 0]}
            />
            <Bar
              dataKey="Simulated"
              name="Simulated"
              fill="#BE123C"
              radius={[3, 3, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
