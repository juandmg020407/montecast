"""Ensemble match model: a Dixon-Coles scoreline shape re-weighted to match
outcome probabilities blended across models.

The Dixon-Coles model owns the *shape* of the scoreline distribution (it is the
only component that produces goals, which the simulator needs for tiebreakers).
Elo — and, when available, a gradient-boosting classifier — contribute
independent win/draw/loss opinions. We blend the three opinions, then rescale
the three regions of the Dixon-Coles scoreline matrix (home win, draw, away
win) so its marginals match the blend while preserving the within-region
scoreline texture. Blend weights are hyperparameters tuned by backtest.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .dixon_coles import DixonColesModel
from .elo import EloModel


@dataclass
class EnsembleModel:
    dc: DixonColesModel
    elo: EloModel
    booster: object | None = None       # optional .predict_proba-style W/D/L model
    w_dc: float = 0.80
    w_elo: float = 0.20
    w_ml: float = 0.0

    def _blend(self, dc_wdl, elo_wdl, ml_wdl):
        w = np.array([self.w_dc, self.w_elo, self.w_ml if ml_wdl is not None else 0.0])
        w = w / w.sum()
        out = w[0] * np.asarray(dc_wdl) + w[1] * np.asarray(elo_wdl)
        if ml_wdl is not None:
            out = out + w[2] * np.asarray(ml_wdl)
        return out / out.sum()

    def scoreline_matrix(self, home, away, home_is_host=False, away_is_host=False) -> np.ndarray:
        mat = self.dc.scoreline_matrix(home, away, home_is_host, away_is_host)
        n = mat.shape[0]
        ix = np.arange(n)
        H = np.greater.outer(ix, ix)
        D = np.equal.outer(ix, ix)
        A = np.less.outer(ix, ix)
        dc_wdl = np.array([mat[H].sum(), mat[D].sum(), mat[A].sum()])

        neutral = not (home_is_host or away_is_host)
        elo_wdl = self.elo.win_probabilities(home, away, neutral=neutral)
        ml_wdl = None
        if self.booster is not None and self.w_ml > 0:
            ml_wdl = self.booster.win_probabilities(home, away, neutral=neutral)

        target = self._blend(dc_wdl, elo_wdl, ml_wdl)

        out = mat.copy()
        for mask, dc_p, t_p in zip((H, D, A), dc_wdl, target):
            if dc_p > 0:
                out[mask] *= t_p / dc_p
        return out / out.sum()

    def outcome_probs(self, home, away, home_is_host=False, away_is_host=False):
        mat = self.scoreline_matrix(home, away, home_is_host, away_is_host)
        n = mat.shape[0]
        ix = np.arange(n)
        p_home = float(mat[np.greater.outer(ix, ix)].sum())
        p_draw = float(np.trace(mat))
        p_away = float(mat[np.less.outer(ix, ix)].sum())
        return p_home, p_draw, p_away

    def predict(self, home, away, home_is_host=False, away_is_host=False):
        """Full match forecast (W/D/L, expected goals, likely scorelines)."""
        from .dixon_coles import MatchForecast

        mat = self.scoreline_matrix(home, away, home_is_host, away_is_host)
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
