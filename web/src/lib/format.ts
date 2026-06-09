export const pct = (x: number, d = 0): string => `${(x * 100).toFixed(d)}%`;
export const pct1 = (x: number): string => `${(x * 100).toFixed(1)}%`;

/** Flag image from flagcdn (supports gb-eng / gb-sct for home nations). */
export const flagUrl = (iso2: string): string =>
  `https://flagcdn.com/${iso2}.svg`;

const CONF: Record<string, string> = {
  UEFA: "var(--color-uefa)",
  CONMEBOL: "var(--color-conmebol)",
  CONCACAF: "var(--color-concacaf)",
  CAF: "var(--color-caf)",
  AFC: "var(--color-afc)",
  OFC: "var(--color-ofc)",
};

export const confColor = (c: string): string => CONF[c] ?? "var(--color-muted)";

export function formatDate(iso: string, lang: "en" | "es"): string {
  const d = new Date(iso);
  return d.toLocaleDateString(lang === "es" ? "es-ES" : "en-GB", {
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}
