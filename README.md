# DerivaLens

## A Regime-Aware Research Framework for Futures & Options

**Status:** Phase 1 - Project Setup and Foundation  
**Version:** 0.1.0  
**Disclaimer:** This is an educational quantitative research tool. It does NOT provide investment advice or trading recommendations.

---

## Why I Built This

DerivaLens is a quantitative research platform designed to answer:

> "Given the current market environment, which trading strategy has historically performed best under similar conditions, and what are the associated risks?"

The core insight is that **the same strategy performs differently in different market regimes**. A momentum strategy that works in trending markets fails in range-bound markets. A volatility-selling strategy that profits when IV > realized volatility loses money when volatility spikes unexpectedly.

This project combines:
- **Derivatives analytics** (futures basis, options Greeks, implied volatility)
- **Volatility research** (realized vs implied, volatility surfaces, skew)
- **Market regime detection** (ML-based classification)
- **Systematic backtesting** (with look-ahead bias prevention)
- **Risk analysis** (drawdown, Sharpe/Sortino, regime attribution)

**Goal:** Demonstrate that I can formulate quantitative hypotheses, test them rigorously against historical data, and clearly explain when and why strategies succeed or fail.

---

## Project Scope

### Phase 1: Foundation ✅ (Current)
- Project structure and configuration
- Environment setup
- Data pipeline skeleton
- Core module architecture
- Unit test framework

### Phases 2-14: Full Implementation
See `DEVELOPMENT.md` for detailed phase breakdown.

---

## Quick Start

### Prerequisites
- Python 3.11+
- Git
- Virtual environment tool (venv or conda)

### Installation

```bash
# 1. Clone or navigate to the project
cd DerivaLens

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Copy environment template
cp .env.example .env

# 6. Verify installation
python -c "from src.config import get_config; config = get_config(); print('✓ DerivaLens initialized')"
```

### Project Structure

