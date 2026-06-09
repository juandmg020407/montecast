"""Dixon-Coles bivariate-Poisson scoreline model.

For a match between teams i (home) and j (away):

    log(lambda) = attack[i] - defence[j] + home_adv * is_home
    log(mu)     = attack[j] - defence[i]

Home goals ~ Poisson(lambda), away goals ~ Poisson(mu), with the Dixon-Coles
low-score dependence correction tau(x, y; lambda, mu, rho). Parameters are
estimated by maximum likelihood on time-weighted historical matches (recent
games count for more), with L2 shrinkage of attack/defence for identifiability
and stability of rarely-seen teams.

The negative log-likelihood and its analytic gradient live in the module-level
``nll_and_grad`` so they can be unit-tested against finite differences.

Reference: Dixon & Coles (1997), "Modelling Association Football Scores and
Inefficiencies in the Football Betting Market".
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import NamedTuple

import numpy as np
import pandas as pd
from scipy.optimize import minimize


class FitData(NamedTuple):
    hi: np.ndarray        # home-team indices
    ai: np.ndarray        # away-team indices
    x: np.ndarray         # home goals
    y: np.ndarray         # away goals
    w: np.ndarray         # time-decay weights
    home_ind: np.ndarray  # 1.0 if home advantage applies, else 0.0
    m00: np.ndarray
    m01: np.ndarray
    m10: np.ndarray
    m11: np.ndarray


def _tau_values(d: FitData, lam, mu, rho):
    tau = np.ones_like(lam)
    tau[d.m00] = 1.0 - lam[d.m00] * mu[d.m00] * rho
    tau[d.m01] = 1.0 + lam[d.m01] * rho
    tau[d.m10] = 1.0 + mu[d.m10] * rho
    tau[d.m11] = 1.0 - rho
    return tau


def nll_and_grad(theta: np.ndarray, d: FitData, n: int, l2: float):
    """Weighted Dixon-Coles negative log-likelihood and its analytic gradient.

    ``theta`` packs [attack(n), defence(n), home_adv, rho].
    """
    atk = theta[:n]
    dfc = theta[n:2 * n]
    home_adv = theta[2 * n]
    rho = theta[2 * n + 1]

    log_lam = atk[d.hi] - dfc[d.ai] + home_adv * d.home_ind
    log_mu = atk[d.ai] - dfc[d.hi]
    lam = np.exp(log_lam)
    mu = np.exp(log_mu)

    nll = np.sum(d.w * (lam - d.x * log_lam + mu - d.y * log_mu))
    tau = np.clip(_tau_values(d, lam, mu, rho), 1e-10, None)
    nll -= np.sum(d.w * np.log(tau))
    nll += l2 * (np.sum(atk * atk) + np.sum(dfc * dfc))

    g_atk = np.zeros(n)
    g_def = np.zeros(n)
    np.add.at(g_atk, d.hi, d.w * (lam - d.x))
    np.add.at(g_atk, d.ai, d.w * (mu - d.y))
    np.add.at(g_def, d.ai, d.w * (d.x - lam))
    np.add.at(g_def, d.hi, d.w * (d.y - mu))
    g_home = np.sum(d.w * (lam - d.x) * d.home_ind)

    # gradient of the tau correction (non-zero only on low-score cells)
    dl = np.zeros_like(lam)
    dm = np.zeros_like(lam)
    dr = np.zeros_like(lam)
    t00, t01, t10, t11 = tau[d.m00], tau[d.m01], tau[d.m10], tau[d.m11]
    dl[d.m00] = (-mu[d.m00] * rho) / t00
    dm[d.m00] = (-lam[d.m00] * rho) / t00
    dr[d.m00] = (-lam[d.m00] * mu[d.m00]) / t00
    dl[d.m01] = rho / t01
    dr[d.m01] = lam[d.m01] / t01
    dm[d.m10] = rho / t10
    dr[d.m10] = mu[d.m10] / t10
    dr[d.m11] = -1.0 / t11
    np.add.at(g_atk, d.hi, -d.w * dl * lam)
    np.add.at(g_def, d.ai, d.w * dl * lam)
    np.add.at(g_atk, d.ai, -d.w * dm * mu)
    np.add.at(g_def, d.hi, d.w * dm * mu)
    g_home += np.sum(-d.w * dl * lam * d.home_ind)
    g_rho = np.sum(-d.w * dr)

    g_atk += 2 * l2 * atk
    g_def += 2 * l2 * dfc
    grad = np.concatenate([g_atk, g_def, [g_home, g_rho]])
    return nll, grad


@dataclass
class MatchForecast:
    home: str
    away: str
    p_home: float
    p_draw: float
    p_away: float
    exp_home_goals: float
    exp_away_goals: float
    top_scorelines: list[tuple[tuple[int, int], float]]


class DixonColesModel:
    def __init__(
        self,
        half_life_years: float = 1.8,
        window_years: int = 8,
        min_matches: int = 3,
        l2: float = 0.01,
        max_goals: int = 10,
    ):
        self.half_life_years = half_life_years
        self.window_years = window_years
        self.min_matches = min_matches
        self.l2 = l2
        self.max_goals = max_goals

        self.teams: list[str] = []
        self.team_idx: dict[str, int] = {}
        self.attack: np.ndarray | None = None
        self.defence: np.ndarray | None = None
        self.home_adv: float = 0.0
        self.rho: float = 0.0
        self._other: int = 0
        self.opt_result = None

    def prepare(self, matches: pd.DataFrame, as_of, force_teams: list[str] | None = None):
        """Build the index, weighted design arrays and parameter count."""
        as_of = pd.Timestamp(as_of)
        lo = as_of - pd.Timedelta(days=int(self.window_years * 365.25))
        df = matches[(matches.date >= lo) & (matches.date <= as_of)]

        counts = pd.concat([df.home_team, df.away_team]).value_counts()
        keep = set(counts[counts >= self.min_matches].index)
        keep.update(force_teams or [])

        self.teams = sorted(keep)
        self.team_idx = {t: k for k, t in enumerate(self.teams)}
        self._other = len(self.teams)
        n = self._other + 1

        def idx(series):
            return series.map(lambda t: self.team_idx.get(t, self._other)).to_numpy()

        x = df.home_score.to_numpy(dtype=float)
        y = df.away_score.to_numpy(dtype=float)
        age_years = (as_of - df.date).dt.days.to_numpy() / 365.25
        data = FitData(
            hi=idx(df.home_team),
            ai=idx(df.away_team),
            x=x,
            y=y,
            w=0.5 ** (age_years / self.half_life_years),
            home_ind=np.where(df.neutral.to_numpy(), 0.0, 1.0),
            m00=(x == 0) & (y == 0),
            m01=(x == 0) & (y == 1),
            m10=(x == 1) & (y == 0),
            m11=(x == 1) & (y == 1),
        )
        return data, n

    def fit(self, matches: pd.DataFrame, as_of, force_teams: list[str] | None = None) -> "DixonColesModel":
        data, n = self.prepare(matches, as_of, force_teams)

        x0 = np.zeros(2 * n + 2)
        x0[2 * n] = 0.25
        x0[2 * n + 1] = -0.05
        bounds = [(None, None)] * (2 * n) + [(0.0, 1.0), (-0.2, 0.2)]

        res = minimize(
            nll_and_grad, x0, args=(data, n, self.l2), jac=True,
            method="L-BFGS-B", bounds=bounds, options={"maxiter": 500, "ftol": 1e-9},
        )
        self.opt_result = res

        atk = res.x[:n].copy()
        dfc = res.x[n:2 * n].copy()
        shift = atk.mean()
        self.attack = atk - shift
        self.defence = dfc - shift
        self.home_adv = float(res.x[2 * n])
        self.rho = float(res.x[2 * n + 1])
        return self

    # -- prediction ---------------------------------------------------------
    def _rates(self, home, away, home_is_host, away_is_host):
        i = self.team_idx.get(home, self._other)
        j = self.team_idx.get(away, self._other)
        log_lam = self.attack[i] - self.defence[j] + (self.home_adv if home_is_host else 0.0)
        log_mu = self.attack[j] - self.defence[i] + (self.home_adv if away_is_host else 0.0)
        return float(np.exp(log_lam)), float(np.exp(log_mu))

    def scoreline_matrix(self, home, away, home_is_host=False, away_is_host=False) -> np.ndarray:
        """Normalised P(home_goals=x, away_goals=y) over 0..max_goals."""
        lam, mu = self._rates(home, away, home_is_host, away_is_host)

        def pmf(rate):
            p = np.empty(self.max_goals + 1)
            p[0] = np.exp(-rate)
            for r in range(1, self.max_goals + 1):
                p[r] = p[r - 1] * rate / r
            return p

        mat = np.outer(pmf(lam), pmf(mu))
        mat[0, 0] *= 1.0 - lam * mu * self.rho
        mat[0, 1] *= 1.0 + lam * self.rho
        mat[1, 0] *= 1.0 + mu * self.rho
        mat[1, 1] *= 1.0 - self.rho
        mat = np.clip(mat, 0.0, None)
        return mat / mat.sum()

    def predict(self, home, away, **kwargs) -> MatchForecast:
        mat = self.scoreline_matrix(home, away, **kwargs)
        n = mat.shape[0]
        ix = np.arange(n)
        p_home = float(mat[np.greater.outer(ix, ix)].sum())
        p_draw = float(np.trace(mat))
        p_away = float(mat[np.less.outer(ix, ix)].sum())
        exp_h = float((mat.sum(axis=1) * ix).sum())
        exp_a = float((mat.sum(axis=0) * ix).sum())
        flat = [((a, b), float(mat[a, b])) for a in range(n) for b in range(n)]
        flat.sort(key=lambda kv: kv[1], reverse=True)
        return MatchForecast(home, away, p_home, p_draw, p_away, exp_h, exp_a, flat[:5])

    def ratings_table(self) -> pd.DataFrame:
        rows = [
            {"team": t, "attack": self.attack[k], "defence": self.defence[k]}
            for t, k in self.team_idx.items()
        ]
        return pd.DataFrame(rows).sort_values("attack", ascending=False).reset_index(drop=True)
