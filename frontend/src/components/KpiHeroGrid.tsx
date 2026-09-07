import React from "react";
import { motion } from "framer-motion";
import { Tag, Box, TrendingUp, Award, PieChart, Sparkles } from "lucide-react";
import { OptimizationData, SKUInfo } from "../types";
import { BorderBeam } from "./ui/BorderBeam";
import { AnimatedCounter } from "./ui/AnimatedCounter";
import { SpotlightCard } from "./ui/Spotlight";

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
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
      
      {/* 1. Optimal Recommended Price (P*) - Hero Card with Laser BorderBeam */}
      <SpotlightCard className="relative p-5 bg-gradient-to-b from-crimson-950/40 via-obsidian-100 to-pitch-black border-crimson-500/30 shadow-crimson-sm group">
        <BorderBeam size={180} duration={6} borderWidth={1.5} colorFrom="#FF1A55" colorTo="#E11D48" />
        
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-crimson-300 flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-crimson-400" />
            Optimal Price (P*)
          </span>
          <div className="w-7 h-7 rounded-lg bg-crimson-900/40 border border-crimson-500/30 flex items-center justify-center text-crimson-400">
            <Tag className="w-3.5 h-3.5" />
          </div>
        </div>

        <div className="text-3xl font-black tracking-tight text-white flex items-baseline gap-1 my-1">
          <AnimatedCounter
            value={optData.optimal_price}
            prefix="$"
            decimals={2}
            className="text-glow-crimson"
          />
        </div>

        <div className="flex items-center gap-2 mt-2">
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-crimson-900/60 text-crimson-300 border border-crimson-600/50">
            {optData.price_change_pct > 0 ? "+" : ""}
            {optData.price_change_pct.toFixed(1)}% vs Base
          </span>
          <span className="text-[11px] text-zinc-400 font-mono">
            Base: ${sku.base_price.toFixed(2)}
          </span>
        </div>
      </SpotlightCard>

      {/* 2. Forecasted Demand (Q*) */}
      <SpotlightCard className="p-5">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
            Forecast Demand (Q*)
          </span>
          <div className="w-7 h-7 rounded-lg bg-obsidian-200 border border-white/5 flex items-center justify-center text-zinc-400">
            <Box className="w-3.5 h-3.5" />
          </div>
        </div>

        <div className="text-3xl font-black tracking-tight text-white flex items-baseline gap-1 my-1">
          <AnimatedCounter
            value={optData.optimal_demand}
            decimals={1}
            suffix=" units"
          />
        </div>

        <div className="flex items-center gap-2 mt-2">
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-zinc-800 text-zinc-300 border border-white/10">
            {horizon}D Horizon Mean
          </span>
          <span className="text-[11px] text-zinc-400 font-mono">
            Daily run-rate
          </span>
        </div>
      </SpotlightCard>

      {/* 3. Projected Gross Revenue (R*) */}
      <SpotlightCard className="p-5">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
            Projected Revenue
          </span>
          <div className="w-7 h-7 rounded-lg bg-obsidian-200 border border-white/5 flex items-center justify-center text-indigo-400">
            <TrendingUp className="w-3.5 h-3.5" />
          </div>
        </div>

        <div className="text-3xl font-black tracking-tight text-white flex items-baseline gap-1 my-1">
          <AnimatedCounter
            value={optData.optimal_revenue}
            prefix="$"
            decimals={2}
          />
        </div>

        <div className="flex items-center gap-2 mt-2">
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-indigo-950/70 text-indigo-300 border border-indigo-500/30">
            P* × Q*
          </span>
          <span className="text-[11px] text-zinc-400 font-mono">
            Gross Receipts
          </span>
        </div>
      </SpotlightCard>

      {/* 4. Projected Operating Profit (Π*) */}
      <SpotlightCard className="p-5 bg-gradient-to-b from-emerald-950/20 via-obsidian-100 to-pitch-black border-emerald-500/20">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-emerald-300 flex items-center gap-1.5">
            <Award className="w-3.5 h-3.5 text-emerald-400" />
            Projected Profit (Π*)
          </span>
          <div className="w-7 h-7 rounded-lg bg-emerald-900/30 border border-emerald-500/30 flex items-center justify-center text-emerald-400">
            <Award className="w-3.5 h-3.5" />
          </div>
        </div>

        <div className="text-3xl font-black tracking-tight text-white flex items-baseline gap-1 my-1">
          <AnimatedCounter
            value={optData.optimal_profit}
            prefix="$"
            decimals={2}
          />
        </div>

        <div className="flex items-center gap-2 mt-2">
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-emerald-950/80 text-emerald-300 border border-emerald-500/40">
            {optData.profit_uplift_pct > 0 ? "+" : ""}
            {optData.profit_uplift_pct.toFixed(1)}% Uplift
          </span>
          <span className="text-[11px] text-zinc-400 font-mono">
            Net Margin
          </span>
        </div>
      </SpotlightCard>

      {/* 5. Gross Margin % & Breakeven Units */}
      <SpotlightCard className="p-5">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs font-semibold uppercase tracking-wider text-zinc-400">
            Gross Margin %
          </span>
          <div className="w-7 h-7 rounded-lg bg-obsidian-200 border border-white/5 flex items-center justify-center text-zinc-400">
            <PieChart className="w-3.5 h-3.5" />
          </div>
        </div>

        <div className="text-3xl font-black tracking-tight text-white flex items-baseline gap-1 my-1">
          <AnimatedCounter
            value={optData.gross_margin_pct}
            suffix="%"
            decimals={1}
          />
        </div>

        <div className="flex items-center gap-2 mt-2">
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-[11px] font-bold bg-zinc-800 text-zinc-200 border border-white/10">
            BE: {optData.breakeven_units} units
          </span>
          <span className="text-[11px] text-zinc-400 font-mono">
            Fixed: ${optData.fixed_costs.toFixed(0)}
          </span>
        </div>
      </SpotlightCard>

    </div>
  );
};
