import React, { useState, useMemo } from "react";
import { BackgroundGrid } from "./components/ui/BackgroundGrid";
import { Header } from "./components/Header";
import { KpiHeroGrid } from "./components/KpiHeroGrid";
import { DemandTrajectoryChart } from "./components/charts/DemandTrajectoryChart";
import { ProfitLandscapeChart } from "./components/charts/ProfitLandscapeChart";
import { ScenarioComparisonChart } from "./components/charts/ScenarioComparisonChart";
import { ScenarioControls } from "./components/controls/ScenarioControls";
import { StrategicCompanion } from "./components/narrative/StrategicCompanion";
import { SpotlightCard } from "./components/ui/Spotlight";
import {
  CURATED_SKUS,
  getHistoricalDemand,
  getForecastSeries,
  computeProfitLandscape,
  computeSimulation,
} from "./services/api";
import { SKUInfo, SimulationSliders } from "./types";

export const App: React.FC = () => {
  const [selectedSku, setSelectedSku] = useState<SKUInfo>(CURATED_SKUS[0]);
  const [horizon, setHorizon] = useState<number>(7);
  const [sliders, setSliders] = useState<SimulationSliders>({
    priceDeltaPct: 0,
    demandShockPct: 0,
    costSurgePct: 0,
    competitorDropPct: 0,
  });

  // Real-time analytical computation
  const historical = useMemo(() => getHistoricalDemand(selectedSku.item_id), [selectedSku.item_id]);
  const forecast = useMemo(() => getForecastSeries(selectedSku.item_id, horizon), [selectedSku.item_id, horizon]);
  const optData = useMemo(() => computeProfitLandscape(selectedSku), [selectedSku]);
  const simulation = useMemo(() => computeSimulation(selectedSku, sliders), [selectedSku, sliders]);

  return (
    <div className="relative min-h-screen bg-[#0B0F19] text-slate-100 flex flex-col font-sans">
      {/* Subtle Slate Background */}
      <BackgroundGrid />

      {/* Sticky Executive Header */}
      <Header
        selectedSku={selectedSku}
        onSelectSku={setSelectedSku}
        horizon={horizon}
        onSelectHorizon={setHorizon}
      />

      {/* Main Content */}
      <main className="relative z-10 max-w-[1500px] w-full mx-auto px-6 py-5 space-y-5 flex-1">
        
        {/* Row 1: 5 Executive KPI Bento Cards */}
        <section>
          <KpiHeroGrid
            optData={optData}
            sku={selectedSku}
            horizon={horizon}
          />
        </section>

        {/* Row 2: Two Core Analytical Visualizations */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          <SpotlightCard className="p-4 h-[340px]">
            <DemandTrajectoryChart
              historical={historical}
              forecast={forecast}
              sku={selectedSku}
            />
          </SpotlightCard>

          <SpotlightCard className="p-4 h-[340px]">
            <ProfitLandscapeChart
              optData={optData}
              sku={selectedSku}
            />
          </SpotlightCard>
        </section>

        {/* Row 3: Decision Workspace (3 Columns) */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-4">
          {/* Sliders (4 cols) */}
          <div className="lg:col-span-4">
            <SpotlightCard className="h-[350px] p-4">
              <ScenarioControls
                sliders={sliders}
                onChangeSliders={setSliders}
              />
            </SpotlightCard>
          </div>

          {/* Impact Bars (4 cols) */}
          <div className="lg:col-span-4">
            <SpotlightCard className="h-[350px] p-4">
              <ScenarioComparisonChart simulation={simulation} />
            </SpotlightCard>
          </div>

          {/* Strategic Brief (4 cols) */}
          <div className="lg:col-span-4">
            <div className="h-[350px]">
              <StrategicCompanion
                simulation={simulation}
                sku={selectedSku}
              />
            </div>
          </div>
        </section>

      </main>

      {/* Minimal Enterprise Footer */}
      <footer className="relative z-10 border-t border-slate-800/80 bg-[#0B0F19] py-3 px-6 text-xs text-slate-500">
        <div className="max-w-[1500px] mx-auto flex items-center justify-between">
          <span>NAOMI Decision Companion • Neural Optimization Engine</span>
          <a
            href="https://github.com/princexpoddar/NAOMI"
            target="_blank"
            rel="noreferrer"
            className="text-slate-400 hover:text-slate-200 transition-colors"
          >
            GitHub Repository
          </a>
        </div>
      </footer>
    </div>
  );
};

export default App;
