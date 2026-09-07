import React from "react";
import { Sliders, RefreshCw, AlertTriangle, TrendingDown, ArrowUpRight, Flame } from "lucide-react";
import { SimulationSliders } from "../../types";
import { CustomSlider } from "./CustomSlider";

interface ScenarioControlsProps {
  sliders: SimulationSliders;
  onChangeSliders: (newSliders: SimulationSliders) => void;
}

export const ScenarioControls: React.FC<ScenarioControlsProps> = ({
  sliders,
  onChangeSliders,
}) => {
  const presets = [
    {
      id: "baseline",
      label: "Baseline",
      icon: RefreshCw,
      apply: () => onChangeSliders({ priceDeltaPct: 0, demandShockPct: 0, costSurgePct: 0, competitorDropPct: 0 }),
    },
    {
      id: "price_up",
      label: "Price +5%",
      icon: ArrowUpRight,
      apply: () => onChangeSliders({ priceDeltaPct: 5, demandShockPct: 0, costSurgePct: 0, competitorDropPct: 0 }),
    },
    {
      id: "macro_shock",
      label: "Macro -15%",
      icon: TrendingDown,
      apply: () => onChangeSliders({ priceDeltaPct: 0, demandShockPct: -15, costSurgePct: 0, competitorDropPct: 0 }),
    },
    {
      id: "cost_surge",
      label: "Cost +10%",
      icon: AlertTriangle,
      apply: () => onChangeSliders({ priceDeltaPct: 0, demandShockPct: 0, costSurgePct: 10, competitorDropPct: 0 }),
    },
    {
      id: "price_war",
      label: "Price War",
      icon: Flame,
      apply: () => onChangeSliders({ priceDeltaPct: 0, demandShockPct: 0, costSurgePct: 0, competitorDropPct: 10 }),
    },
    {
      id: "stagflation",
      label: "Stagflation",
      icon: AlertTriangle,
      apply: () => onChangeSliders({ priceDeltaPct: 0, demandShockPct: -8, costSurgePct: 10, competitorDropPct: 0 }),
    },
  ];

  const handleReset = () => {
    onChangeSliders({
      priceDeltaPct: 0,
      demandShockPct: 0,
      costSurgePct: 0,
      competitorDropPct: 0,
    });
  };

  return (
    <div className="w-full h-full flex flex-col justify-between p-1">
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Sliders className="w-4 h-4 text-crimson-400" />
            <h3 className="text-sm font-bold tracking-tight text-white">
              Counterfactual Simulation Engine
            </h3>
          </div>
          <button
            onClick={handleReset}
            className="flex items-center gap-1 text-[11px] font-mono text-zinc-400 hover:text-white px-2 py-0.5 rounded-md bg-obsidian-200 border border-white/5 transition-colors"
          >
            <RefreshCw className="w-3 h-3" />
            Reset
          </button>
        </div>

        {/* Instant Scenario Presets Grid */}
        <div className="grid grid-cols-3 sm:grid-cols-6 gap-1.5 mb-4">
          {presets.map((preset) => {
            const Icon = preset.icon;
            return (
              <button
                key={preset.id}
                onClick={preset.apply}
                className="flex flex-col items-center justify-center p-2 rounded-xl bg-obsidian-200/80 border border-white/5 hover:border-crimson-500/40 hover:bg-crimson-950/20 text-zinc-300 hover:text-white transition-all text-center group"
              >
                <Icon className="w-3.5 h-3.5 text-zinc-400 group-hover:text-crimson-400 mb-1 transition-colors" />
                <span className="text-[10px] font-semibold tracking-tight leading-tight">{preset.label}</span>
              </button>
            );
          })}
        </div>

        {/* 4 Custom Range Sliders */}
        <div className="space-y-2">
          <CustomSlider
            label="Candidate Price Adjustment"
            description="Simulate direct price point policy changes"
            value={sliders.priceDeltaPct}
            min={-30}
            max={40}
            step={1}
            unit="%"
            onChange={(val) => onChangeSliders({ ...sliders, priceDeltaPct: val })}
          />

          <CustomSlider
            label="Exogenous Macro Demand Shock"
            description="Simulate broad recessionary or expansionary shocks"
            value={sliders.demandShockPct}
            min={-50}
            max={30}
            step={1}
            unit="%"
            onChange={(val) => onChangeSliders({ ...sliders, demandShockPct: val })}
          />

          <CustomSlider
            label="Supply Chain Cost Surge"
            description="Simulate wholesale inflation on unit product cost"
            value={sliders.costSurgePct}
            min={0}
            max={50}
            step={1}
            unit="%"
            onChange={(val) => onChangeSliders({ ...sliders, costSurgePct: val })}
          />

          <CustomSlider
            label="Competitor Price War"
            description="Rival price cuts (Cross-elasticity loss = 2.0x)"
            value={sliders.competitorDropPct}
            min={0}
            max={30}
            step={1}
            unit="%"
            formatSign={false}
            onChange={(val) => onChangeSliders({ ...sliders, competitorDropPct: val })}
          />
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between text-[11px] font-mono text-zinc-400">
        <span>Instant 60fps Analytical Feedback</span>
        <span className="text-crimson-400/80">Active Reactive State</span>
      </div>
    </div>
  );
};
