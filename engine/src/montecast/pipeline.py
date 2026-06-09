"""End-to-end pipeline: ingest -> fit models -> simulate -> export JSON.

Run with::

    python -m montecast.pipeline --n-sims 50000
"""
from __future__ import annotations

import argparse
import time
from pathlib import Path

from . import settings
from .export.to_json import export_all
from .ingest.load import load_matches
from .models.dixon_coles import DixonColesModel
from .models.elo import EloModel
from .models.ensemble import EnsembleModel
from .simulate.monte_carlo import Simulator
from .tournament import load_tournament


def run_pipeline(as_of: str, n_sims: int, seed: int, out_dir: Path) -> dict:
    t0 = time.time()
    tournament = load_tournament()
    matches = load_matches()
    force = list(tournament.dataset_names().values())

    elo = EloModel().fit(matches[matches.date <= as_of])
    dc = DixonColesModel().fit(matches, as_of, force_teams=force)
    model = EnsembleModel(dc=dc, elo=elo)
    print(f"[montecast] models fitted ({time.time() - t0:.1f}s)")

    sim = Simulator(model, tournament)
    res = sim.run(n_sims=n_sims, seed=seed)
    print(f"[montecast] {n_sims:,} tournaments simulated ({time.time() - t0:.1f}s)")

    files = export_all(model, res, tournament, elo, dc, out_dir, as_of)
    print(f"[montecast] wrote {len(files)} artifacts -> {out_dir}")
    return res


def main(argv=None) -> None:
    p = argparse.ArgumentParser(description="Montecast World Cup 2026 forecast pipeline")
    p.add_argument("--as-of", default=str(settings.DEFAULT_AS_OF),
                   help="generate the forecast as of this date (YYYY-MM-DD)")
    p.add_argument("--n-sims", type=int, default=50_000)
    p.add_argument("--seed", type=int, default=settings.RANDOM_SEED)
    p.add_argument("--out", default=str(settings.WEB_DATA_DIR),
                   help="output directory for JSON artifacts")
    args = p.parse_args(argv)

    res = run_pipeline(args.as_of, args.n_sims, args.seed, Path(args.out))

    teams, N = res["teams"], res["n_sims"]
    ranked = sorted(range(len(teams)), key=lambda i: res["champion"][i], reverse=True)
    print("\nTitle favourites:")
    for i in ranked[:10]:
        print(f"  {teams[i]:<16} {res['champion'][i] / N * 100:5.1f}%")


if __name__ == "__main__":
    main()
