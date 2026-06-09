"use client";

import { useState } from "react";
import { Flag, ProbBar } from "@/components/ui";
import { Reveal } from "@/components/Reveal";
import { useLang, type DictKey } from "@/lib/i18n";
import { pct1 } from "@/lib/format";
import type { SimTeam } from "@/lib/types";

const ROW = "grid-cols-[1.75rem_minmax(0,1fr)_auto] md:grid-cols-[2.5rem_minmax(0,1fr)_9rem_repeat(4,3rem)]";

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="hidden text-center md:block">
      <p className="tnum text-sm text-paper">{pct1(value)}</p>
      <p className="mt-0.5 text-[0.58rem] uppercase tracking-wide text-muted">
        {label}
      </p>
    </div>
  );
}

export function Favourites({ teams }: { teams: SimTeam[] }) {
  const { t } = useLang();
  const [showAll, setShowAll] = useState(false);

  const ranked = [...teams].sort((a, b) => b.champion - a.champion);
  const max = ranked[0]?.champion ?? 1;
  const shown = showAll ? ranked : ranked.slice(0, 16);

  const path: { key: DictKey; field: keyof SimTeam }[] = [
    { key: "lb.r16", field: "r16" },
    { key: "lb.quarter", field: "quarter" },
    { key: "lb.semi", field: "semi" },
    { key: "lb.final", field: "final" },
  ];

  return (
    <section id="favourites" className="mx-auto max-w-6xl px-5 py-20 sm:px-8">
      <Reveal>
        <p className="eyebrow">01 — {t("nav.favorites")}</p>
        <h2 className="mt-3 font-display text-3xl font-medium tracking-tight text-paper sm:text-4xl">
          {t("lb.title")}
        </h2>
        <p className="mt-3 max-w-2xl text-paper-dim">{t("lb.subtitle")}</p>
      </Reveal>

      <div className="mt-10 overflow-hidden rounded-xl border border-line">
        {/* column headers (md+) */}
        <div
          className={`hidden items-center gap-3 border-b border-line bg-ink-1 px-4 py-2.5 text-[0.62rem] uppercase tracking-wider text-muted md:grid ${ROW}`}
        >
          <span>#</span>
          <span>{t("brand.tag")}</span>
          <span>{t("lb.champion")}</span>
          {path.map((p) => (
            <span key={p.key} className="text-center">
              {t(p.key)}
            </span>
          ))}
        </div>

        {shown.map((team, i) => (
          <Reveal key={team.code} delay={Math.min(i, 14) * 22}>
            <div
              className={`grid items-center gap-3 border-b border-line px-4 py-3 transition-colors last:border-0 hover:bg-ink-1/60 ${ROW}`}
            >
              <span
                className={`tnum text-sm ${i === 0 ? "text-gold" : "text-muted"}`}
              >
                {i + 1}
              </span>

              <div className="flex min-w-0 items-center gap-3">
                <Flag
                  iso2={team.iso2}
                  alt={team.name}
                  className="h-6 w-9 shrink-0 rounded"
                />
                <div className="min-w-0">
                  <p className="truncate font-medium text-paper">{team.name}</p>
                  <p className="text-xs text-muted">
                    {team.group} · Elo {Math.round(team.elo)}
                  </p>
                </div>
              </div>

              {/* champion: bar on md+, plain % on mobile */}
              <div className="hidden items-center gap-2 md:flex">
                <ProbBar
                  value={team.champion}
                  max={max}
                  tone={i === 0 ? "gold" : "lime"}
                  delay={Math.min(i, 14) * 22}
                />
                <span className="tnum w-11 shrink-0 text-right text-sm text-paper">
                  {pct1(team.champion)}
                </span>
              </div>
              <span className="tnum text-right text-sm font-medium text-paper md:hidden">
                {pct1(team.champion)}
              </span>

              {path.map((p) => (
                <Stat
                  key={p.key}
                  label={t(p.key)}
                  value={team[p.field] as number}
                />
              ))}
            </div>
          </Reveal>
        ))}
      </div>

      <div className="mt-6 text-center">
        <button
          onClick={() => setShowAll((s) => !s)}
          className="rounded-full border border-line-strong px-5 py-2.5 text-sm text-paper-dim transition-colors hover:border-lime hover:text-lime"
        >
          {showAll ? t("lb.showLess") : t("lb.showAll")}
        </button>
      </div>
    </section>
  );
}
