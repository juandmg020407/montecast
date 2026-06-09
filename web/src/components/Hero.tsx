"use client";

import { Flag, CountUp } from "@/components/ui";
import { useLang } from "@/lib/i18n";
import { formatDate } from "@/lib/format";
import type { Meta, SimTeam } from "@/lib/types";

export function Hero({ meta, top }: { meta: Meta; top: SimTeam }) {
  const { t, lang } = useLang();

  const stats = [
    { value: meta.nSims, label: t("hero.sims") },
    { value: meta.format.total_matches, label: t("hero.matches") },
    { value: meta.format.teams, label: t("hero.teams") },
  ];

  return (
    <section
      id="top"
      className="relative mx-auto max-w-6xl px-5 pb-16 pt-14 sm:px-8 sm:pt-20"
    >
      <div className="reveal max-w-3xl">
        <p className="eyebrow">{t("hero.eyebrow")}</p>
        <h1 className="mt-5 font-display text-[2.5rem] font-medium leading-[1.04] tracking-tight text-paper sm:text-6xl">
          {t("hero.title")}
        </h1>
        <p className="mt-6 max-w-2xl text-base leading-relaxed text-paper-dim sm:text-lg">
          {t("hero.lead")}
        </p>
      </div>

      <div className="reveal mt-12 grid gap-10 lg:grid-cols-[1.1fr_1fr] lg:items-center">
        {/* Current favourite */}
        <div className="card p-6 sm:p-7" style={{ boxShadow: "var(--shadow-lift)" }}>
          <p className="eyebrow text-gold">{t("common.favourite")}</p>
          <div className="mt-4 flex items-center justify-between gap-5">
            <div className="flex items-center gap-4">
              <Flag
                iso2={top.iso2}
                alt={top.name}
                className="h-12 w-[4.4rem] rounded-md"
              />
              <div>
                <p className="font-display text-2xl font-semibold text-paper sm:text-3xl">
                  {top.name}
                </p>
                <p className="mt-0.5 text-sm text-muted">
                  {t("br.group")} {top.group} · Elo {Math.round(top.elo)}
                </p>
              </div>
            </div>
            <div className="text-right">
              <span className="tnum font-display text-4xl font-semibold text-gold sm:text-5xl">
                <CountUp value={top.champion * 100} decimals={1} suffix="%" />
              </span>
              <p className="mt-0.5 max-w-[7rem] text-right text-xs leading-snug text-muted">
                {t("hero.toWin")}
              </p>
            </div>
          </div>
        </div>

        {/* Headline counters */}
        <div className="grid grid-cols-3 gap-px overflow-hidden rounded-xl border border-line bg-line">
          {stats.map((s) => (
            <div key={s.label} className="bg-ink-1 px-4 py-6 text-center">
              <p className="tnum font-display text-2xl font-semibold text-paper sm:text-3xl">
                <CountUp value={s.value} />
              </p>
              <p className="mt-1.5 text-[0.7rem] uppercase tracking-wider text-muted">
                {s.label}
              </p>
            </div>
          ))}
        </div>
      </div>

      <div className="reveal mt-10 flex flex-wrap items-center gap-x-6 gap-y-3">
        <a
          href="#favourites"
          className="group inline-flex items-center gap-2 rounded-full bg-lime px-6 py-3 text-sm font-semibold text-ink transition hover:brightness-110"
        >
          {t("hero.explore")}
          <span className="transition-transform group-hover:translate-y-0.5">
            ↓
          </span>
        </a>
        <p className="text-xs text-muted">
          {t("hero.asOf")}{" "}
          <span className="text-paper-dim">{formatDate(meta.asOf, lang)}</span>
        </p>
      </div>
    </section>
  );
}
