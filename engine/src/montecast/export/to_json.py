"""Serialise model outputs to the JSON artifacts consumed by the web app."""
from __future__ import annotations

import datetime
import json
from pathlib import Path

import montecast
from ..simulate import bracket as B
from ..simulate.monte_carlo import GROUP_FIXTURES


def _r(x, nd: int = 4) -> float:
    return round(float(x), nd)


def build_meta(tournament, as_of, n_sims) -> dict:
    return {
        "tournament": tournament.name,
        "generatedAt": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "asOf": str(as_of),
        "nSims": n_sims,
        "startDate": tournament.start_date,
        "endDate": tournament.end_date,
        "finalVenue": tournament.final_venue,
        "hostNations": list(tournament.host_nations),
        "format": tournament.fmt,
        "modelVersion": montecast.__version__,
        "engine": "Dixon-Coles x Elo ensemble + Monte Carlo",
    }


def build_teams(tournament, elo, dc) -> list[dict]:
    out = []
    for name, team in tournament.teams.items():
        idx = dc.team_idx.get(team.dataset_name)
        out.append({
            "name": name,
            "code": team.code,
            "iso2": team.iso2,
            "confederation": team.confederation,
            "group": team.group,
            "host": team.host,
            "elo": round(elo.rating(team.dataset_name)),
            "attack": _r(dc.attack[idx], 3) if idx is not None else 0.0,
            "defence": _r(dc.defence[idx], 3) if idx is not None else 0.0,
        })
    return out


def build_simulation(res, tournament) -> list[dict]:
    teams, N = res["teams"], res["n_sims"]
    rows = []
    for i, name in enumerate(teams):
        tm = tournament.teams[name]
        rows.append({
            "name": name, "code": tm.code, "iso2": tm.iso2, "group": tm.group,
            "confederation": tm.confederation, "host": tm.host,
            "elo": None,  # filled by caller-side merge if desired
            "champion": _r(res["champion"][i] / N),
            "final": _r(res["final"][i] / N),
            "semi": _r(res["semi"][i] / N),
            "quarter": _r(res["quarter"][i] / N),
            "r16": _r(res["round16"][i] / N),
            "advance": _r(res["advance"][i] / N),
            "winGroup": _r(res["win_group"][i] / N),
        })
    rows.sort(key=lambda r: r["champion"], reverse=True)
    return rows


def build_groups(res, tournament, model) -> dict:
    teams, N = res["teams"], res["n_sims"]
    advance = {teams[i]: res["advance"][i] / N for i in range(len(teams))}
    out = {}
    for g in B.GROUPS:
        members = tournament.groups[g]
        grmap = {d["team"]: d for d in res["group_results"][g]}
        teams_out = []
        for name in members:
            tm = tournament.teams[name]
            d = grmap[name]
            teams_out.append({
                "name": name, "code": tm.code, "iso2": tm.iso2, "host": tm.host,
                "pFirst": _r(d["p_first"]), "pSecond": _r(d["p_second"]),
                "pThird": _r(d["p_third"]), "pFourth": _r(d["p_fourth"]),
                "pAdvance": _r(advance[name]),
            })
        fixtures = []
        for la, lb in GROUP_FIXTURES:
            hn, an = members[la], members[lb]
            th, ta = tournament.teams[hn], tournament.teams[an]
            fc = model.predict(th.dataset_name, ta.dataset_name,
                               home_is_host=th.host, away_is_host=ta.host)
            (sh, sa), sp = fc.top_scorelines[0]
            fixtures.append({
                "home": hn, "away": an, "homeCode": th.code, "awayCode": ta.code,
                "homeIso2": th.iso2, "awayIso2": ta.iso2,
                "pHome": _r(fc.p_home), "pDraw": _r(fc.p_draw), "pAway": _r(fc.p_away),
                "expHome": _r(fc.exp_home_goals, 2), "expAway": _r(fc.exp_away_goals, 2),
                "likely": {"home": int(sh), "away": int(sa), "p": _r(sp)},
            })
        out[g] = {"teams": teams_out, "fixtures": fixtures}
    return out


def build_bracket() -> dict:
    def slot(s):
        if s[0] == "W":
            return {"type": "winner", "group": s[1]}
        if s[0] == "RU":
            return {"type": "runnerUp", "group": s[1]}
        return {"type": "third", "candidates": list(s[1])}

    return {
        "r32": [{"match": m, "a": slot(a), "b": slot(b)} for m, a, b in B.R32],
        "progression": {
            "r16": [{"match": m, "a": fa, "b": fb} for m, fa, fb in B.R16],
            "qf": [{"match": m, "a": fa, "b": fb} for m, fa, fb in B.QF],
            "sf": [{"match": m, "a": fa, "b": fb} for m, fa, fb in B.SF],
            "final": {"match": B.FINAL[0], "a": B.FINAL[1], "b": B.FINAL[2]},
        },
    }


def export_all(model, res, tournament, elo, dc, out_dir: Path, as_of) -> list[str]:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # merge elo into the simulation rows for convenience
    sim_rows = build_simulation(res, tournament)
    for row in sim_rows:
        row["elo"] = round(elo.rating(tournament.teams[row["name"]].dataset_name))

    artifacts = {
        "meta.json": build_meta(tournament, as_of, res["n_sims"]),
        "teams.json": build_teams(tournament, elo, dc),
        "simulation.json": {"nSims": res["n_sims"], "teams": sim_rows},
        "groups.json": build_groups(res, tournament, model),
        "bracket.json": build_bracket(),
    }
    for name, obj in artifacts.items():
        with open(out_dir / name, "w", encoding="utf-8") as fh:
            json.dump(obj, fh, ensure_ascii=False, indent=2)
    return list(artifacts)
