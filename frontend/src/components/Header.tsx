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
    <header className="w-full border-b border-zinc-800/80 bg-[#09090B] px-6 py-3">
      <div className="max-w-[1500px] mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-rose-950 border border-rose-800/60 flex items-center justify-center font-black text-rose-400 text-sm">
            N
          </div>
          <div>
            <h1 className="font-bold text-base tracking-tight text-white leading-tight">NAOMI</h1>
            <p className="text-[11px] text-zinc-400">Pricing & Demand Decision Engine</p>
          </div>
        </div>

        {/* Center: SKU Navigation Pills */}
        <div className="flex items-center gap-1.5 p-1 bg-[#121215] border border-zinc-800 rounded-xl overflow-x-auto max-w-full">
          {CURATED_SKUS.map((sku) => {
            const isSelected = sku.item_id === selectedSku.item_id;
            return (
              <button
                key={sku.item_id}
                onClick={() => onSelectSku(sku)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors whitespace-nowrap flex items-center gap-2 ${
                  isSelected
                    ? "bg-rose-950 border border-rose-700/60 text-white"
                    : "text-zinc-400 hover:text-zinc-200 border border-transparent"
                }`}
              >
                <span>{sku.item_name}</span>
                <span className={`text-[10px] font-mono px-1.5 py-0.2 rounded ${
                  isSelected ? "bg-rose-900/60 text-rose-200" : "bg-zinc-800 text-zinc-400"
                }`}>
                  ${sku.base_price.toFixed(2)}
                </span>
              </button>
            );
          })}
        </div>

        {/* Right: Horizon Selector */}
        <div className="flex items-center gap-1 p-1 bg-[#121215] border border-zinc-800 rounded-lg">
          <span className="text-[11px] text-zinc-400 px-2 font-medium">Horizon:</span>
          {horizons.map((h) => {
            const isActive = horizon === h.value;
            return (
              <button
                key={h.value}
                onClick={() => onSelectHorizon(h.value)}
                className={`px-2.5 py-1 rounded text-xs font-medium transition-colors ${
                  isActive
                    ? "bg-rose-900/80 text-white font-semibold"
                    : "text-zinc-400 hover:text-zinc-200"
                }`}
              >
                {h.label}
              </button>
            );
          })}
        </div>

      </div>
    </header>
  );
};
