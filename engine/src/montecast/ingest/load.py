"""Load and clean the historical international-results dataset.

Source: the community-maintained "International football results from 1872
to the present" dataset (martj42/international_results). We normalise
historical team names to their modern equivalents so a nation's rating has
a continuous history (e.g. West Germany -> Germany).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .. import settings


def load_former_names() -> pd.DataFrame:
    """Mapping of former national-team names to their current names."""
    df = pd.read_csv(settings.FORMER_NAMES_CSV, encoding="utf-8")
    df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")
    df["end_date"] = pd.to_datetime(df["end_date"], errors="coerce")
    return df


def _apply_former_names(df: pd.DataFrame, former: pd.DataFrame) -> pd.DataFrame:
    """Replace former names with current ones, respecting validity dates."""
    fmap: dict[str, list[tuple[str, pd.Timestamp, pd.Timestamp]]] = {}
    for r in former.itertuples(index=False):
        fmap.setdefault(r.former, []).append((r.current, r.start_date, r.end_date))

    def resolve(name: str, date: pd.Timestamp) -> str:
        for current, start, end in fmap.get(name, ()):
            if (pd.isna(start) or date >= start) and (pd.isna(end) or date <= end):
                return current
        return name

    for col in ("home_team", "away_team"):
        mask = df[col].isin(fmap)
        if mask.any():
            df.loc[mask, col] = [
                resolve(n, d) for n, d in zip(df.loc[mask, col], df.loc[mask, "date"])
            ]
    return df


def load_matches(apply_renames: bool = True) -> pd.DataFrame:
    """Return a clean, chronologically sorted match dataframe.

    Columns: date, home_team, away_team, home_score, away_score, tournament,
    city, country, neutral (bool), outcome (H/D/A), total_goals (int).
    """
    df = pd.read_csv(settings.RESULTS_CSV, encoding="utf-8")
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.dropna(subset=["date", "home_score", "away_score"]).copy()
    df["home_score"] = df["home_score"].astype(int)
    df["away_score"] = df["away_score"].astype(int)
    df["neutral"] = (
        df["neutral"].astype(str).str.strip().str.lower().isin(("true", "1", "yes"))
    )

    if apply_renames:
        df = _apply_former_names(df, load_former_names())

    df["outcome"] = np.select(
        [df.home_score > df.away_score, df.home_score < df.away_score],
        ["H", "A"],
        default="D",
    )
    df["total_goals"] = df.home_score + df.away_score
    return df.sort_values("date").reset_index(drop=True)
