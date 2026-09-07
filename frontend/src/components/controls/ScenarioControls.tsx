import React from "react";
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
      isActive: sliders.priceDeltaPct === 0 && sliders.demandShockPct === 0 && sliders.costSurgePct === 0 && sliders.competitorDropPct === 0,
      apply: () => onChangeSliders({ priceDeltaPct: 0, demandShockPct: 0, costSurgePct: 0, competitorDropPct: 0 }),
    },
    {
      id: "price_up",
      label: "Price +5%",
      isActive: sliders.priceDeltaPct === 5 && sliders.demandShockPct === 0 && sliders.costSurgePct === 0 && sliders.competitorDropPct === 0,
      apply: () => onChangeSliders({ priceDeltaPct: 5, demandShockPct: 0, costSurgePct: 0, competitorDropPct: 0 }),
    },
    {
      id: "macro_shock",
      label: "Macro -15%",
      isActive: sliders.priceDeltaPct === 0 && sliders.demandShockPct === -15 && sliders.costSurgePct === 0 && sliders.competitorDropPct === 0,
      apply: () => onChangeSliders({ priceDeltaPct: 0, demandShockPct: -15, costSurgePct: 0, competitorDropPct: 0 }),
    },
    {
      id: "cost_surge",
      label: "Cost +10%",
      isActive: sliders.priceDeltaPct === 0 && sliders.demandShockPct === 0 && sliders.costSurgePct === 10 && sliders.competitorDropPct === 0,
      apply: () => onChangeSliders({ priceDeltaPct: 0, demandShockPct: 0, costSurgePct: 10, competitorDropPct: 0 }),
    },
    {
      id: "price_war",
      label: "Price War",
      isActive: sliders.priceDeltaPct === 0 && sliders.demandShockPct === 0 && sliders.costSurgePct === 0 && sliders.competitorDropPct === 10,
      apply: () => onChangeSliders({ priceDeltaPct: 0, demandShockPct: 0, costSurgePct: 0, competitorDropPct: 10 }),
    },
    {
      id: "stagflation",
      label: "Stagflation",
      isActive: sliders.priceDeltaPct === 0 && sliders.demandShockPct === -8 && sliders.costSurgePct === 10 && sliders.competitorDropPct === 0,
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
    <div className="w-full h-full flex flex-col justify-between">
      <div>
        <div className="flex items-center justify-between mb-2.5">
          <div>
            <h3 className="text-sm font-semibold tracking-tight text-white">
              Counterfactual Simulation
            </h3>
            <p className="text-[11px] text-slate-400">Exogenous shock & pricing levers</p>
          </div>
          <button
            onClick={handleReset}
            className="text-[11px] text-slate-400 hover:text-white px-2.5 py-0.5 rounded bg-slate-800/80 border border-slate-700/60 hover:border-slate-500 transition-colors font-mono"
          >
            Reset
          </button>
        </div>

        {/* Presets Grid */}
        <div className="grid grid-cols-3 sm:grid-cols-6 gap-1.5 mb-3">
          {presets.map((preset) => (
            <button
              key={preset.id}
              onClick={preset.apply}
              className={`py-1 px-1.5 text-center rounded-lg text-xs font-medium transition-all ${
                preset.isActive
                  ? "bg-blue-950 border border-blue-600/80 text-white shadow-sm font-semibold"
                  : "bg-[#111827] border border-slate-800 text-slate-400 hover:text-slate-200 hover:border-slate-700"
              }`}
            >
              {preset.label}
            </button>
          ))}
        </div>

        {/* 4 Compact Range Sliders */}
        <div className="space-y-1">
          <CustomSlider
            label="Candidate Price Adjustment"
            value={sliders.priceDeltaPct}
            min={-30}
            max={40}
            step={1}
            unit="%"
            onChange={(val) => onChangeSliders({ ...sliders, priceDeltaPct: val })}
          />

          <CustomSlider
            label="Macro Demand Shock"
            value={sliders.demandShockPct}
            min={-50}
            max={30}
            step={1}
            unit="%"
            onChange={(val) => onChangeSliders({ ...sliders, demandShockPct: val })}
          />

          <CustomSlider
            label="Unit Cost Surge"
            value={sliders.costSurgePct}
            min={0}
            max={50}
            step={1}
            unit="%"
            onChange={(val) => onChangeSliders({ ...sliders, costSurgePct: val })}
          />

          <CustomSlider
            label="Competitor Price Cut"
            value={sliders.competitorDropPct}
            min={0}
            max={30}
            step={1}
            unit="%"
            onChange={(val) => onChangeSliders({ ...sliders, competitorDropPct: val })}
          />
        </div>
      </div>
    </div>
  );
};
