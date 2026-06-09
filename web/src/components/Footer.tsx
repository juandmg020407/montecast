"use client";

import { useLang } from "@/lib/i18n";
import { formatDate } from "@/lib/format";
import type { Meta } from "@/lib/types";

const REPO = "https://github.com/juandmg020407/montecast";

export function Footer({ meta }: { meta: Meta }) {
  const { t, lang } = useLang();

  return (
    <footer className="relative z-10 border-t border-line">
      <div className="mx-auto flex max-w-6xl flex-col gap-8 px-5 py-12 sm:flex-row sm:items-end sm:justify-between sm:px-8">
        <div>
          <div className="flex items-center gap-2.5">
            <span className="grid h-7 w-7 place-items-center rounded-md bg-lime font-display text-sm font-bold text-ink">
              M
            </span>
            <span className="font-display text-lg font-semibold text-paper">
              Montecast
            </span>
          </div>
          <p className="mt-4 max-w-md text-sm leading-relaxed text-paper-dim">
            {t("ft.tagline")}
          </p>
        </div>

        <div className="text-sm sm:text-right">
          <p className="text-paper">{t("ft.built")}</p>
          <a
            href={REPO}
            target="_blank"
            rel="noopener noreferrer"
            className="mt-1 inline-block font-mono text-xs text-paper-dim underline-offset-4 transition-colors hover:text-lime hover:underline"
          >
            github.com/juandmg020407/montecast
          </a>
          <p className="mt-3 text-xs text-muted">
            {t("ft.generated")} {formatDate(meta.generatedAt, lang)} · v
            {meta.modelVersion}
          </p>
        </div>
      </div>
    </footer>
  );
}
