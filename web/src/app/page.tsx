import { loadData } from "@/lib/data";
import { DotField } from "@/components/ui";
import { Nav } from "@/components/Nav";
import { Hero } from "@/components/Hero";
import { Favourites } from "@/components/Favourites";
import { Groups } from "@/components/Groups";
import { Bracket } from "@/components/Bracket";
import { Method } from "@/components/Method";

export default function Home() {
  const data = loadData();
  const favourite = [...data.simulation.teams].sort(
    (a, b) => b.champion - a.champion,
  )[0];

  return (
    <>
      <DotField />
      <div className="relative z-10">
        <Nav />
        <main>
          <Hero meta={data.meta} top={favourite} />
          <Favourites teams={data.simulation.teams} />
          <Groups groups={data.groups} />
          <Bracket
            bracket={data.bracket}
            groups={data.groups}
            teams={data.simulation.teams}
            meta={data.meta}
          />
          <Method meta={data.meta} />
        </main>
      </div>
    </>
  );
}
