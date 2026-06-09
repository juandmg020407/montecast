"""Temporary end-to-end smoke check for the full pipeline."""
import time

import pandas as pd

from montecast.ingest.load import load_matches
from montecast.models.dixon_coles import DixonColesModel
from montecast.models.elo import EloModel
from montecast.models.ensemble import EnsembleModel
from montecast.simulate.monte_carlo import Simulator
from montecast.tournament import load_tournament

t0 = time.time()
m = load_matches()
t = load_tournament()
ds = list(t.dataset_names().values())
elo = EloModel().fit(m)
dc = DixonColesModel().fit(m, "2026-06-09", force_teams=ds)
ens = EnsembleModel(dc=dc, elo=elo)
print(f"models fit in {time.time() - t0:.1f}s")

sim = Simulator(ens, t)
print(f"simulator ready in {time.time() - t0:.1f}s (incl. advantage matrix)")

N = 20000
t1 = time.time()
res = sim.run(n_sims=N, seed=1)
print(f"simulated {N} tournaments in {time.time() - t1:.1f}s")

code = {n: t.teams[n].code for n in t.teams}
champ = pd.Series(
    {code[n]: res["champion"][i] / N for i, n in enumerate(res["teams"])}
).sort_values(ascending=False)
print("\nChampion probability (top 15):")
for c, p in champ.head(15).items():
    print(f"  {c}  {p * 100:5.1f}%")

print("\n-- conservation checks (expected) --")
print(f"  sum P(champion)      = {res['champion'].sum() / N:.3f}  (1)")
print(f"  mean teams advancing = {res['advance'].sum() / N:.3f}  (32)")
print(f"  sum reach final      = {res['final'].sum() / N:.3f}  (2)")
print(f"  sum reach semi       = {res['semi'].sum() / N:.3f}  (4)")
print(f"  sum reach quarter    = {res['quarter'].sum() / N:.3f}  (8)")
print(f"  sum reach R16        = {res['round16'].sum() / N:.3f}  (16)")
print(f"  sum reach R32        = {res['round32'].sum() / N:.3f}  (32)")

print("\nGroup A:")
for r in res["group_results"]["A"]:
    adv = (r["p_first"] + r["p_second"]) * 100
    print(f"  {r['team']:<14} 1st {r['p_first']*100:4.1f}%  2nd {r['p_second']*100:4.1f}%  "
          f"3rd {r['p_third']*100:4.1f}%  advance {adv:4.1f}%")
