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
  ReferenceLine,
  ReferenceDot,
  Legend,
} from "recharts";
import { OptimizationData, SKUInfo } from "../../types";

interface ProfitLandscapeChartProps {
  optData: OptimizationData;
  sku: SKUInfo;
}

export const ProfitLandscapeChart: React.FC<ProfitLandscapeChartProps> = ({
  optData,
  sku,
}) => {
  const data = optData.curve_prices.map((p, i) => ({
    price: p,
    profit: optData.curve_profits[i],
    revenue: optData.curve_revenues[i],
  }));

  return (
    <div className="w-full h-full flex flex-col">
      <div className="flex items-center justify-between mb-2">
        <div>
          <h3 className="text-sm font-semibold tracking-tight text-white">
            Profit & Revenue Optimization Curve
          </h3>
          <p className="text-[11px] text-slate-400">
            Profit maximization across candidate price range
          </p>
        </div>
        <span className="text-[11px] font-mono text-blue-300 bg-blue-950/80 border border-blue-800/50 px-2 py-0.5 rounded">
          Optimal: ${optData.optimal_price.toFixed(2)}
        </span>
      </div>

      <div className="w-full h-[260px] min-h-[260px]">
        <ResponsiveContainer width="100%" height="100%" minHeight={260}>
          <ComposedChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <CartesianGrid strokeDasharray="2 2" stroke="#1E293B" vertical={false} opacity={0.6} />

            <XAxis
              dataKey="price"
              stroke="#475569"
              tickFormatter={(val) => `$${Number(val).toFixed(2)}`}
              tick={{ fill: "#94A3B8", fontSize: 10, fontFamily: "JetBrains Mono" }}
              tickLine={false}
              axisLine={{ stroke: "#1E293B" }}
            />
            <YAxis
              stroke="#475569"
              tickFormatter={(val) => `$${Number(val).toFixed(0)}`}
              tick={{ fill: "#94A3B8", fontSize: 10, fontFamily: "JetBrains Mono" }}
              tickLine={false}
              axisLine={false}
            />

            <Tooltip
              content={({ active, payload }) => {
                if (!active || !payload || !payload.length) return null;
                const p = payload[0].payload.price;
                const profit = payload[0].payload.profit;
                const revenue = payload[0].payload.revenue;
                return (
                  <div className="rounded-lg border border-slate-800 bg-[#111827] p-2.5 shadow-xl text-xs">
                    <p className="font-mono text-slate-300 font-bold mb-1">Price: ${Number(p).toFixed(2)}</p>
                    <div className="flex items-center justify-between gap-3 py-0.5">
                      <span className="text-slate-400">Operating Profit:</span>
                      <span className="font-mono font-bold text-emerald-400">${Number(profit).toFixed(2)}</span>
                    </div>
                    <div className="flex items-center justify-between gap-3 py-0.5">
                      <span className="text-slate-400">Gross Revenue:</span>
                      <span className="font-mono font-bold text-blue-400">${Number(revenue).toFixed(2)}</span>
                    </div>
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

            {/* Gross Revenue Curve */}
            <Line
              type="monotone"
              dataKey="revenue"
              stroke="#3B82F6"
              strokeWidth={1.5}
              strokeDasharray="3 3"
              dot={false}
              name="Gross Revenue"
            />

            {/* Projected Profit Curve */}
            <Area
              type="monotone"
              dataKey="profit"
              stroke="#10B981"
              strokeWidth={2.2}
              fill="#10B981"
              fillOpacity={0.12}
              name="Operating Profit"
            />

            {/* Optimal Price Vertical Reference */}
            <ReferenceLine
              x={optData.optimal_price}
              stroke="#F59E0B"
              strokeDasharray="2 2"
              strokeWidth={1.2}
              label={{
                value: `P* = $${optData.optimal_price.toFixed(2)}`,
                fill: "#FCD34D",
                fontSize: 10,
                position: "top",
                fontFamily: "JetBrains Mono",
              }}
            />

            {/* Peak Dot */}
            <ReferenceDot
              x={optData.optimal_price}
              y={optData.optimal_profit}
              r={4}
              fill="#10B981"
              stroke="#FFFFFF"
              strokeWidth={1.5}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
