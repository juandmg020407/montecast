import { loadData } from "@/lib/data";
import { DotField } from "@/components/ui";
import { Nav } from "@/components/Nav";
import { Hero } from "@/components/Hero";
import { Favourites } from "@/components/Favourites";

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
        </main>
      </div>
    </>
  );
}