```
DerivaLens/
├── README.md                          # Project overview (this file)
├── DEVELOPMENT.md                     # Phase-by-phase development guide
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── .gitignore                         # Git ignore rules
│
├── config/
│   ├── config.yaml                   # Main configuration (settings, params)
│   └── instruments.yaml              # Instrument specifications (NIFTY, etc.)
│
├── data/
│   ├── raw/                          # Raw market data (not in git)
│   ├── processed/                    # Cleaned/validated data
│   ├── features/                     # Engineered features
│   └── synthetic/                    # Test data (clearly labeled)
│
├── src/
│   ├── __init__.py                   # Package initialization
│   ├── config.py                     # Configuration loader
│   │
│   ├── data/                         # Data pipeline
│   │   ├── __init__.py
│   │   ├── ingestion.py              # Load data from sources
│   │   ├── cleaning.py               # Data cleaning
│   │   ├── validation.py             # Data validation
│   │   └── storage.py                # Save/load data
│   │
│   ├── futures/                      # Futures analytics
│   │   ├── __init__.py
│   │   ├── basis.py                  # Basis calculation
│   │   ├── term_structure.py         # Term structure analysis
│   │   └── futures_features.py       # Feature engineering
│   │
│   ├── options/                      # Options analytics
│   │   ├── __init__.py
│   │   ├── black_scholes.py          # BS pricing model
│   │   ├── implied_volatility.py     # IV solver
│   │   ├── greeks.py                 # Delta, Gamma, Vega, Theta
│   │   ├── skew.py                   # Volatility skew
│   │   ├── chain.py                  # Options chain handling
│   │   ├── term_structure.py         # Expiry term structure
│   │   └── open_interest.py          # OI analysis
│   │
│   ├── volatility/                   # Volatility research
│   │   ├── __init__.py
│   │   ├── realized_volatility.py    # Historical volatility
│   │   ├── implied_vs_realized.py    # IV-RV analysis
│   │   └── volatility_regimes.py     # Vol-based regimes
│   │
│   ├── sentiment/                    # Event/news analysis
│   │   ├── __init__.py
│   │   ├── events.py                 # Event management
│   │   └── sentiment.py              # Sentiment scoring
│   │
│   ├── regimes/                      # Market regime detection
│   │   ├── __init__.py
│   │   ├── features.py               # Regime features
│   │   ├── classifier.py             # ML classifier
│   │   └── regime_analysis.py        # Regime analysis
│   │
│   ├── strategies/                   # Trading strategies
│   │   ├── __init__.py
│   │   ├── base.py                   # Base strategy class
│   │   ├── futures_momentum.py       # Futures momentum
│   │   ├── iv_rv.py                  # IV-RV volatility arb
│   │   ├── options_skew.py           # Skew-based strategy
│   │   ├── basis_convergence.py      # Basis mean-reversion
│   │   └── event_volatility.py       # Event vol strategy
│   │
│   ├── backtesting/                  # Backtesting engine
│   │   ├── __init__.py
│   │   ├── engine.py                 # Main backtester
│   │   ├── execution.py              # Order execution
│   │   ├── costs.py                  # Transaction costs
│   │   ├── portfolio.py              # Portfolio tracking
│   │   └── walk_forward.py           # Walk-forward testing
│   │
│   ├── risk/                         # Risk management
│   │   ├── __init__.py
│   │   ├── metrics.py                # Sharpe, Sortino, etc.
│   │   ├── drawdown.py               # Drawdown analysis
│   │   ├── position_sizing.py        # Position sizing rules
│   │   └── stress_testing.py         # Stress tests
│   │
│   └── reporting/                    # Analysis & reporting
│       ├── __init__.py
│       ├── performance_report.py     # Performance summary
│       └── research_report.py        # Full research report
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_futures_analysis.ipynb
│   ├── 03_options_analysis.ipynb
│   ├── 04_volatility_analysis.ipynb
│   ├── 05_regime_analysis.ipynb
│   ├── 06_strategy_research.ipynb
│   └── 07_walk_forward_results.ipynb
│
├── dashboard/
│   └── app.py                        # Streamlit dashboard
│
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_data.py
│   ├── test_options.py
│   ├── test_futures.py
│   ├── test_backtester.py
│   └── test_risk.py
│
└── reports/
    ├── DerivaLens_Research_Report.md
    └── figures/
```

---

## Core Concepts

### Market Regimes
Market behavior falls into distinct regimes with different characteristics:

| Regime | Volatility | Trend | Strategies | Example |
|--------|-----------|-------|-----------|---------|
| Trending + Low Vol | Low | Strong | Momentum | Post-recovery |
| Trending + High Vol | High | Strong | Vol selling | Crisis recovery |
| Range-bound + Low Vol | Low | Weak | Mean reversion | Boring periods |
| Range-bound + High Vol | High | Weak | Vol selling + hedges | Uncertainty |
| Event-driven | Extreme | N/A | Event-specific | Earnings, policy |

**Key insight:** The same strategy (e.g., sell volatility) may be profitable in some regimes and disastrous in others.

### Implied vs Realized Volatility
- **Implied Volatility (IV):** What the options market thinks volatility will be
- **Realized Volatility (RV):** Actual volatility that occurs
- **IV-RV Spread:** The "Volatility Risk Premium"
  - If IV > RV: Options were overpriced → selling vol was profitable
  - If IV < RV: Options were underpriced → buying vol was profitable

### Futures Basis
- **Basis = Futures Price - Spot Price**
- Basis converges to zero at expiry
- Abnormal basis may signal mispricings

### Greeks (Options Risk Measures)
- **Delta (Δ):** How much option price changes when spot moves $1
- **Gamma (Γ):** How much delta changes when spot moves $1 (acceleration)
- **Vega (ν):** How much option price changes when IV rises 1%
- **Theta (Θ):** Daily option decay from time passage

---

## Architecture Philosophy

### 1. **Instrument Abstraction**
The system is designed to work with different instruments (NIFTY, BANKNIFTY, SPX, etc.) without hardcoding. Configuration files define instrument specs.

