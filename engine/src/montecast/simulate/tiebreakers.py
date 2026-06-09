"""FIFA group-stage tiebreakers and best-third ranking.

Ranking criteria (2026 regulations), applied in order:
  1. Points
  2. Goal difference (all group matches)
  3. Goals scored (all group matches)
  4. Head-to-head among teams still level: points, then GD, then goals
  5. Drawing of lots  -> a seeded random key (we skip fair-play, which we
     cannot simulate)

For the eight best third-placed teams, only the overall criteria (1-3) plus
the random key apply, since the teams come from different groups.
"""
from __future__ import annotations

import numpy as np

GroupResult = tuple[int, int, int, int]  # (home_local, away_local, home_goals, away_goals)


def _overall(results: list[GroupResult]):
    pts = np.zeros(4)
    gf = np.zeros(4)
    ga = np.zeros(4)
    for i, j, gi, gj in results:
        gf[i] += gi
        ga[i] += gj
        gf[j] += gj
        ga[j] += gi
        if gi > gj:
            pts[i] += 3
        elif gi < gj:
            pts[j] += 3
        else:
            pts[i] += 1
            pts[j] += 1
    return pts, gf - ga, gf


def _sort_h2h(block: list[int], results: list[GroupResult], rand: np.ndarray) -> list[int]:
    s = set(block)
    hp = dict.fromkeys(block, 0)
    hgf = dict.fromkeys(block, 0)
    hga = dict.fromkeys(block, 0)
    for i, j, gi, gj in results:
        if i in s and j in s:
            hgf[i] += gi
            hga[i] += gj
            hgf[j] += gj
            hga[j] += gi
            if gi > gj:
                hp[i] += 3
            elif gi < gj:
                hp[j] += 3
            else:
                hp[i] += 1
                hp[j] += 1
    return sorted(
        block,
        key=lambda t: (hp[t], hgf[t] - hga[t], hgf[t], rand[t]),
        reverse=True,
    )


def rank_group(results: list[GroupResult], rand: np.ndarray):
    """Return finishing order (best->worst, local indices) and per-team stats."""
    pts, gd, gf = _overall(results)
    order = sorted(range(4), key=lambda t: (pts[t], gd[t], gf[t], rand[t]), reverse=True)

    # Re-sort any block tied on the overall criteria using head-to-head.
    resolved: list[int] = []
    i = 0
    while i < len(order):
        j = i
        key = (pts[order[i]], gd[order[i]], gf[order[i]])
        while j + 1 < len(order) and (pts[order[j + 1]], gd[order[j + 1]], gf[order[j + 1]]) == key:
            j += 1
        block = order[i:j + 1]
        resolved.extend(_sort_h2h(block, results, rand) if len(block) > 1 else block)
        i = j + 1

    return resolved, pts, gd, gf


def rank_thirds(thirds: list[tuple[str, float, float, float]], rand: dict[str, float]):
    """Rank the 12 third-placed teams; return the 8 qualifiers (group letters).

    ``thirds`` items are (group_letter, points, goal_diff, goals_for).
    """
    ordered = sorted(
        thirds,
        key=lambda r: (r[1], r[2], r[3], rand[r[0]]),
        reverse=True,
    )
    return [g for g, *_ in ordered[:8]]
