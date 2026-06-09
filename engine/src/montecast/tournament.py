"""Typed access to the 2026 World Cup configuration (the real final draw)."""
from __future__ import annotations

import json
from dataclasses import dataclass

from . import settings


@dataclass(frozen=True)
class Team:
    name: str           # display name (also the key used across the engine)
    code: str           # FIFA three-letter code
    iso2: str           # ISO-3166 alpha-2 (or gb-eng/gb-sct) for flag rendering
    confederation: str
    group: str
    host: bool
    dataset_name: str   # name as it appears in the historical dataset


@dataclass(frozen=True)
class Tournament:
    name: str
    host_nations: tuple[str, ...]
    start_date: str
    end_date: str
    final_venue: str
    fmt: dict
    groups: dict[str, list[str]]   # group letter -> display names
    teams: dict[str, Team]         # display name -> Team

    @property
    def team_names(self) -> list[str]:
        return list(self.teams)

    def dataset_names(self) -> dict[str, str]:
        """display name -> historical-dataset name."""
        return {t.name: t.dataset_name for t in self.teams.values()}

    def to_dataset(self, display_name: str) -> str:
        return self.teams[display_name].dataset_name


def load_tournament() -> Tournament:
    with open(settings.WC2026_CONFIG, encoding="utf-8") as fh:
        cfg = json.load(fh)

    group_of = {
        name: letter
        for letter, names in cfg["groups"].items()
        for name in names
    }

    teams: dict[str, Team] = {}
    for name, meta in cfg["teams"].items():
        teams[name] = Team(
            name=name,
            code=meta["code"],
            iso2=meta["iso2"],
            confederation=meta["confederation"],
            group=group_of[name],
            host=bool(meta.get("host", False)),
            dataset_name=meta.get("dataset_name", name),
        )

    return Tournament(
        name=cfg["tournament"],
        host_nations=tuple(cfg["host_nations"]),
        start_date=cfg["start_date"],
        end_date=cfg["end_date"],
        final_venue=cfg["final_venue"],
        fmt=cfg["format"],
        groups=cfg["groups"],
        teams=teams,
    )