### 2. **Modular Pipeline**
```
Raw Data → Cleaning → Validation → Features → Analytics → Strategies → Backtesting → Reporting
```

### 3. **Look-Ahead Bias Prevention**
At each time step, strategies only use information available **at or before** that time.
- Walk-forward validation (no random train/test split)
- Temporal separation of train/validate/test
- No future information in signals
- Proper feature fitting (on training data only)

### 4. **Configuration-Driven**
Parameters are in YAML config files, not hardcoded. Easy to test sensitivity.

### 5. **Testing First**
Unit tests for critical components (IV solver, Greeks, Sharpe calculation, etc.).

---

## Data

### Current Status: SYNTHETIC TEST DATA ONLY

**IMPORTANT:** Phase 1 uses synthetic data for testing the pipeline only.

Future phases will add:
1. Real NIFTY futures/options data (from NSE/licensed sources)
2. Data validation system
3. Missing data handling

All synthetic data is clearly labeled in the `data/synthetic/` folder.

### Data Requirements
Once real data is added, each dataset contains:
- **Timestamp/Date**
- **Instrument** (NIFTY, BANKNIFTY, etc.)
- **Expiry date** (for futures/options)
- **Strike price** (for options)
- **Option type** (call/put, for options)
- **OHLCV** (open, high, low, close, volume)
- **Open Interest** (OI)
- **Implied Volatility** (IV, for options)

---

## Configuration

### Main Config: `config/config.yaml`
Defines:
- Project settings
- Data paths
- Instrument specs
- Backtesting parameters (costs, leverage, position sizing)
- Strategy parameters
- Volatility calculation methods
- Regime classification settings
- ML classifier parameters
- Logging configuration

### Instruments: `config/instruments.yaml`
Defines:
- Exchange specs for each instrument
- Futures contract specs (multiplier, tick size)
- Options contract specs (strike spacing, expiry schedule)

### Environment: `.env`
For sensitive data (API keys, database URLs, etc.). Use `.env.example` as template.

---

## Avoiding Look-Ahead Bias

This is critical for any backtest. Here's how DerivaLens prevents it:

### Rule 1: Temporal Separation
- At time t, decisions use only data available at or before time t
- Future realized volatility is NOT used to decide today's trade
- Future option prices are NOT used for today's Greeks

### Rule 2: Walk-Forward Validation
```
Train: 2019-2022 → Validate: 2023 → Test: 2024
(never mix these periods)
```

### Rule 3: Proper Scaler Fitting
- Scalers (normalization, standardization) fit ONLY on training data
- Applied to validation and test sets using training parameters

### Rule 4: Signal Specification
- Signals defined BEFORE seeing backtest results
- Parameters locked before evaluation
- No parameter tweaking based on results

---

## Research Methodology

DerivaLens follows this process:

```
1. HYPOTHESIS FORMULATION
   ↓
2. DATA COLLECTION & CLEANING
   ↓
3. FEATURE ENGINEERING
   ↓
4. REGIME CLASSIFICATION
   ↓
5. STRATEGY DESIGN (parameters pre-specified)
   ↓
6. TRAINING BACKTEST (2019-2022)
   ↓
7. VALIDATION (2023)
   ↓
8. FINAL TEST (2024) ← Only report this
   ↓
9. STATISTICAL ANALYSIS (correlation, significance, etc.)
   ↓
10. ROBUSTNESS TESTING (cost, parameter, market sensitivity)
    ↓
11. FAILURE ANALYSIS (why did it lose money?)
    ↓
12. CONCLUSION & REPORT
```

**Never:** backtest 100 strategies and pick the best one.

---

## Testing

### Run Tests
```bash
pytest tests/ -v
```

### Test Coverage
```bash
pytest tests/ --cov=src --cov-report=html
```

---

## Logging

Logging is configured in `config/config.yaml`. By default:
- **Level:** INFO
- **Output:** Console + `logs/` directory

