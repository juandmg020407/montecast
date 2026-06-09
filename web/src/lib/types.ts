export interface Meta {
  tournament: string;
  generatedAt: string;
  asOf: string;
  nSims: number;
  startDate: string;
  endDate: string;
  finalVenue: string;
  hostNations: string[];
  format: {
    teams: number;
    groups: number;
    group_size: number;
    qualify_per_group: number;
    best_thirds: number;
    total_matches: number;
    knockout_rounds: string[];
  };
  modelVersion: string;
  engine: string;
}

export interface TeamInfo {
  name: string;
  code: string;
  iso2: string;
  confederation: string;
  group: string;
  host: boolean;
  elo: number;
  attack: number;
  defence: number;
}

export interface SimTeam {
  name: string;
  code: string;
  iso2: string;
  group: string;
  confederation: string;
  host: boolean;
  elo: number;
  champion: number;
  final: number;
  semi: number;
  quarter: number;
  r16: number;
  advance: number;
  winGroup: number;
}

export interface Simulation {
  nSims: number;
  teams: SimTeam[];
}

export interface GroupTeam {
  name: string;
  code: string;
  iso2: string;
  host: boolean;
  pFirst: number;
  pSecond: number;
  pThird: number;
  pFourth: number;
  pAdvance: number;
}

export interface Fixture {
  home: string;
  away: string;
  homeCode: string;
  awayCode: string;
  homeIso2: string;
  awayIso2: string;
  pHome: number;
  pDraw: number;
  pAway: number;
  expHome: number;
  expAway: number;
  likely: { home: number; away: number; p: number };
}

export interface Group {
  teams: GroupTeam[];
  fixtures: Fixture[];
}

export type Groups = Record<string, Group>;

export interface BracketSlot {
  type: "winner" | "runnerUp" | "third";
  group?: string;
  candidates?: string[];
}

export interface R32Match {
  match: number;
  a: BracketSlot;
  b: BracketSlot;
}

export interface Feeder {
  match: number;
  a: number;
  b: number;
}

export interface Bracket {
  r32: R32Match[];
  progression: {
    r16: Feeder[];
    qf: Feeder[];
    sf: Feeder[];
    final: { match: number; a: number; b: number };
  };
}

export interface MontecastData {
  meta: Meta;
  teams: TeamInfo[];
  simulation: Simulation;
  groups: Groups;
  bracket: Bracket;
}
