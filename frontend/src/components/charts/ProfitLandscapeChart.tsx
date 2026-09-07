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
  // Build chart points from 100-point grid sweep
  const data = optData.curve_prices.map((p, i) => ({
    price: p,
    profit: optData.curve_profits[i],
    revenue: optData.curve_revenues[i],
  }));

  return (
    <div className="w-full h-full flex flex-col">
      <div className="flex items-center justify-between mb-3 px-1">
        <div>
          <h3 className="text-sm font-bold tracking-tight text-white flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-emerald-500 shadow-sm" />
            Profit & Revenue vs. Price Landscape
          </h3>
          <p className="text-[11px] text-zinc-400 font-mono">
            Empirical Concave Sweep • argmax Π(P) = (P - c)Q(P) - F
          </p>
        </div>
        <div className="text-[11px] font-mono text-emerald-400 bg-emerald-950/70 border border-emerald-600/40 px-2 py-0.5 rounded">
          Optimal P*: ${optData.optimal_price.toFixed(2)} (+{optData.profit_uplift_pct.toFixed(1)}% Π)
        </div>
      </div>

      <div className="w-full h-[280px]">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
            <defs>
              {/* Profit Curve Fill Gradient */}
              <linearGradient id="profit-gradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#E11D48" stopOpacity={0.35} />
                <stop offset="100%" stopColor="#881337" stopOpacity={0.02} />
              </linearGradient>

              {/* Crimson Glow */}
              <filter id="profit-glow" x="-20%" y="-20%" width="140%" height="140%">
                <feGaussianBlur stdDeviation="3" result="blur" />
                <feMerge>
                  <feMergeNode in="blur" />
                  <feMergeNode in="SourceGraphic" />
                </feMerge>
              </filter>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#27272A" vertical={false} opacity={0.4} />

            <XAxis
              dataKey="price"
              stroke="#52525B"
              tickFormatter={(val) => `$${Number(val).toFixed(2)}`}
              tick={{ fill: "#71717A", fontSize: 10, fontFamily: "JetBrains Mono" }}
              tickLine={false}
              axisLine={{ stroke: "#27272A" }}
            />
            <YAxis
              stroke="#52525B"
              tickFormatter={(val) => `$${Number(val).toFixed(0)}`}
              tick={{ fill: "#71717A", fontSize: 10, fontFamily: "JetBrains Mono" }}
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
                  <div className="rounded-xl border border-crimson-600/30 bg-pitch-black/95 p-3 shadow-crimson-md backdrop-blur-xl text-xs">
                    <p className="font-mono text-zinc-300 font-bold mb-1">Price: ${Number(p).toFixed(2)}</p>
                    <div className="flex items-center justify-between gap-4 py-0.5">
                      <span className="text-crimson-400 font-medium">Projected Profit:</span>
                      <span className="font-mono font-bold text-white">${Number(profit).toFixed(2)}</span>
                    </div>
                    <div className="flex items-center justify-between gap-4 py-0.5">
                      <span className="text-indigo-400 font-medium">Gross Revenue:</span>
                      <span className="font-mono font-bold text-white">${Number(revenue).toFixed(2)}</span>
                    </div>
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

            {/* Gross Revenue Curve (Dashed Indigo) */}
            <Line
              type="monotone"
              dataKey="revenue"
              stroke="#818CF8"
              strokeWidth={1.8}
              strokeDasharray="4 4"
              dot={false}
              name="Gross Revenue R(P)"
            />

            {/* Projected Profit Curve (Crimson Neon with Area Gradient) */}
            <Area
              type="monotone"
              dataKey="profit"
              stroke="#E11D48"
              strokeWidth={2.6}
              fill="url(#profit-gradient)"
              name="Projected Profit Π(P)"
              filter="url(#profit-glow)"
            />

            {/* Vertical Marker at Optimal P* */}
            <ReferenceLine
              x={optData.optimal_price}
              stroke="#F59E0B"
              strokeDasharray="3 3"
              strokeWidth={1.5}
              label={{
                value: `P* = $${optData.optimal_price.toFixed(2)}`,
                fill: "#FCD34D",
                fontSize: 10,
                position: "top",
                fontFamily: "JetBrains Mono",
              }}
            />

            {/* Star Marker at Peak Profit */}
            <ReferenceDot
              x={optData.optimal_price}
              y={optData.optimal_profit}
              r={5}
              fill="#F59E0B"
              stroke="#FFFFFF"
              strokeWidth={1.5}
            />

            {/* Baseline P0 Diamond Marker */}
            <ReferenceDot
              x={sku.base_price}
              y={
                optData.curve_profits[
                  optData.curve_prices.findIndex((p) => Math.abs(p - sku.base_price) < 0.05) || 0
                ]
              }
              r={4}
              fill="#71717A"
              stroke="#E4E4E7"
              strokeWidth={1}
            />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
