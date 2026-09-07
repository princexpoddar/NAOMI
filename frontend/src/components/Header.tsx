import React from "react";
import { SKUInfo } from "../types";
import { CURATED_SKUS } from "../services/api";

interface HeaderProps {
  selectedSku: SKUInfo;
  onSelectSku: (sku: SKUInfo) => void;
  horizon: number;
  onSelectHorizon: (h: number) => void;
}

export const Header: React.FC<HeaderProps> = ({
  selectedSku,
  onSelectSku,
  horizon,
  onSelectHorizon,
}) => {
  const horizons = [
    { label: "1D", value: 1 },
    { label: "7D", value: 7 },
    { label: "30D", value: 30 },
  ];

  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-[#0B0F19]/95 border-b border-slate-800/80 px-6 py-2.5 shadow-sm">
      <div className="max-w-[1500px] mx-auto flex flex-col md:flex-row items-center justify-between gap-3">
        
        {/* Brand & System Status */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-600 to-indigo-700 border border-blue-500/50 flex items-center justify-center font-black text-white text-sm shadow-sm">
            N
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="font-bold text-base tracking-tight text-white leading-tight font-display">NAOMI</h1>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800/90 text-slate-300 border border-slate-700/50">
                Decision Companion
              </span>
            </div>
            <p className="text-[11px] text-slate-400">Neural Analytics & Market Intelligence</p>
          </div>
        </div>

        {/* Center: SKU Navigation Pills */}
        <div className="flex items-center gap-1.5 p-1 bg-[#111827] border border-slate-800/90 rounded-xl overflow-x-auto max-w-full no-scrollbar">
          {CURATED_SKUS.map((sku) => {
            const isSelected = sku.item_id === selectedSku.item_id;
            return (
              <button
                key={sku.item_id}
                onClick={() => onSelectSku(sku)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all whitespace-nowrap flex items-center gap-2 ${
                  isSelected
                    ? "bg-gradient-to-r from-blue-950 to-blue-900 border border-blue-600/70 text-white shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50 border border-transparent"
                }`}
              >
                <span className={`text-[9px] font-mono uppercase px-1 rounded ${
                  isSelected ? "bg-blue-800 text-blue-200" : "bg-slate-800 text-slate-400"
                }`}>
                  {sku.category}
                </span>
                <span>{sku.item_name}</span>
                <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded ${
                  isSelected ? "bg-blue-900/80 text-blue-200 font-bold" : "bg-slate-800 text-slate-400"
                }`}>
                  ${sku.base_price.toFixed(2)}
                </span>
              </button>
            );
          })}
        </div>

        {/* Right: Horizon Selector */}
        <div className="flex items-center gap-1.5">
          <div className="flex items-center gap-1 p-1 bg-[#111827] border border-slate-800/90 rounded-lg">
            <span className="text-[11px] text-slate-400 px-2 font-medium">Horizon:</span>
            {horizons.map((h) => {
              const isActive = horizon === h.value;
              return (
                <button
                  key={h.value}
                  onClick={() => onSelectHorizon(h.value)}
                  className={`px-2.5 py-1 rounded text-xs font-medium transition-all ${
                    isActive
                      ? "bg-blue-600 border border-blue-500 text-white font-semibold shadow-sm"
                      : "text-slate-400 hover:text-slate-200"
                  }`}
                >
                  {h.label}
                </button>
              );
            })}
          </div>
        </div>

      </div>
    </header>
  );
};
