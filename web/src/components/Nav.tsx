"use client";

import { useLang, type DictKey } from "@/lib/i18n";

const LINKS: { href: string; key: DictKey }[] = [
  { href: "#favourites", key: "nav.favorites" },
  { href: "#groups", key: "nav.groups" },
  { href: "#bracket", key: "nav.bracket" },
  { href: "#method", key: "nav.method" },
];

export function Nav() {
  const { t, lang, toggle } = useLang();

  return (
    <header className="sticky top-0 z-50 border-b border-line bg-ink/70 backdrop-blur-xl">
      <nav className="mx-auto flex h-16 max-w-6xl items-center justify-between px-5 sm:px-8">
        <a href="#top" className="flex items-center gap-2.5">
          <span className="grid h-7 w-7 place-items-center rounded-md bg-lime font-display text-sm font-bold text-ink">
            M
          </span>
          <span className="flex flex-col leading-none">
            <span className="font-display text-base font-semibold tracking-tight text-paper">
              Montecast
            </span>
            <span className="eyebrow !text-[0.55rem] !tracking-[0.16em]">
              {t("brand.tag")}
            </span>
          </span>
        </a>

        <div className="flex items-center gap-1 sm:gap-2">
          <ul className="hidden items-center gap-0.5 md:flex">
            {LINKS.map((l) => (
              <li key={l.href}>
                <a
                  href={l.href}
                  className="rounded-full px-3 py-2 text-sm text-paper-dim transition-colors hover:bg-ink-2 hover:text-paper"
                >
                  {t(l.key)}
                </a>
              </li>
            ))}
          </ul>
          <button
            onClick={toggle}
            aria-label="Toggle language English / Spanish"
            className="ml-1 flex items-center gap-1.5 rounded-full border border-line-strong px-3 py-1.5 font-mono text-xs text-paper-dim transition-colors hover:border-lime"
          >
            <span className={lang === "en" ? "text-lime" : ""}>EN</span>
            <span className="text-muted">/</span>
            <span className={lang === "es" ? "text-lime" : ""}>ES</span>
          </button>
        </div>
      </nav>
    </header>
  );
}
