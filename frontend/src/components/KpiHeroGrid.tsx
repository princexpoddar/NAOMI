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
  const baseDemand = optData.optimal_demand / Math.pow(optData.optimal_price / sku.base_price, sku.historical_elasticity);
  const demandDeltaPct = ((optData.optimal_demand - baseDemand) / baseDemand) * 100;
  const horizonRevenue = optData.optimal_revenue * horizon;

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3.5">
      
      {/* 1. Optimal Price (P*) */}
      <div className="rounded-xl border border-blue-700/60 bg-gradient-to-b from-[#16223D] to-[#0F1626] p-4 flex flex-col justify-between shadow-sm transition-all">
        <div className="flex items-center justify-between text-xs text-blue-300 font-medium">
          <span>Optimal Price (P*)</span>
          <span className="text-[10px] font-mono font-bold px-2 py-0.5 rounded-full bg-blue-950/90 text-blue-300 border border-blue-700/50">
            {optData.price_change_pct >= 0 ? "+" : ""}{optData.price_change_pct.toFixed(1)}%
          </span>
        </div>
        <div className="my-2">
          <span className="text-2xl lg:text-3xl font-bold tracking-tight text-white font-mono">
            ${optData.optimal_price.toFixed(2)}
          </span>
        </div>
        <div className="text-[11px] text-slate-400 font-mono flex items-center justify-between">
          <span>Base: ${sku.base_price.toFixed(2)}</span>
          <span className="text-blue-400">Inflection P*</span>
        </div>
      </div>

      {/* 2. Target Demand (Q*) */}
      <div className="rounded-xl border border-slate-800/80 bg-gradient-to-b from-[#131B2E] to-[#0E1524] p-4 flex flex-col justify-between shadow-sm hover:border-slate-700/80 transition-all">
        <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
          <span>Target Demand (Q*)</span>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800/80 text-slate-400 border border-slate-700/50">
            {horizon}D Horizon
          </span>
        </div>
        <div className="my-2">
          <span className="text-2xl lg:text-3xl font-bold tracking-tight text-white font-mono">
            {optData.optimal_demand.toFixed(1)}
          </span>
          <span className="text-xs font-normal text-slate-400 ml-1.5">units/day</span>
        </div>
        <div className="text-[11px] text-slate-400 font-mono">
          <span>{demandDeltaPct >= 0 ? "+" : ""}{demandDeltaPct.toFixed(1)}% volume impact</span>
        </div>
      </div>

      {/* 3. Projected Daily Revenue */}
      <div className="rounded-xl border border-slate-800/80 bg-gradient-to-b from-[#131B2E] to-[#0E1524] p-4 flex flex-col justify-between shadow-sm hover:border-slate-700/80 transition-all">
        <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
          <span>Projected Revenue</span>
          <span className="text-[10px] font-mono text-slate-400">${horizonRevenue.toFixed(0)}/{horizon}D</span>
        </div>
        <div className="my-2">
          <span className="text-2xl lg:text-3xl font-bold tracking-tight text-white font-mono">
            ${optData.optimal_revenue.toFixed(2)}
          </span>
          <span className="text-xs font-normal text-slate-400 ml-1.5">/day</span>
        </div>
        <div className="text-[11px] text-slate-400 font-mono">
          <span>Gross receipts at P*</span>
        </div>
      </div>

      {/* 4. Operating Profit (Pi*) */}
      <div className="rounded-xl border border-emerald-800/60 bg-gradient-to-b from-[#0F261E] to-[#0A1914] p-4 flex flex-col justify-between shadow-sm hover:border-emerald-700/80 transition-all">
        <div className="flex items-center justify-between text-xs text-emerald-300 font-medium">
          <span>Operating Profit (Π*)</span>
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-950/90 text-emerald-300 border border-emerald-700/50 font-bold">
            +{optData.profit_uplift_pct.toFixed(1)}% Uplift
          </span>
        </div>
        <div className="my-2">
          <span className="text-2xl lg:text-3xl font-bold tracking-tight text-emerald-400 font-mono">
            +${optData.optimal_profit.toFixed(2)}
          </span>
          <span className="text-xs font-normal text-emerald-400/80 ml-1.5">/day</span>
        </div>
        <div className="text-[11px] text-slate-400 font-mono">
          <span>Net of allocated overhead</span>
        </div>
      </div>

      {/* 5. Gross Margin & Breakeven */}
      <div className="rounded-xl border border-slate-800/80 bg-gradient-to-b from-[#131B2E] to-[#0E1524] p-4 flex flex-col justify-between col-span-2 md:col-span-1 shadow-sm hover:border-slate-700/80 transition-all">
        <div className="flex items-center justify-between text-xs text-slate-400 font-medium">
          <span>Gross Margin</span>
          <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800/80 text-slate-300 border border-slate-700/50">
            BE: {optData.breakeven_units}u/d
          </span>
        </div>
        <div className="my-2">
          <span className="text-2xl lg:text-3xl font-bold tracking-tight text-white font-mono">
            {optData.gross_margin_pct.toFixed(1)}%
          </span>
        </div>
        <div className="text-[11px] text-slate-400 font-mono">
          <span>Unit contrib: ${(optData.optimal_price - sku.base_price * 0.6).toFixed(2)}</span>
        </div>
      </div>

    </div>
  );
};
