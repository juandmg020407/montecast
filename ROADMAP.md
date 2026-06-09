# Roadmap

Montecast is intentionally small and honest: a working forecasting engine plus a clear way
to read it. This is what's done and what's next.

## ✅ Done

- **Engine** — historical ingestion (150 yrs) · international Elo · time‑weighted
  Dixon‑Coles bivariate‑Poisson · ensemble blend · vectorised Monte Carlo simulator with
  FIFA tiebreakers, best‑thirds selection and the official Round‑of‑32 bracket.
- **Artifacts** — five JSON files (`meta`, `teams`, `simulation`, `groups`, `bracket`).
- **Web** — bilingual (EN/ES) Next.js 16 site: data‑driven hero, favourites leaderboard,
  group standings + match forecasts, projected knockout bracket, methodology.
- **Ship** — static build, ready for Vercel.

## 🔜 Next

- **Calibration / backtest page** — run the engine `--as-of` past tournaments and report
  Brier score & reliability curves, so the "honest probabilities" claim is measurable.
- **Per‑match detail** — click any fixture to see the full scoreline distribution.
- **Social share image** — an OpenGraph card auto‑generated from the current favourite.
- **Live updates** — re‑run the pipeline as real 2026 results come in and redeploy, so the
  forecast tracks the tournament.

## 🌅 Later

- **Enable the ML layer** — the ensemble has a gradient‑boosting slot (`w_ml`, currently 0);
  add engineered features and turn it on if it improves calibration.
- **On‑demand API** — a route to regenerate a forecast for a custom `as-of` date.
- **Tests** — pytest coverage for the tiebreaker logic and bracket solver.

> Forecasts are probabilistic. The goal isn't to be "right" about one bracket — it's to be
> well‑calibrated across thousands of them.
