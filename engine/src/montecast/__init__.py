"""Montecast — a Monte Carlo forecasting engine for the 2026 FIFA World Cup.

The engine fits team-strength models on ~150 years of international results,
draws tens of thousands of simulated tournaments, and exports calibrated
probabilities (champion odds, per-stage chances, match forecasts) as JSON
artifacts consumed by the web frontend.
"""

__version__ = "0.1.0"
