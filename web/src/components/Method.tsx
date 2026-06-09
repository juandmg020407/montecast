"use client";

import { CountUp } from "@/components/ui";
import { Reveal } from "@/components/Reveal";
import { useLang, type DictKey } from "@/lib/i18n";
import type { Meta } from "@/lib/types";

export function Method({ meta }: { meta: Meta }) {
  const { t } = useLang();

  const cards: { title: DictKey; body: DictKey }[] = [
    { title: "mt.p1.t", body: "mt.p1.b" },
    { title: "mt.p2.t", body: "mt.p2.b" },
    { title: "mt.p3.t", body: "mt.p3.b" },
    { title: "mt.p4.t", body: "mt.p4.b" },
  ];

  return (
    <section id="method" className="mx-auto max-w-6xl px-5 py-20 sm:px-8">
      <Reveal>
        <p className="eyebrow">04 — {t("nav.method")}</p>
        <h2 className="mt-3 font-display text-3xl font-medium tracking-tight text-paper sm:text-4xl">
          {t("mt.title")}
        </h2>
        <p className="mt-3 max-w-2xl text-paper-dim">{t("mt.subtitle")}</p>
      </Reveal>

      <div className="mt-10 grid gap-4 md:grid-cols-2">
        {cards.map((c, i) => (
          <Reveal key={c.title} delay={i * 50}>
            <div className="card h-full p-6 sm:p-7">
              <span className="font-mono text-xs text-lime">
                {String(i + 1).padStart(2, "0")}
              </span>
              <h3 className="mt-3 font-display text-xl font-semibold text-paper">
                {t(c.title)}
              </h3>
              <p className="mt-2.5 text-sm leading-relaxed text-paper-dim">
                {t(c.body)}
              </p>
            </div>
          </Reveal>
        ))}
      </div>

      <Reveal className="mt-6">
        <div className="grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-line bg-line md:grid-cols-4">
          <div className="bg-ink-1 px-4 py-6 text-center">
            <p className="font-display text-2xl font-semibold text-paper">150</p>
            <p className="mt-1.5 text-[0.68rem] uppercase tracking-wide text-muted">
              {t("mt.stat.matches")}
            </p>
          </div>
          <div className="bg-ink-1 px-4 py-6 text-center">
            <p className="tnum font-display text-2xl font-semibold text-paper">
              <CountUp value={meta.nSims} />
            </p>
            <p className="mt-1.5 text-[0.68rem] uppercase tracking-wide text-muted">
              {t("mt.stat.sims")}
            </p>
          </div>
          <div className="bg-ink-1 px-4 py-6 text-center">
            <p className="font-display text-lg font-semibold text-paper">
              {t("mt.stat.params.v")}
            </p>
            <p className="mt-1.5 text-[0.68rem] uppercase tracking-wide text-muted">
              {t("mt.stat.params")}
            </p>
          </div>
          <div className="bg-ink-1 px-4 py-6 text-center">
            <p className="font-display text-lg font-semibold text-paper">
              Monte Carlo
            </p>
            <p className="mt-1.5 text-[0.68rem] uppercase tracking-wide text-muted">
              {t("mt.stat.engine")}
            </p>
          </div>
        </div>
      </Reveal>
    </section>
  );
}
