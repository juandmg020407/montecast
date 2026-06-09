"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

export type Lang = "en" | "es";

export const dict = {
  en: {
    "brand.tag": "World Cup 2026 Forecast",
    "nav.favorites": "Favourites",
    "nav.groups": "Groups",
    "nav.bracket": "Bracket",
    "nav.method": "Method",

    "hero.eyebrow": "Monte Carlo Forecast",
    "hero.title": "Who lifts the trophy in 2026?",
    "hero.lead":
      "We simulate the entire 48-team tournament tens of thousands of times with a model trained on 150 years of international football — then read off who is most likely to lift the trophy.",
    "hero.toWin": "to win it all",
    "hero.sims": "simulations",
    "hero.matches": "matches",
    "hero.teams": "teams",
    "hero.asOf": "Forecast as of",
    "hero.explore": "Explore the forecast",

    "lb.title": "The Favourites",
    "lb.subtitle":
      "Probability of being crowned champion, across every simulated tournament.",
    "lb.champion": "Champion",
    "lb.path": "Road to glory",
    "lb.r16": "R16",
    "lb.quarter": "QF",
    "lb.semi": "SF",
    "lb.final": "Final",
    "lb.win": "Win",
    "lb.showAll": "Show all 48 nations",
    "lb.showLess": "Show top 16 only",
    "lb.elo": "Elo",

    "gr.title": "The Groups",
    "gr.subtitle":
      "Twelve groups of four. The top two of each — plus the eight best third-placed teams — reach the Round of 32.",
    "gr.advance": "Advance",
    "gr.win": "Win grp",
    "gr.fixtures": "Match forecasts",
    "gr.draw": "Draw",
    "gr.likely": "Likely",
    "gr.host": "Host",

    "br.title": "The Bracket",
    "br.subtitle":
      "The official knockout path, from a 32-team Round of 32 to the final at MetLife Stadium. Each slot shows its most likely occupant.",
    "br.r32": "Round of 32",
    "br.r16": "Round of 16",
    "br.qf": "Quarter-finals",
    "br.sf": "Semi-finals",
    "br.final": "Final",
    "br.winner": "Winner",
    "br.runner": "Runner-up",
    "br.third": "3rd",
    "br.group": "Group",
    "br.toReachFinal": "to reach the final",

    "mt.title": "How it works",
    "mt.subtitle": "A genuine forecasting engine, not a bracket generator.",
    "mt.p1.t": "Team strength",
    "mt.p1.b":
      "A time-weighted Dixon-Coles bivariate-Poisson model estimates every nation's attack and defence from recent results, blended with an international Elo rating. Recent matches count for more.",
    "mt.p2.t": "Every scoreline",
    "mt.p2.b":
      "For any matchup the model returns a full distribution over scorelines — not just who wins, but by how much — including the Dixon-Coles low-score correction and host advantage.",
    "mt.p3.t": "50,000 tournaments",
    "mt.p3.b":
      "We play the whole tournament tens of thousands of times: real group fixtures, FIFA tiebreakers, the eight best thirds, and the official Round-of-32 bracket, all the way to a champion.",
    "mt.p4.t": "Honest probabilities",
    "mt.p4.b":
      "Aggregating millions of simulated matches yields calibrated odds for every stage. The engine is open-source and regenerates as real results come in.",
    "mt.stat.matches": "Historical matches",
    "mt.stat.params": "Model",
    "mt.stat.params.v": "Dixon-Coles × Elo",
    "mt.stat.sims": "Simulations",
    "mt.stat.engine": "Engine",

    "ft.built": "Built by Juan Morales",
    "ft.tagline":
      "An open-source data-science portfolio project. Forecasts are probabilistic — upsets are the point.",
    "ft.generated": "Generated",
    "common.champion": "Champion",
    "common.favourite": "Favourite",
  },
  es: {
    "brand.tag": "Pronóstico Mundial 2026",
    "nav.favorites": "Favoritos",
    "nav.groups": "Grupos",
    "nav.bracket": "Cuadro",
    "nav.method": "Método",

    "hero.eyebrow": "Pronóstico Monte Carlo",
    "hero.title": "¿Quién levanta la copa en 2026?",
    "hero.lead":
      "Simulamos el torneo completo de 48 selecciones decenas de miles de veces con un modelo entrenado con 150 años de fútbol internacional — y leemos quién tiene más probabilidades de levantar la copa.",
    "hero.toWin": "de ganarlo todo",
    "hero.sims": "simulaciones",
    "hero.matches": "partidos",
    "hero.teams": "selecciones",
    "hero.asOf": "Pronóstico a fecha de",
    "hero.explore": "Explora el pronóstico",

    "lb.title": "Los Favoritos",
    "lb.subtitle":
      "Probabilidad de proclamarse campeón, en todos los torneos simulados.",
    "lb.champion": "Campeón",
    "lb.path": "Camino a la gloria",
    "lb.r16": "16avos",
    "lb.quarter": "4tos",
    "lb.semi": "Semis",
    "lb.final": "Final",
    "lb.win": "Gana",
    "lb.showAll": "Ver las 48 selecciones",
    "lb.showLess": "Ver solo el top 16",
    "lb.elo": "Elo",

    "gr.title": "Los Grupos",
    "gr.subtitle":
      "Doce grupos de cuatro. Los dos primeros de cada uno — más los ocho mejores terceros — pasan a la ronda de 32.",
    "gr.advance": "Pasa",
    "gr.win": "Gana grp",
    "gr.fixtures": "Pronóstico de partidos",
    "gr.draw": "Empate",
    "gr.likely": "Probable",
    "gr.host": "Anfitrión",

    "br.title": "El Cuadro",
    "br.subtitle":
      "El cuadro oficial de eliminatorias, desde una ronda de 32 hasta la final en el MetLife Stadium. Cada hueco muestra a su ocupante más probable.",
    "br.r32": "Ronda de 32",
    "br.r16": "Octavos",
    "br.qf": "Cuartos",
    "br.sf": "Semifinales",
    "br.final": "Final",
    "br.winner": "1.º",
    "br.runner": "2.º",
    "br.third": "3.º",
    "br.group": "Grupo",
    "br.toReachFinal": "de llegar a la final",

    "mt.title": "Cómo funciona",
    "mt.subtitle": "Un motor de pronóstico de verdad, no un generador de cuadros.",
    "mt.p1.t": "Fuerza de equipo",
    "mt.p1.b":
      "Un modelo Dixon-Coles (Poisson bivariante) ponderado en el tiempo estima el ataque y la defensa de cada selección a partir de resultados recientes, combinado con un Elo internacional. Los partidos recientes pesan más.",
    "mt.p2.t": "Cada marcador",
    "mt.p2.b":
      "Para cualquier cruce, el modelo devuelve una distribución completa de marcadores — no solo quién gana, sino por cuánto — incluyendo la corrección Dixon-Coles y la ventaja de local.",
    "mt.p3.t": "50.000 torneos",
    "mt.p3.b":
      "Jugamos el torneo entero decenas de miles de veces: partidos reales de grupo, desempates FIFA, los ocho mejores terceros y el cuadro oficial de la ronda de 32, hasta el campeón.",
    "mt.p4.t": "Probabilidades honestas",
    "mt.p4.b":
      "Agregar millones de partidos simulados produce probabilidades calibradas para cada fase. El motor es de código abierto y se actualiza con los resultados reales.",
    "mt.stat.matches": "Partidos históricos",
    "mt.stat.params": "Modelo",
    "mt.stat.params.v": "Dixon-Coles × Elo",
    "mt.stat.sims": "Simulaciones",
    "mt.stat.engine": "Motor",

    "ft.built": "Creado por Juan Morales",
    "ft.tagline":
      "Un proyecto de portfolio de ciencia de datos, de código abierto. Los pronósticos son probabilísticos — las sorpresas son parte del juego.",
    "ft.generated": "Generado",
    "common.champion": "Campeón",
    "common.favourite": "Favorito",
  },
} as const;

export type DictKey = keyof (typeof dict)["en"];

interface LangContext {
  lang: Lang;
  setLang: (l: Lang) => void;
  toggle: () => void;
  t: (k: DictKey) => string;
}

const Ctx = createContext<LangContext>({
  lang: "en",
  setLang: () => {},
  toggle: () => {},
  t: (k) => dict.en[k],
});

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [lang, setLang] = useState<Lang>("en");

  useEffect(() => {
    const saved = localStorage.getItem("montecast-lang");
    if (saved === "es" || saved === "en") setLang(saved);
  }, []);

  useEffect(() => {
    document.documentElement.lang = lang;
    localStorage.setItem("montecast-lang", lang);
  }, [lang]);

  const t = (k: DictKey) => dict[lang][k] ?? dict.en[k] ?? k;
  const toggle = () => setLang((l) => (l === "en" ? "es" : "en"));

  return (
    <Ctx.Provider value={{ lang, setLang, toggle, t }}>{children}</Ctx.Provider>
  );
}

export const useLang = () => useContext(Ctx);
