import React, { useState, useEffect, useMemo } from "react";
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
  checkApiHealth,
  getHistoricalDemand,
  getForecastSeries,
  computeProfitLandscape,
  computeSimulation,
} from "./services/api";
import { SKUInfo, SimulationSliders } from "./types";
import { ExternalLink, GitBranch, Cpu, Database } from "lucide-react";

export const App: React.FC = () => {
  const [selectedSku, setSelectedSku] = useState<SKUInfo>(CURATED_SKUS[0]);
  const [horizon, setHorizon] = useState<number>(7);
  const [sliders, setSliders] = useState<SimulationSliders>({
    priceDeltaPct: 0,
    demandShockPct: 0,
    costSurgePct: 0,
    competitorDropPct: 0,
  });
  const [isApiOnline, setIsApiOnline] = useState<boolean>(false);

  // Check backend status on mount
  useEffect(() => {
    checkApiHealth().then(setIsApiOnline);
    const interval = setInterval(() => {
      checkApiHealth().then(setIsApiOnline);
    }, 10000);
    return () => clearInterval(interval);
  }, []);

  // Compute reactive calculations at 60fps
  const historical = useMemo(() => getHistoricalDemand(selectedSku.item_id), [selectedSku.item_id]);
  const forecast = useMemo(() => getForecastSeries(selectedSku.item_id, horizon), [selectedSku.item_id, horizon]);
  const optData = useMemo(() => computeProfitLandscape(selectedSku), [selectedSku]);
  const simulation = useMemo(() => computeSimulation(selectedSku, sliders), [selectedSku, sliders]);

  return (
    <div className="relative min-h-screen bg-pitch-black text-zinc-100 flex flex-col selection:bg-crimson-600 selection:text-white">
      {/* 1. Interactive Pitch Black Dot Grid & Ambient Crimson Atmosphere */}
      <BackgroundGrid />

      {/* 2. Top Navigation & Command Bar */}
      <Header
        selectedSku={selectedSku}
        onSelectSku={setSelectedSku}
        horizon={horizon}
        onSelectHorizon={setHorizon}
        isApiOnline={isApiOnline}
      />

      {/* 3. Main C-Suite Dashboard Content Container */}
      <main className="relative z-10 max-w-[1600px] w-full mx-auto px-4 lg:px-8 py-6 space-y-6 flex-1">
        
        {/* Top Section: 5 Hero KPI Metric Cards */}
        <section>
          <KpiHeroGrid
            optData={optData}
            sku={selectedSku}
            horizon={horizon}
          />
        </section>

        {/* Middle Section: Two Core Analytical Visualizations */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-5">
          {/* Left Chart: Demand Trajectory + LSTM + 90% CI */}
          <SpotlightCard className="p-5 h-[360px]">
            <DemandTrajectoryChart
              historical={historical}
              forecast={forecast}
              sku={selectedSku}
            />
          </SpotlightCard>

          {/* Right Chart: Profit & Revenue Parabolic Landscape */}
          <SpotlightCard className="p-5 h-[360px]">
            <ProfitLandscapeChart
              optData={optData}
              sku={selectedSku}
            />
          </SpotlightCard>
        </section>

        {/* Bottom Section: 3-Column Decision Workspace */}
        <section className="grid grid-cols-1 lg:grid-cols-12 gap-5">
          
          {/* 1. Counterfactual Sliders (4 cols) */}
          <div className="lg:col-span-4">
            <SpotlightCard className="h-[390px] p-4">
              <ScenarioControls
                sliders={sliders}
                onChangeSliders={setSliders}
              />
            </SpotlightCard>
          </div>

          {/* 2. Scenario Comparison Bars (4 cols) */}
          <div className="lg:col-span-4">
            <SpotlightCard className="h-[390px] p-5">
              <ScenarioComparisonChart simulation={simulation} />
            </SpotlightCard>
          </div>

          {/* 3. AI Strategic Decision Companion (4 cols) */}
          <div className="lg:col-span-4">
            <div className="h-[390px]">
              <StrategicCompanion
                simulation={simulation}
                sku={selectedSku}
              />
            </div>
          </div>

        </section>

      </main>

      {/* 4. Luxury Executive Footer */}
      <footer className="relative z-10 border-t border-white/5 bg-pitch-black/90 py-4 px-4 lg:px-8 text-xs font-mono text-zinc-400">
        <div className="max-w-[1600px] mx-auto flex flex-col sm:flex-row items-center justify-between gap-3">
          <div className="flex items-center gap-4">
            <span className="flex items-center gap-1.5 text-zinc-300">
              <Cpu className="w-3.5 h-3.5 text-crimson-400" />
              PyTorch LSTM + Huber Loss (W=30)
            </span>
            <span className="hidden sm:inline text-zinc-600">•</span>
            <span className="flex items-center gap-1.5">
              <Database className="w-3.5 h-3.5 text-emerald-400" />
              Empirical Walmart M5 (5.4 Yrs / 1,913 Days)
            </span>
          </div>

          <div className="flex items-center gap-4 text-[11px]">
            <span className="text-zinc-400">
              Grounded in <strong className="text-zinc-300">Leeroy & Leeroy (2025)</strong>
            </span>
            <a
              href="https://github.com/princexpoddar/NAOMI"
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-1 text-crimson-400 hover:text-crimson-300 transition-colors"
            >
              <GitBranch className="w-3.5 h-3.5" />
              <span>princexpoddar/NAOMI</span>
              <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
