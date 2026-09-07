import React from "react";
import { OptimizationData, SKUInfo } from "../types";

interface KpiHeroGridProps {
  optData: OptimizationData;
  sku: SKUInfo;
  horizon: number;
}

export const KpiHeroGrid: React.FC<KpiHeroGridProps> = ({
  optData,
  sku,
  horizon,
}) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3.5">
      
      {/* 1. Optimal Price (P*) */}
      <div className="rounded-xl border border-rose-900/50 bg-[#120D10] p-4 flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-rose-300 font-medium">
          <span>Optimal Price (P*)</span>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-rose-950 text-rose-300 border border-rose-800/40">
            {optData.price_change_pct >= 0 ? "+" : ""}{optData.price_change_pct.toFixed(1)}%
          </span>
        </div>
        <div className="text-2xl lg:text-3xl font-bold tracking-tight text-white my-1.5 font-mono">
          ${optData.optimal_price.toFixed(2)}
        </div>
        <div className="text-[11px] text-zinc-400 font-mono">
          Base: ${sku.base_price.toFixed(2)}
        </div>
      </div>

      {/* 2. Forecast Demand (Q*) */}
      <div className="rounded-xl border border-zinc-800/80 bg-[#0F0F12] p-4 flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-zinc-400 font-medium">
          <span>Forecast Demand</span>
          <span className="text-[10px] font-mono text-zinc-400">{horizon}D Average</span>
        </div>
        <div className="text-2xl lg:text-3xl font-bold tracking-tight text-white my-1.5 font-mono">
          {optData.optimal_demand.toFixed(1)} <span className="text-sm font-normal text-zinc-400">units</span>
        </div>
        <div className="text-[11px] text-zinc-400">
          Daily sales volume
        </div>
      </div>

      {/* 3. Projected Revenue */}
      <div className="rounded-xl border border-zinc-800/80 bg-[#0F0F12] p-4 flex flex-col justify-between">
        <div className="text-xs text-zinc-400 font-medium">
          Projected Revenue
        </div>
        <div className="text-2xl lg:text-3xl font-bold tracking-tight text-white my-1.5 font-mono">
          ${optData.optimal_revenue.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </div>
        <div className="text-[11px] text-zinc-400 font-mono">
          Gross receipts
        </div>
      </div>

      {/* 4. Projected Operating Profit */}
      <div className="rounded-xl border border-zinc-800/80 bg-[#0F0F12] p-4 flex flex-col justify-between">
        <div className="flex items-center justify-between text-xs text-zinc-400 font-medium">
          <span>Projected Profit</span>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-950 text-emerald-300 border border-emerald-800/40 font-bold">
            {optData.profit_uplift_pct >= 0 ? "+" : ""}{optData.profit_uplift_pct.toFixed(1)}% Uplift
          </span>
        </div>
        <div className="text-2xl lg:text-3xl font-bold tracking-tight text-white my-1.5 font-mono">
          ${optData.optimal_profit.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </div>
        <div className="text-[11px] text-zinc-400">
          Net operating margin
        </div>
      </div>

      {/* 5. Gross Margin & Breakeven */}
      <div className="rounded-xl border border-zinc-800/80 bg-[#0F0F12] p-4 flex flex-col justify-between col-span-2 md:col-span-1">
        <div className="flex items-center justify-between text-xs text-zinc-400 font-medium">
          <span>Gross Margin</span>
          <span className="text-[10px] font-mono text-zinc-400">BE: {optData.breakeven_units}u</span>
        </div>
        <div className="text-2xl lg:text-3xl font-bold tracking-tight text-white my-1.5 font-mono">
          {optData.gross_margin_pct.toFixed(1)}%
        </div>
        <div className="text-[11px] text-zinc-400 font-mono">
          Fixed overhead: ${optData.fixed_costs.toFixed(0)}
        </div>
      </div>

    </div>
  );
};
