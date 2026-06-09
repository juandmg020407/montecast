"use client";

import { Flag } from "@/components/ui";
import { Reveal } from "@/components/Reveal";
import { useLang } from "@/lib/i18n";
import { pct1 } from "@/lib/format";
import type {
  Bracket as BracketData,
  BracketSlot,
  GroupTeam,
  Groups as GroupsData,
  Meta,
  SimTeam,
} from "@/lib/types";

/** Most likely occupant of a bracket slot, derived from group standings. */
function occupant(slot: BracketSlot, groups: GroupsData) {
  const best = (letters: string[], key: "pFirst" | "pSecond" | "pThird") => {
    let top: GroupTeam | null = null;
    for (const l of letters) {
      const cand = [...groups[l].teams].sort((a, b) => b[key] - a[key])[0];
      if (!top || cand[key] > top[key]) top = cand;
    }
    return top;
  };

  if (slot.type === "winner" && slot.group)
    return { team: best([slot.group], "pFirst"), seed: slot.group };
  if (slot.type === "runnerUp" && slot.group)
    return { team: best([slot.group], "pSecond"), seed: slot.group };
  const cands = slot.candidates ?? [];
  return { team: best(cands, "pThird"), seed: cands.join("/") };
}

function SlotRow({
  slot,
  groups,
  seedLabel,
}: {
  slot: BracketSlot;
  groups: GroupsData;
  seedLabel: string;
}) {
  const { team, seed } = occupant(slot, groups);
  return (
    <div className="flex items-center gap-2.5 py-1.5">
      {team && (
        <Flag iso2={team.iso2} alt={team.name} className="h-5 w-7 shrink-0 rounded" />
      )}
      <div className="min-w-0">
        <p className="truncate text-sm text-paper">{team?.name ?? "—"}</p>
        <p className="text-[0.58rem] uppercase tracking-wide text-muted">
          {seedLabel} {seed}
        </p>
      </div>
    </div>
  );
}

export function Bracket({
  bracket,
  groups,
  teams,
  meta,
}: {
  bracket: BracketData;
  groups: GroupsData;
  teams: SimTeam[];
  meta: Meta;
}) {
  const { t } = useLang();
  const favourite = [...teams].sort((a, b) => b.champion - a.champion)[0];
  const rounds = ["br.r32", "br.r16", "br.qf", "br.sf", "br.final"] as const;
  const matches = [...bracket.r32].sort((a, b) => a.match - b.match);

  const seedLabel = (slot: BracketSlot) =>
    slot.type === "winner"
      ? t("br.winner")
      : slot.type === "runnerUp"
        ? t("br.runner")
        : t("br.third");

  return (
    <section id="bracket" className="mx-auto max-w-6xl px-5 py-20 sm:px-8">
      <Reveal>
        <p className="eyebrow">03 — {t("nav.bracket")}</p>
        <h2 className="mt-3 font-display text-3xl font-medium tracking-tight text-paper sm:text-4xl">
          {t("br.title")}
        </h2>
        <p className="mt-3 max-w-2xl text-paper-dim">{t("br.subtitle")}</p>
      </Reveal>

      {/* round rail */}
      <Reveal className="mt-8 flex flex-wrap items-center gap-2 text-xs">
        {rounds.map((r, i) => (
          <span key={r} className="flex items-center gap-2">
            <span
              className={`rounded-full border px-3 py-1 ${
                i === rounds.length - 1
                  ? "border-gold/50 text-gold"
                  : "border-line-strong text-paper-dim"
              }`}
            >
              {t(r)}
            </span>
            {i < rounds.length - 1 && <span className="text-muted">→</span>}
          </span>
        ))}
      </Reveal>

      {/* projected Round of 32 */}
      <div className="mt-8 grid gap-3 sm:grid-cols-2">
        {matches.map((m, i) => (
          <Reveal key={m.match} delay={Math.min(i, 10) * 25}>
            <div className="card p-3.5">
              <span className="eyebrow !text-[0.55rem]">
                {t("br.r32")} · {m.match}
              </span>
              <div className="mt-1 divide-y divide-line">
                <SlotRow slot={m.a} groups={groups} seedLabel={seedLabel(m.a)} />
                <SlotRow slot={m.b} groups={groups} seedLabel={seedLabel(m.b)} />
              </div>
            </div>
          </Reveal>
        ))}
      </div>

      {/* the final */}
      <Reveal className="mt-8">
        <div
          className="card relative overflow-hidden p-7 text-center"
          style={{ boxShadow: "var(--shadow-lift)" }}
        >
          <p className="eyebrow text-gold">{t("br.final")}</p>
          <p className="mt-1.5 text-sm text-paper-dim">{meta.finalVenue}</p>
          {favourite && (
            <div className="mt-5 flex items-center justify-center gap-4">
              <Flag
                iso2={favourite.iso2}
                alt={favourite.name}
                className="h-11 w-16 rounded-md"
              />
              <div className="text-left">
                <p className="font-display text-2xl font-semibold text-paper">
                  {favourite.name}
                </p>
                <p className="tnum text-gold">
                  {pct1(favourite.champion)}{" "}
                  <span className="text-sm text-muted">{t("hero.toWin")}</span>
                </p>
              </div>
            </div>
          )}
        </div>
      </Reveal>
    </section>
  );
}
