"""Monte Carlo tournament simulator for the 48-team 2026 World Cup.

Each replication: sample all 72 group scorelines, rank every group with FIFA
tiebreakers, pick the eight best third-placed teams, solve the bracket matching,
then play the 32-team knockout to a champion. The group stage is vectorised
across all replications; the knockout carries team-id arrays through the fixed
bracket so every round is a single vectorised step. Aggregating millions of
simulated matches yields each nation's probability of reaching every stage.
"""
from __future__ import annotations

import numpy as np

from ..tournament import Tournament
from . import bracket as B
from .tiebreakers import rank_group

# Round-robin schedule for four teams (local indices).
GROUP_FIXTURES = [(0, 1), (2, 3), (0, 3), (1, 2), (0, 2), (1, 3)]


class Simulator:
    def __init__(self, model, tournament: Tournament, max_goals: int = 10):
        self.model = model
        self.t = tournament
        self.max_goals = max_goals

        self.teams = list(tournament.teams)                 # canonical order
        self.n = len(self.teams)
        self.idx = {name: i for i, name in enumerate(self.teams)}
        self.ds = [tournament.teams[name].dataset_name for name in self.teams]
        self.host = [tournament.teams[name].host for name in self.teams]
        self.group_members = {
            g: [self.idx[name] for name in tournament.groups[g]] for g in B.GROUPS
        }

        K = max_goals + 1
        self._flat_h = np.repeat(np.arange(K), K)   # flat index -> home goals
        self._flat_a = np.tile(np.arange(K), K)     # flat index -> away goals
        self._build_group_fixtures()
        self._build_advantage_matrix()

    # -- precomputation -----------------------------------------------------
    def _build_group_fixtures(self):
        self.fixtures: dict[str, list[tuple[int, int, np.ndarray]]] = {}
        for g in B.GROUPS:
            gm = self.group_members[g]
            fixtures = []
            for la, lb in GROUP_FIXTURES:
                ga, gb = gm[la], gm[lb]
                mat = self.model.scoreline_matrix(
                    self.ds[ga], self.ds[gb],
                    home_is_host=self.host[ga], away_is_host=self.host[gb],
                )
                cdf = np.cumsum(mat.ravel())
                cdf[-1] = 1.0
                fixtures.append((la, lb, cdf))
            self.fixtures[g] = fixtures

    def _build_advantage_matrix(self):
        """adv[i, j] = P(team i eliminates team j) in a neutral knockout."""
        n = self.n
        adv = np.full((n, n), 0.5)
        for i in range(n):
            for j in range(n):
                if i == j:
                    continue
                ph, pd, pa = self.model.outcome_probs(self.ds[i], self.ds[j])
                denom = ph + pa
                adv[i, j] = ph + (pd * ph / denom if denom > 0 else 0.5 * pd)
        self.adv = adv

    # -- simulation ---------------------------------------------------------
    def run(self, n_sims: int = 50_000, seed: int = 20260611) -> dict:
        rng = np.random.default_rng(seed)
        N, n = n_sims, self.n
        Ksq = (self.max_goals + 1) ** 2

        winners: dict[str, np.ndarray] = {}
        runners: dict[str, np.ndarray] = {}
        third_gid: dict[str, np.ndarray] = {}
        third_pts: dict[str, np.ndarray] = {}
        third_gd: dict[str, np.ndarray] = {}
        third_gf: dict[str, np.ndarray] = {}
        group_order: dict[str, np.ndarray] = {}

        for g in B.GROUPS:
            gm = np.array(self.group_members[g])
            pts = np.zeros((N, 4))
            gf = np.zeros((N, 4))
            ga = np.zeros((N, 4))
            sampled = []
            for la, lb, cdf in self.fixtures[g]:
                k = np.searchsorted(cdf, rng.random(N))
                np.clip(k, 0, Ksq - 1, out=k)
                hg = self._flat_h[k]
                ag = self._flat_a[k]
                gf[:, la] += hg
                ga[:, la] += ag
                gf[:, lb] += ag
                ga[:, lb] += hg
                home_win, away_win = hg > ag, hg < ag
                draw = ~(home_win | away_win)
                pts[:, la] += 3 * home_win + draw
                pts[:, lb] += 3 * away_win + draw
                sampled.append((la, lb, hg, ag))
            gd = gf - ga

            key = pts * 1e6 + (gd + 100.0) * 1e3 + gf
            order_local = np.argsort(-key, axis=1, kind="stable")

            # Head-to-head fallback for groups tied on points/GD/GF.
            tied = np.any(np.diff(np.sort(key, axis=1), axis=1) == 0, axis=1)
            for s in np.nonzero(tied)[0]:
                results = [(la, lb, int(hg[s]), int(ag[s])) for la, lb, hg, ag in sampled]
                order_local[s] = rank_group(results, rng.random(4))[0]

            order_global = gm[order_local]
            group_order[g] = order_global
            winners[g] = order_global[:, 0]
            runners[g] = order_global[:, 1]
            third_gid[g] = order_global[:, 2]
            rows = np.arange(N)
            tl = order_local[:, 2]
            third_pts[g] = pts[rows, tl]
            third_gd[g] = gd[rows, tl]
            third_gf[g] = gf[rows, tl]

        # -- rank third-placed teams; pick best 8 groups per sim ------------
        gl = B.GROUPS
        tp = np.stack([third_pts[g] for g in gl], axis=1)
        tgd = np.stack([third_gd[g] for g in gl], axis=1)
        tgf = np.stack([third_gf[g] for g in gl], axis=1)
        tkey = tp * 1e6 + (tgd + 100.0) * 1e3 + tgf + rng.random((N, 12)) * 1e-3
        top8 = np.argsort(-tkey, axis=1, kind="stable")[:, :8]

        third_slot_team = {m: np.empty(N, dtype=np.int64) for m in B.THIRD_SLOTS}
        for s in range(N):
            qualified = {gl[p] for p in top8[s]}
            for m, grp in B.assign_thirds(qualified).items():
                third_slot_team[m][s] = third_gid[grp][s]

        # -- knockout bracket (vectorised) ----------------------------------
        def play(a: np.ndarray, b: np.ndarray) -> np.ndarray:
            return np.where(rng.random(N) < self.adv[a, b], a, b)

        def resolve(slot, match_number) -> np.ndarray:
            kind = slot[0]
            if kind == "W":
                return winners[slot[1]]
            if kind == "RU":
                return runners[slot[1]]
            return third_slot_team[match_number]

        win: dict[int, np.ndarray] = {}
        r32_participants = []
        for m, sa, sb in B.R32:
            a = resolve(sa, m)
            b = resolve(sb, m)
            r32_participants.extend((a, b))
            win[m] = play(a, b)
        for m, fa, fb in B.R16 + B.QF + B.SF:
            win[m] = play(win[fa], win[fb])
        champion = play(win[B.FINAL[1]], win[B.FINAL[2]])

        # -- aggregate ------------------------------------------------------
        def counts(ids_iterable) -> np.ndarray:
            return np.bincount(np.concatenate(ids_iterable), minlength=n).astype(float)

        win_group = np.zeros(n)
        advance = np.zeros(n)
        for g in B.GROUPS:
            win_group += np.bincount(winners[g], minlength=n)
            advance += np.bincount(winners[g], minlength=n)
            advance += np.bincount(runners[g], minlength=n)
            mask = np.any(top8 == gl.index(g), axis=1)
            advance += np.bincount(third_gid[g][mask], minlength=n)

        group_results = {}
        for g in B.GROUPS:
            go = group_order[g]
            place = np.stack([np.bincount(go[:, p], minlength=n) for p in range(4)])
            group_results[g] = [
                {
                    "team": self.teams[m],
                    "p_first": place[0, m] / N,
                    "p_second": place[1, m] / N,
                    "p_third": place[2, m] / N,
                    "p_fourth": place[3, m] / N,
                }
                for m in self.group_members[g]
            ]

        return {
            "n_sims": N,
            "teams": self.teams,
            "champion": np.bincount(champion, minlength=n).astype(float),
            "final": counts([win[101], win[102]]),
            "semi": counts([win[97], win[98], win[99], win[100]]),
            "quarter": counts([win[m] for m, *_ in B.R16]),
            "round16": counts([win[m] for m, *_ in B.R32]),
            "round32": counts(r32_participants),
            "advance": advance,
            "win_group": win_group,
            "group_results": group_results,
        }
