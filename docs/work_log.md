# NAOMI: Step-by-Step Project Work Log & Progress Tracker

**Project:** NAOMI — Neural Analytics for Optimization & Market Intelligence  
**Based on:** *Business Decision Companion (BDC) Blueprint (Leeroy & Leeroy 2025 Extension)*  
**Repository:** [https://github.com/princexpoddar/NAOMI.git](https://github.com/princexpoddar/NAOMI.git)  
**Maintained by:** AI Pair Programmer & Engineering Team  
**Last Updated:** 2026-09-04  

---

## 1. Project Progress Summary Table

| Phase / Milestone | Status | Owner | Primary Outputs / Files | Git Commit |
| :--- | :--- | :--- | :--- | :--- |
| **Phase 0: Blueprint & Architecture** | ✅ Completed | All | `docs/Business Decision Companion (BDC) – Project Blueprint.pdf`<br>`docs/implementation_plan.md` | `a858f32`<br>`927b864` |
| **Phase 1: Environment & Project Scaffolding** | ✅ Completed | Member 1 (You) | `requirements.txt`<br>`.gitignore`<br>`src/config.py`<br>`src/data/schemas.py` | `e5f0d64`<br>`52a00a6` |
| **Phase 2: Dataset Curation (Walmart M5 & Synthetic)** | ✅ Completed | Member 1 (You) | `scripts/build_m5_curated_data.py`<br>`data/raw/walmart_m5_curated.csv` (9,565 rows)<br>`data/synthetic/generate_synthetic_data.py` | `e5f0d64` |
| **Phase 3: Feature Engineering & Sequential Windowing** | ✅ Completed | Member 1 (You) | `src/data/pipeline.py`<br>`src/data/dataset.py`<br>`tests/test_data_pipeline.py` (5/5 tests pass) | `f957768` |
| **Phase 4: Demand Forecasting Engine (Baselines + LSTM)** | ✅ Completed | Member 1 (You) | `src/models/`<br>`tests/test_models.py` (5/5 tests pass)<br>`scripts/train_and_benchmark.py`<br>`models_cache/` | *Committing now* |
| **Phase 5: Economics, Pricing & Profit Optimization** | 🔄 Next | Member 2 | `src/core/elasticity.py`<br>`src/core/optimizer.py`<br>`src/core/financial.py` | *Upcoming* |
| **Phase 6: Counterfactual Simulation & REST API** | ⏳ Queued | Member 3 | `src/core/simulator.py`<br>`src/api/main.py` | *Upcoming* |
| **Phase 7: Executive Dashboard (Plotly Dash)** | ⏳ Queued | Member 4 | `src/dashboard/app.py`<br>`src/dashboard/layouts/`<br>`src/dashboard/components/`<br>`src/dashboard/callbacks/` | *Upcoming* |
| **Phase 8: Presentation & LLM Narrative** | ⏳ Queued | Member 5 | `presentation/`<br>`src/llm/` | *Upcoming* |

---

## 2. Detailed Step-by-Step Chronological Activity Log

### Milestone 1: Blueprint Study & Architecture Design
* **Date/Time**: 2026-09-04
* **Commit**: `a858f32`
* **Actions Completed**:
  1. Analyzed all 11 pages of `Business Decision Companion (BDC) – Project Blueprint.pdf`.
  2. Created the `docs/` directory and safely archived the blueprint PDF inside it.
  3. Formulated the low-level implementation plan with mathematical formulas for price elasticity ($E_d$), profit optimization ($\Pi(P) = (P - c) Q(P) - F$), Huber loss, and financial KPIs.
  4. Designed the 5-person peer team division with strict file ownership and zero merge-conflict protocols.

---

### Milestone 2: Dataset Strategy & Real-World Grounding Decision
* **Date/Time**: 2026-09-04
* **Commit**: `927b864`
* **Actions Completed**:
  1. Re-evaluated the role of synthetic data against the original paper (*Leeroy & Leeroy 2025, Journal of Risk and Financial Management*).
  2. Confirmed that the original paper utilized real-world Roblox Corporation financial data (58 quarters), and that using synthetic data as the primary source would weaken the academic story.
  3. Selected **Walmart M5 (Curated Subseries of 5 SKUs across 5.4 years / 1,913 daily observations each)** as the **Primary Production Dataset**:
     - `FOODS_3_090_CA_1` (Grocery / High volume, elastic $E_d \approx -1.35$)
     - `FOODS_1_001_CA_1` (Packaged Staples, moderate $E_d \approx -0.80$)
     - `HOUSEHOLD_1_001_CA_1` (Cleaning Essentials, inelastic $E_d \approx -0.42$)
     - `HOUSEHOLD_2_005_CA_1` (Home Goods, semi-durable $E_d \approx -0.95$)
     - `HOBBIES_1_001_CA_1` (Discretionary / Toys, holiday spikes $E_d \approx -1.15$)
  4. Established the documented benchmark unit cost assumption: $c = 60\% \times P_{\text{baseline}}$ (40% gross margin).
  5. Positioned the synthetic data generator as a secondary unit-testing validation harness.

---

### Milestone 3: Project Scaffolding & Data Generation
* **Date/Time**: 2026-09-04
* **Commits**: `e5f0d64`, `52a00a6`
* **Files Created**:
  - `requirements.txt`: Python package dependencies (torch, pandas, numpy, scipy, scikit-learn, xgboost, plotly, dash, pydantic, pytest).
  - `.gitignore`: Ignored Python bytecode, virtual environments, IDE files, and testing caches.
  - `src/config.py`: Global paths, 5 curated SKU profiles, lookback window $W=30$, train/val/test ratios (70/15/15), and LSTM hyperparameters.
  - `src/data/schemas.py`: Pydantic and dataclass models for `SKUProfile`, `SalesRecord`, `ForecastOutput`, `FinancialKPIs`, `OptimizationResult`, and `ScenarioResult`.
  - `scripts/build_m5_curated_data.py`: Data builder incorporating real Walmart calendar events (Super Bowl, Thanksgiving, Christmas closure, Easter) and California SNAP food stamp periods (1st-10th of month).
  - `data/raw/walmart_m5_curated.csv`: **9,565 rows** across 5 SKUs spanning 1,913 consecutive days (< 450 KB, bundled in Git).
  - `data/synthetic/generate_synthetic_data.py`: Controlled benchmark generator with known mathematical elasticity ($E_d = -1.20$) for unit testing.

---

### Milestone 4: Feature Pipeline & Sequential PyTorch Windowing
* **Date/Time**: 2026-09-04
* **Files Created**:
  - `src/data/pipeline.py`:
    - Strict backward-looking lags ($t-1, t-2, t-3, t-7, t-14, t-28$).
    - Rolling 7-day mean/std and 30-day mean using `shift(1)` to eliminate lookahead bias.
    - Cyclical calendar transforms: $\sin/\cos$ encodings for Day of Week and Month.
    - Event and SNAP disbursement indicator variables.
    - Chronological 70/15/15 split.
    - `MinMaxScaler` fitted exclusively on the Training set to prevent data leakage.
    - Target inversion utility (`inverse_transform_target`).
  - `src/data/dataset.py`:
    - `TimeSeriesWindowDataset(torch.utils.data.Dataset)`: Converts tabular matrices into $(B, W=30, F)$ sequential window tensors.
    - `build_dataloaders`: Generates PyTorch `DataLoader` objects for Train, Val, and Test.
  - `tests/test_data_pipeline.py`:
    - `test_primary_dataset_exists_and_valid`: Asserts 9,565 rows across 5 curated SKUs.
    - `test_feature_engineering_dimensions_and_cleanliness`: Asserts 20 features computed with zero NaNs.
    - `test_chronological_splits_integrity`: Asserts strict non-overlapping temporal splits.
    - `test_scaling_and_inverse_transformation`: Asserts scaling in $[0, 1]$ and inverse transform fidelity.
    - `test_pytorch_sliding_windows_and_dataloaders`: Asserts batch shape $(32, 30, 20)$ and target $(32, 1)$.
  - `scripts/verify_all_skus.py`: Comprehensive test script validating all 5 SKUs end-to-end.
* **Test Verification Status**: **All 5 automated tests passed (Exit Code 0).**
* **Commit**: `f957768`

---

### Milestone 5: Demand Forecasting Engine (Baselines + PyTorch LSTM + Ablation)
* **Date/Time**: 2026-09-04
* **Files Created**:
  - `src/models/base.py`: Abstract `BaseForecastModel` interface declaring `fit(X, y)` and `predict(X)`.
  - `src/models/baseline.py`: Statistical baselines (`NaiveBenchmarkModel`, `SeasonalNaiveBenchmarkModel`, `MovingAverageBenchmarkModel`, `RidgeBenchmarkModel`).
  - `src/models/lstm.py`: `DemandLSTM` 2-layer stacked network ($H=64$, dropout $0.2$, linear projection head), Smooth L1 Huber loss, Adam optimizer, early stopping, and Monte Carlo Dropout uncertainty quantification (`predict_with_confidence`).
  - `src/models/metrics.py`: MAE, RMSE, MAPE, $R^2$, and automated ablation dataframe generator.
  - `tests/test_models.py`: 5 automated tests covering baseline execution, LSTM forward pass, real training loop, uncertainty quantification, and metrics calculation.
  - `scripts/train_and_benchmark.py`: End-to-end multi-model benchmarking script across all 5 SKUs.
  - `docs/ablation_benchmark_results.csv`: Persisted quantitative benchmark table.
  - `models_cache/pytorch_lstm.pt`: Checkpointed trained neural network weights (< 250 KB).
* **Test Verification Status**: **All 5 model tests passed (Exit Code 0).**
* **Commit**: `07c48fa`

---

### Milestone 6: Developer Onboarding, README Overhaul & Git Collaboration Rules
* **Date/Time**: 2026-09-05
* **Files Modified**:
  - `README.md`:
    - Executive summary and architectural diagram.
    - Current technical status matrix across all 8 phases.
    - 30-second quickstart guide (`pip install -r requirements.txt`, verify scripts, run tests).
    - **Mandatory Git Collaboration & Strict Branching Protocol**: Protected `main` branch policy, dedicated feature branch allocation matrix, and exact terminal commands to prevent accidental overwrites.
    - Role-by-role developer jumpstart guide with exact Git branch names, file scopes, ready-to-use input code snippets, and expected output signatures for Members 2, 3, 4, and 5.
    - Full repository layout and documentation hyperlinks.
  - `docs/implementation_plan.md`:
    - Reinforced Section 7.3 with strict feature branch isolation (`feat/*`) and PR review requirement before merging.

---

## 3. Immediate Next Steps & Action Plan

1. **Member 2**: Checkout branch `feat/pricing-finance` and implement `src/core/elasticity.py`, `optimizer.py`, `financial.py`.
2. **Member 3**: Checkout branch `feat/simulation-api` and implement `src/core/simulator.py`, `src/api/main.py`.
3. **Member 4**: Checkout branch `feat/dashboard-ui` and build `src/dashboard/` Plotly Dash application.
4. **Member 5**: Checkout branch `feat/presentation-llm` and build `presentation/SLIDE_DECK_CONTENT.md`, `DEMO_SCRIPT.md`, and `src/llm/`.

