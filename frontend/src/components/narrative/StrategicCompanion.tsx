import React from "react";
import { SimulationResult, SKUInfo } from "../../types";

interface StrategicCompanionProps {
  simulation: SimulationResult;
  sku: SKUInfo;
}

export const StrategicCompanion: React.FC<StrategicCompanionProps> = ({
  simulation,
  sku,
}) => {
  const getRiskColor = (risk: SimulationResult["risk_label"]) => {
    switch (risk) {
      case "Positive":
        return "bg-emerald-950/90 border-emerald-700/60 text-emerald-300";
      case "Stable":
        return "bg-zinc-800/90 border-zinc-700 text-zinc-200";
      case "Moderate Risk":
        return "bg-amber-950/90 border-amber-700/60 text-amber-300";
      case "High Risk":
      case "Critical Risk":
        return "bg-rose-950/90 border-rose-700 text-rose-300";
    }
  };

  const profitDelta = simulation.shocked_kpis.gross_profit - simulation.baseline_kpis.gross_profit;

  return (
    <div className="w-full h-full flex flex-col justify-between rounded-xl border border-zinc-800/80 bg-gradient-to-b from-[#15151A] to-[#0E0E12] p-4 shadow-sm">
      <div>
        {/* Header */}
        <div className="flex items-center justify-between mb-2.5">
          <div>
            <h3 className="text-sm font-semibold tracking-tight text-white">
              Strategic Executive Brief
            </h3>
            <p className="text-[11px] text-zinc-400">Automated counterfactual scenario analysis</p>
          </div>
          <span
            className={`px-2.5 py-0.5 rounded-full text-xs font-mono font-bold border ${getRiskColor(
              simulation.risk_label
            )}`}
          >
            {simulation.risk_label}
          </span>
        </div>

        {/* Narrative Summary */}
        <div className="text-xs text-zinc-300 leading-relaxed bg-[#101014] border border-zinc-800/90 p-3 rounded-lg mb-3">
          {simulation.executive_brief}
        </div>

        {/* Structured Executive Metrics */}
        <div className="grid grid-cols-3 gap-2 text-xs font-mono">
          <div className="p-2 rounded-lg bg-[#101014] border border-zinc-800/70 flex flex-col">
            <span className="text-zinc-400 text-[10px]">Price Elasticity</span>
            <span className="font-bold text-white mt-0.5 text-[11px]">
              Ed = {sku.historical_elasticity.toFixed(2)}
            </span>
            <span className="text-[10px] text-zinc-400 font-sans">
              {sku.historical_elasticity < -1 ? "Elastic" : "Inelastic"}
            </span>
          </div>

          <div className="p-2 rounded-lg bg-[#101014] border border-zinc-800/70 flex flex-col">
            <span className="text-zinc-400 text-[10px]">Breakeven Volume</span>
            <span className="font-bold text-white mt-0.5 text-[11px]">
              {simulation.shocked_kpis.breakeven_units} u/day
            </span>
            <span className="text-[10px] text-zinc-400 font-sans">Target threshold</span>
          </div>

          <div className="p-2 rounded-lg bg-[#101014] border border-zinc-800/70 flex flex-col">
            <span className="text-zinc-400 text-[10px]">Profit Delta</span>
            <span className={`font-bold mt-0.5 text-[11px] ${profitDelta >= 0 ? "text-emerald-400" : "text-rose-400"}`}>
              {profitDelta >= 0 ? "+" : ""}${profitDelta.toFixed(2)}/d
            </span>
            <span className="text-[10px] text-zinc-400 font-sans">vs. Baseline</span>
          </div>
        </div>
      </div>

      <div className="mt-2.5 pt-2 border-t border-zinc-800/70 text-[10px] text-zinc-400 flex items-center justify-between">
        <span>AI-assisted decision advisory</span>
        <span className="text-zinc-400 font-mono">Non-binding recommendation</span>
      </div>
    </div>
  );
};