Change log level with environment variable:
```bash
LOG_LEVEL=DEBUG python -m src.data.ingestion
```

---

## Phase Checklist

- [ ] **Phase 1:** Architecture, config, skeleton (CURRENT)
- [ ] **Phase 2:** Data ingestion and validation
- [ ] **Phase 3:** Futures analytics (basis, OI)
- [ ] **Phase 4:** Options analytics (Greeks, IV, skew)
- [ ] **Phase 5:** Volatility analytics (RV, IV-RV)
- [ ] **Phase 6:** Regime classification
- [ ] **Phase 7:** Strategy framework
- [ ] **Phase 8:** Backtesting engine
- [ ] **Phase 9:** Risk engine
- [ ] **Phase 10:** Walk-forward validation
- [ ] **Phase 11:** Statistical analysis
- [ ] **Phase 12:** Streamlit dashboard
- [ ] **Phase 13:** Research report
- [ ] **Phase 14:** Testing and GitHub polish

---

## Key Interview Questions This Project Answers

### Derivatives Knowledge
- "What is implied volatility and why isn't it the same as realized volatility?"
- "Explain the volatility smile and why it exists in equity options."
- "What is futures basis and why does it converge to zero?"
- "Explain Delta, Gamma, Theta, and Vega in simple terms."

### Quantitative Research
- "How did you prevent look-ahead bias in your backtest?"
- "Why did you use walk-forward validation instead of random train/test split?"
- "How did transaction costs affect your strategy performance?"
- "What does it mean for a strategy to be 'robust'?"

### Machine Learning
- "How did you decide to use regime classification instead of price prediction?"
- "What features were most important for regime detection?"
- "How would your model handle a regime it has never seen before?"

### Trading & Risk
- "What is your maximum acceptable drawdown and why?"
- "Why is a high win rate not necessarily a good strategy?"
- "How would your strategy perform during a volatility shock?"

---

## Limitations & Disclaimers

1. **Educational Tool Only**
   - Not for live trading or real money decisions
   - Does not provide investment advice

2. **Synthetic Data**
   - Initial versions use synthetic data for testing
   - Real data from NSE/licensed sources required for actual research

3. **Model Limitations**
   - Historical performance ≠ future performance
   - Black-Scholes assumes European options and perfect markets
   - Market regimes can change unexpectedly
   - Tail risks may exceed VaR estimates

4. **Execution Assumptions**
   - Backtests assume prices fill at OHLC levels
   - Real market impact and slippage may differ
   - Margin and leverage carry real risks

---

## Future Enhancements (Post-Phase 14)

- [ ] Real-time data feeds
- [ ] Heston volatility model
- [ ] GARCH volatility forecasting
- [ ] XGBoost regime classifier
- [ ] Monte Carlo simulation
- [ ] Options portfolio Greeks aggregation
- [ ] International instruments (SPX, other indices)
- [ ] Alternative volatility estimators (Garman-Klass, Parkinson)
- [ ] News sentiment analysis (NLP)
- [ ] PostgreSQL backend for larger datasets

---

## How to Contribute

This is a personal research project, but the code is structured for extensibility.

To add new strategies:
1. Create `src/strategies/your_strategy.py`
2. Inherit from `BaseStrategy`
3. Implement `generate_signal()` and `position_sizing()`
4. Add tests
5. Document the hypothesis

---

## Contact & Attribution

**Project:** DerivaLens (v0.1.0)  
**Author:** Quantitative Research Team  
**Purpose:** Educational quantitative research platform  
**Target:** Futures First Internship Application  

---

## License

This project is provided as-is for educational and research purposes.

---

## Next Steps

For Phase 2 setup, see `DEVELOPMENT.md`.

To verify Phase 1 is working:
```bash
python -c "from src.config import get_config; c = get_config(); print(f'✓ Config loaded: {c.get(\"project.name\")}')"
```

Expected output:
```
✓ Config loaded: DerivaLens
```

---

**Last Updated:** 2026-08-18  
**Status:** Phase 1 Complete ✅
