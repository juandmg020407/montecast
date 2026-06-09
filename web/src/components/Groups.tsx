"use client";

import { Flag, ProbBar } from "@/components/ui";
import { Reveal } from "@/components/Reveal";
import { useLang } from "@/lib/i18n";
import { pct } from "@/lib/format";
import type { Group, GroupTeam, Fixture, Groups as GroupsData } from "@/lib/types";

function HostTag({ label }: { label: string }) {
  return (
    <span className="ml-1.5 rounded bg-lime-soft px-1.5 py-0.5 align-middle text-[0.55rem] font-medium uppercase tracking-wide text-lime">
      {label}
    </span>
  );
}

function Standing({
  team,
  rank,
  winLabel,
  hostLabel,
}: {
  team: GroupTeam;
  rank: number;
  winLabel: string;
  hostLabel: string;
}) {
  return (
    <div className="flex items-center gap-2.5 py-2">
      <span className="tnum w-3.5 text-xs text-muted">{rank}</span>
      <Flag iso2={team.iso2} alt={team.name} className="h-5 w-7 shrink-0 rounded" />
      <div className="min-w-0 flex-1">
        <div className="flex items-baseline justify-between gap-2">
          <span className="truncate text-sm text-paper">
            {team.name}
            {team.host && <HostTag label={hostLabel} />}
          </span>
          <span className="tnum shrink-0 text-sm text-paper">
            {pct(team.pAdvance)}
          </span>
        </div>
        <div className="mt-1 flex items-center gap-2">
          <ProbBar value={team.pAdvance} tone={rank === 1 ? "lime" : "dim"} height={4} />
          <span className="tnum w-16 shrink-0 text-right text-[0.6rem] text-muted">
            {winLabel} {pct(team.pFirst)}
          </span>
        </div>
      </div>
    </div>
  );
}

function FixtureRow({ fx }: { fx: Fixture }) {
  return (
    <div className="flex items-center gap-2 py-1 text-xs">
      <span className="flex w-14 items-center justify-end gap-1.5">
        <span className="tnum text-paper-dim">{fx.homeCode}</span>
        <Flag iso2={fx.homeIso2} alt={fx.home} className="h-3.5 w-5 rounded-sm" />
      </span>
      <div className="flex h-1.5 flex-1 overflow-hidden rounded-full bg-ink-3">
        <span style={{ width: `${fx.pHome * 100}%`, background: "var(--color-lime)" }} />
        <span style={{ width: `${fx.pDraw * 100}%`, background: "var(--color-ink-3)" }} />
        <span style={{ width: `${fx.pAway * 100}%`, background: "var(--color-paper-dim)" }} />
      </div>
      <span className="flex w-14 items-center gap-1.5">
        <Flag iso2={fx.awayIso2} alt={fx.away} className="h-3.5 w-5 rounded-sm" />
        <span className="tnum text-paper-dim">{fx.awayCode}</span>
      </span>
      <span className="tnum w-8 text-right text-muted">
        {fx.likely.home}–{fx.likely.away}
      </span>
    </div>
  );
}

function GroupCard({ letter, group }: { letter: string; group: Group }) {
  const { t } = useLang();
  const teams = [...group.teams].sort((a, b) => b.pAdvance - a.pAdvance);

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between">
        <h3 className="font-display text-lg font-semibold text-paper">
          {t("br.group")} {letter}
        </h3>
        <span className="eyebrow !text-[0.55rem]">{t("gr.advance")}</span>
      </div>

      <div className="mt-2 divide-y divide-line">
        {teams.map((team, i) => (
          <Standing
            key={team.code}
            team={team}
            rank={i + 1}
            winLabel={t("gr.win")}
            hostLabel={t("gr.host")}
          />
        ))}
      </div>

      <div className="rule my-4" />

      <p className="eyebrow !text-[0.55rem]">{t("gr.fixtures")}</p>
      <div className="mt-2 space-y-0.5">
        {group.fixtures.map((fx, i) => (
          <FixtureRow key={i} fx={fx} />
        ))}
      </div>
    </div>
  );
}

export function Groups({ groups }: { groups: GroupsData }) {
  const { t } = useLang();
  const order = Object.keys(groups).sort();

  return (
    <section id="groups" className="mx-auto max-w-6xl px-5 py-20 sm:px-8">
      <Reveal>
        <p className="eyebrow">02 — {t("nav.groups")}</p>
        <h2 className="mt-3 font-display text-3xl font-medium tracking-tight text-paper sm:text-4xl">
          {t("gr.title")}
        </h2>
        <p className="mt-3 max-w-2xl text-paper-dim">{t("gr.subtitle")}</p>
      </Reveal>

      <div className="mt-10 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
        {order.map((letter, i) => (
          <Reveal key={letter} delay={Math.min(i, 6) * 40}>
            <GroupCard letter={letter} group={groups[letter]} />
          </Reveal>
        ))}
      </div>
    </section>
  );
}
