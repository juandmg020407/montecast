"""Project-wide paths, constants and reproducibility settings."""
from __future__ import annotations

import datetime as _dt
from pathlib import Path

# --- Paths -----------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[3]
ENGINE_DIR = ROOT / "engine"
DATA_DIR = ENGINE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
CONFIG_DIR = Path(__file__).resolve().parent / "config"
WEB_DATA_DIR = ROOT / "web" / "public" / "data"

RESULTS_CSV = RAW_DIR / "results.csv"
SHOOTOUTS_CSV = RAW_DIR / "shootouts.csv"
FORMER_NAMES_CSV = RAW_DIR / "former_names.csv"
WC2026_CONFIG = CONFIG_DIR / "wc2026.json"

# --- Time ------------------------------------------------------------------
# Predictions are generated "as of" this date. The pipeline can override it
# (e.g. to reproduce a pre-tournament forecast or run a historical backtest).
DEFAULT_AS_OF: _dt.date = _dt.date.today()

# --- Reproducibility -------------------------------------------------------
RANDOM_SEED = 20260611  # opening day, for luck

# Ensure the processed-data directory exists (cheap, side-effect-free import).
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
