# Montecast — engine

The Python forecasting engine behind [Montecast](../README.md). It ingests ~150 years of
international results, fits a Dixon‑Coles × Elo ensemble, runs a Monte Carlo simulation of
the 2026 World Cup, and exports JSON artifacts for the web app.

## Install

```bash
cd engine
pip install -e .            # runtime deps
pip install -e ".[dev]"     # + pytest, ruff
```

## Data

Place the [martj42 international‑results dataset](https://www.kaggle.com/datasets/martj42/international-football-results-from-1872-to-2017)
in `engine/data/raw/`:

- `results.csv` — every international match, 1872 → present
- `shootouts.csv` — penalty‑shootout outcomes
- `former_names.csv` — historical → current team‑name mapping

## Run

```bash
python -m montecast.pipeline --n-sims 50000
```

| Flag | Default | Meaning |
|------|---------|---------|
| `--as-of` | today | Generate the forecast as of this date (also enables backtests) |
| `--n-sims` | 50000 | Number of simulated tournaments |
| `--seed` | 20260611 | RNG seed for reproducibility |
| `--out` | `web/public/data` | Output directory for the JSON artifacts |

## Layout

```
src/montecast/
├── ingest/load.py        # load & clean historical matches
├── models/
│   ├── elo.py            # international Elo ratings
│   ├── dixon_coles.py    # time-weighted bivariate-Poisson model
│   └── ensemble.py       # Dixon-Coles × Elo (+ optional GB layer)
├── simulate/
│   ├── monte_carlo.py    # vectorised tournament simulator
│   ├── tiebreakers.py    # FIFA group-ranking rules
│   └── bracket.py        # knockout bracket logic
├── export/to_json.py     # JSON artifacts
├── tournament.py         # 2026 draw / config loader
└── pipeline.py           # end-to-end CLI entry point
```
