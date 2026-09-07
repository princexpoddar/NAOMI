import React from "react";
import { Sparkles, ShieldCheck, AlertOctagon, Info } from "lucide-react";
import { SimulationResult, SKUInfo } from "../../types";
import { BorderBeam } from "../ui/BorderBeam";

interface StrategicCompanionProps {
  simulation: SimulationResult;
  sku: SKUInfo;
}

export const StrategicCompanion: React.FC<StrategicCompanionProps> = ({
  simulation,
  sku,
}) => {
  const getRiskBadge = (risk: SimulationResult["risk_label"]) => {
    switch (risk) {
      case "Positive":
        return {
          bg: "bg-emerald-950/80 border-emerald-500/50 text-emerald-300",
          icon: ShieldCheck,
        };
      case "Stable":
        return {
          bg: "bg-sky-950/80 border-sky-500/50 text-sky-300",
          icon: ShieldCheck,
        };
      case "Moderate Risk":
        return {
          bg: "bg-amber-950/80 border-amber-500/50 text-amber-300",
          icon: AlertOctagon,
        };
      case "High Risk":
        return {
          bg: "bg-crimson-950/80 border-crimson-500/50 text-crimson-300",
          icon: AlertOctagon,
        };
      case "Critical Risk":
        return {
          bg: "bg-red-950 border-red-500 text-red-100 animate-pulse",
          icon: AlertOctagon,
        };
    }
  };

  const riskInfo = getRiskBadge(simulation.risk_label);
  const RiskIcon = riskInfo.icon;

  return (
    <div className="relative w-full h-full flex flex-col justify-between p-5 rounded-2xl bg-gradient-to-b from-crimson-950/20 via-obsidian-150 to-pitch-black border border-crimson-500/20 overflow-hidden shadow-crimson-sm">
      <BorderBeam size={160} duration={8} borderWidth={1} colorFrom="#FF1A55" colorTo="#E11D48" />

      <div>
        {/* Header with Title & Dynamic Risk Pill */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <div className="w-7 h-7 rounded-lg bg-crimson-900/40 border border-crimson-500/30 flex items-center justify-center text-crimson-400">
              <Sparkles className="w-4 h-4" />
            </div>
            <div>
              <h3 className="text-sm font-bold tracking-tight text-white">
                Strategic Decision Companion
              </h3>
              <p className="text-[10px] text-zinc-400 font-mono">
                Real-Time C-Suite Advisory Intelligence
              </p>
            </div>
          </div>

          <div
            className={`flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-bold border tracking-wide font-mono ${riskInfo.bg}`}
          >
            <RiskIcon className="w-3.5 h-3.5" />
            <span>{simulation.risk_label}</span>
          </div>
        </div>

        {/* Narrative Content Body */}
        <div className="space-y-3 font-sans text-xs leading-relaxed text-zinc-300">
          <p className="p-3 rounded-xl bg-obsidian-200/90 border border-white/5 text-zinc-200">
            {simulation.executive_brief}
          </p>

          <div className="grid grid-cols-2 gap-2 pt-1 font-mono text-[11px]">
            <div className="p-2.5 rounded-lg bg-obsidian-200/60 border border-white/5 flex flex-col gap-0.5">
              <span className="text-zinc-400 text-[10px] uppercase">Elasticity Profile</span>
              <span className="font-bold text-crimson-300">
                Ed = {sku.historical_elasticity.toFixed(2)} ({sku.historical_elasticity < -1 ? "Elastic" : "Inelastic"})
              </span>
            </div>
            <div className="p-2.5 rounded-lg bg-obsidian-200/60 border border-white/5 flex flex-col gap-0.5">
              <span className="text-zinc-400 text-[10px] uppercase">Breakeven Volume</span>
              <span className="font-bold text-white">
                {simulation.shocked_kpis.breakeven_units} units (${(simulation.shocked_kpis.breakeven_units * simulation.candidate_price).toFixed(0)})
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Compliance Disclaimer Footer */}
      <div className="mt-4 pt-3 border-t border-white/5 flex items-center gap-2 text-[10px] text-zinc-400 font-mono">
        <Info className="w-3.5 h-3.5 flex-shrink-0 text-zinc-400" />
        <span>Notice: AI-assisted strategic guidance; non-binding C-suite recommendation.</span>
      </div>
    </div>
  );
};
