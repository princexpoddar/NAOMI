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
      label: "Baseline",
      apply: () => onChangeSliders({ priceDeltaPct: 0, demandShockPct: 0, costSurgePct: 0, competitorDropPct: 0 }),
    },
    {
      label: "Price +5%",
      apply: () => onChangeSliders({ priceDeltaPct: 5, demandShockPct: 0, costSurgePct: 0, competitorDropPct: 0 }),
    },
    {
      label: "Macro -15%",
      apply: () => onChangeSliders({ priceDeltaPct: 0, demandShockPct: -15, costSurgePct: 0, competitorDropPct: 0 }),
    },
    {
      label: "Cost +10%",
      apply: () => onChangeSliders({ priceDeltaPct: 0, demandShockPct: 0, costSurgePct: 10, competitorDropPct: 0 }),
    },
    {
      label: "Price War",
      apply: () => onChangeSliders({ priceDeltaPct: 0, demandShockPct: 0, costSurgePct: 0, competitorDropPct: 10 }),
    },
    {
      label: "Stagflation",
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
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold tracking-tight text-white">
            Counterfactual Simulation
          </h3>
          <button
            onClick={handleReset}
            className="text-[11px] text-zinc-400 hover:text-white px-2 py-0.5 rounded bg-zinc-800/80 border border-zinc-700/60 transition-colors"
          >
            Reset
          </button>
        </div>

        {/* Clean Presets Pill Row */}
        <div className="grid grid-cols-3 sm:grid-cols-6 gap-1.5 mb-3">
          {presets.map((preset, idx) => (
            <button
              key={idx}
              onClick={preset.apply}
              className="py-1 px-1.5 text-center rounded-lg bg-[#141418] border border-zinc-800 hover:border-rose-700/60 hover:text-white text-zinc-400 text-xs font-medium transition-colors"
            >
              {preset.label}
            </button>
          ))}
        </div>

        {/* 4 Range Sliders */}
        <div className="space-y-1.5">
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
            formatSign={false}
            onChange={(val) => onChangeSliders({ ...sliders, competitorDropPct: val })}
          />
        </div>
      </div>
    </div>
  );
};
