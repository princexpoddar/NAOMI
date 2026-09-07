import React from "react";
import { motion } from "framer-motion";
import { Activity, ShieldCheck, Zap, Layers, Sparkles } from "lucide-react";
import { SKUInfo } from "../types";
import { CURATED_SKUS } from "../services/api";
import { ShinyText } from "./ui/ShinyText";

interface HeaderProps {
  selectedSku: SKUInfo;
  onSelectSku: (sku: SKUInfo) => void;
  horizon: number;
  onSelectHorizon: (h: number) => void;
  isApiOnline: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  selectedSku,
  onSelectSku,
  horizon,
  onSelectHorizon,
  isApiOnline,
}) => {
  const horizons = [
    { label: "1D Horizon", value: 1 },
    { label: "7D Horizon", value: 7 },
    { label: "30D Horizon", value: 30 },
  ];

  return (
    <header className="sticky top-0 z-40 w-full border-b border-white/5 bg-pitch-black/80 backdrop-blur-2xl px-4 lg:px-8 py-3.5 transition-all">
      <div className="max-w-[1600px] mx-auto flex flex-col xl:flex-row items-center justify-between gap-4">
        
        {/* Left: Brand Identity & Live Engine Badge */}
        <div className="flex items-center gap-4 w-full xl:w-auto justify-between xl:justify-start">
          <div className="flex items-center gap-3">
            <div className="relative flex items-center justify-center w-10 h-10 rounded-xl bg-gradient-to-br from-crimson-600 via-crimson-800 to-pitch-black border border-crimson-500/40 shadow-crimson-sm">
              <Zap className="w-5 h-5 text-white animate-pulse" />
              <div className="absolute -inset-0.5 rounded-xl bg-crimson-500/30 blur-sm -z-10" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-xl tracking-wider text-white">NAOMI</span>
                <span className="text-[10px] uppercase font-bold tracking-widest px-2 py-0.5 rounded-full bg-crimson-950/80 border border-crimson-700/60 text-crimson-400">
                  C-Suite 2.0
                </span>
              </div>
              <p className="text-[11px] font-medium tracking-wide text-zinc-400">
                <ShinyText text="Neural Analytics for Optimization & Market Intelligence" />
              </p>
            </div>
          </div>

          {/* Live Status Badge */}
          <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-obsidian-200 border border-white/10 text-xs">
            <span
              className={`w-2 h-2 rounded-full ${
                isApiOnline ? "bg-emerald-500 animate-ping" : "bg-crimson-500"
              }`}
            />
            <span className="text-[11px] font-mono text-zinc-300">
              {isApiOnline ? "FastAPI Online :8000" : "Client Engine Standalone"}
            </span>
          </div>
        </div>

        {/* Center: SKU Navigation Pills */}
        <div className="flex items-center gap-1.5 p-1 bg-obsidian-200/90 border border-white/5 rounded-2xl overflow-x-auto max-w-full">
          {CURATED_SKUS.map((sku) => {
            const isSelected = sku.item_id === selectedSku.item_id;
            return (
              <button
                key={sku.item_id}
                onClick={() => onSelectSku(sku)}
                className={`relative px-3 py-2 rounded-xl text-xs font-medium transition-all whitespace-nowrap flex items-center gap-2 ${
                  isSelected ? "text-white" : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {isSelected && (
                  <motion.div
                    layoutId="active-sku-pill"
                    className="absolute inset-0 rounded-xl bg-gradient-to-r from-crimson-950/80 via-crimson-900/60 to-obsidian-300 border border-crimson-500/50 shadow-crimson-sm"
                    transition={{ type: "spring", stiffness: 380, damping: 30 }}
                  />
                )}
                <span className="relative z-10 font-mono text-[11px] text-zinc-400">
                  {sku.category === "FOODS" ? "🥦" : sku.category === "HOUSEHOLD" ? "🧼" : "🎮"}
                </span>
                <span className="relative z-10 font-semibold tracking-tight">{sku.item_name}</span>
                <span className="relative z-10 text-[10px] font-mono text-crimson-300/80 bg-crimson-950/60 px-1.5 py-0.5 rounded">
                  ${sku.base_price.toFixed(2)}
                </span>
              </button>
            );
          })}
        </div>

        {/* Right: Forecast Horizon Selector */}
        <div className="flex items-center gap-1 p-1 bg-obsidian-200/90 border border-white/5 rounded-xl self-end xl:self-auto">
          {horizons.map((h) => {
            const isActive = horizon === h.value;
            return (
              <button
                key={h.value}
                onClick={() => onSelectHorizon(h.value)}
                className={`relative px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  isActive ? "text-white font-semibold" : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {isActive && (
                  <motion.div
                    layoutId="active-horizon"
                    className="absolute inset-0 rounded-lg bg-crimson-600 shadow-crimson-sm"
                    transition={{ type: "spring", stiffness: 450, damping: 32 }}
                  />
                )}
                <span className="relative z-10">{h.label}</span>
              </button>
            );
          })}
        </div>

      </div>
    </header>
  );
};
