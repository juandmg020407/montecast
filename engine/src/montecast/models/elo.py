"""International Elo ratings (World Football Elo style).

Elo is used two ways in Montecast: as a strong, interpretable baseline and as
an input feature to the gradient-boosting layer. Ratings evolve match-by-match
with a K-factor scaled by fixture importance and goal margin.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


def match_importance(tournament: str) -> float:
    """K-factor base weight by competition tier (World Football Elo convention)."""
    t = tournament.lower()
    if "world cup" in t and "qual" not in t:
        return 60.0
    if "qual" in t:
        return 40.0
    if any(k in t for k in (
        "uefa euro", "copa am", "african cup", "afc asian", "gold cup",
        "confederations", "nations league",
    )) and "qual" not in t:
        return 50.0
    if t == "friendly":
        return 20.0
    return 30.0


def goal_diff_multiplier(goal_diff: int) -> float:
    """Inflate the update for emphatic wins (World Football Elo formula)."""
    g = abs(goal_diff)
    if g <= 1:
        return 1.0
    if g == 2:
        return 1.5
    return (11.0 + g) / 8.0


def expected_score(rating_home: float, rating_away: float, home_adv: float) -> float:
    """Logistic expectation that the home side wins (draw counts as 0.5)."""
    return 1.0 / (1.0 + 10.0 ** (-((rating_home + home_adv) - rating_away) / 400.0))


@dataclass
class EloModel:
    home_adv: float = 70.0
    init_rating: float = 1500.0
    ratings: dict[str, float] = field(default_factory=dict)

    def fit(self, matches: pd.DataFrame) -> "EloModel":
        """Stream chronologically through matches, updating ratings in place."""
        r: dict[str, float] = {}
        cols = matches[
            ["home_team", "away_team", "home_score", "away_score", "tournament", "neutral"]
        ].itertuples(index=False, name=None)
        for home, away, hs, as_, tournament, neutral in cols:
            rh = r.get(home, self.init_rating)
            ra = r.get(away, self.init_rating)
            ha = 0.0 if neutral else self.home_adv
            exp_h = expected_score(rh, ra, ha)
            gd = hs - as_
            score_h = 1.0 if gd > 0 else (0.5 if gd == 0 else 0.0)
            k = match_importance(tournament) * goal_diff_multiplier(gd)
            delta = k * (score_h - exp_h)
            r[home] = rh + delta
            r[away] = ra - delta
        self.ratings = r
        return self

    def rating(self, team: str) -> float:
        return self.ratings.get(team, self.init_rating)

    def table(self) -> pd.Series:
        """Ratings as a descending-sorted Series."""
        return pd.Series(self.ratings, name="elo").sort_values(ascending=False)

    def win_probabilities(
        self, home: str, away: str, neutral: bool = True
    ) -> tuple[float, float, float]:
        """(P_home, P_draw, P_away) from the rating gap.

        Draw share is modelled as a smooth function of how close the teams are;
        this is only a baseline — the Dixon-Coles model produces the scoreline
        distribution used by the simulator.
        """
        ha = 0.0 if neutral else self.home_adv
        exp_h = expected_score(self.rating(home), self.rating(away), ha)
        # Empirical draw rate peaks (~0.28) for even games and decays as the gap grows.
        p_draw = 0.28 * (1.0 - 2.0 * abs(exp_h - 0.5)) + 0.18 * (2.0 * abs(exp_h - 0.5))
        p_draw = max(0.10, min(0.32, p_draw))
        p_home = (1.0 - p_draw) * exp_h
        p_away = (1.0 - p_draw) * (1.0 - exp_h)
        return p_home, p_draw, p_away
