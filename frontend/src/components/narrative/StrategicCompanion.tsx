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
        return "bg-emerald-950/80 border-emerald-700/60 text-emerald-300";
      case "Stable":
        return "bg-zinc-800 border-zinc-700 text-zinc-200";
      case "Moderate Risk":
        return "bg-amber-950/80 border-amber-700/60 text-amber-300";
      case "High Risk":
      case "Critical Risk":
        return "bg-rose-950 border-rose-700 text-rose-300";
    }
  };

  return (
    <div className="w-full h-full flex flex-col justify-between rounded-xl border border-zinc-800/80 bg-[#0F0F12] p-5">
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold tracking-tight text-white">
            Strategic Executive Brief
          </h3>
          <span
            className={`px-2 py-0.5 rounded text-xs font-mono font-bold border ${getRiskColor(
              simulation.risk_label
            )}`}
          >
            {simulation.risk_label}
          </span>
        </div>

        {/* Narrative Summary */}
        <p className="text-xs text-zinc-300 leading-relaxed bg-[#141418] border border-zinc-800/80 p-3 rounded-lg mb-3">
          {simulation.executive_brief}
        </p>

        {/* Structured Executive Metrics */}
        <div className="grid grid-cols-2 gap-2 text-xs font-mono">
          <div className="p-2.5 rounded-lg bg-[#141418] border border-zinc-800/60 flex flex-col">
            <span className="text-zinc-400 text-[10px]">Price Elasticity</span>
            <span className="font-bold text-white mt-0.5">
              Ed = {sku.historical_elasticity.toFixed(2)} ({sku.historical_elasticity < -1 ? "Elastic" : "Inelastic"})
            </span>
          </div>

          <div className="p-2.5 rounded-lg bg-[#141418] border border-zinc-800/60 flex flex-col">
            <span className="text-zinc-400 text-[10px]">Breakeven Volume</span>
            <span className="font-bold text-white mt-0.5">
              {simulation.shocked_kpis.breakeven_units} units
            </span>
          </div>
        </div>
      </div>

      <div className="mt-3 pt-2.5 border-t border-zinc-800/60 text-[10px] text-zinc-400">
        AI-assisted decision advisory • Non-binding C-suite recommendation
      </div>
    </div>
  );
};
