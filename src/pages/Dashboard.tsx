import { useEffect, useState } from "react";
import { FilterBar } from "@/components/FilterBar";
import { Kpis } from "@/components/Kpis";
import { TimeSeries } from "@/components/TimeSeries";
import { RankingTable } from "@/components/RankingTable";
import { getOverview, getTimeseries, getRankingUfs } from "@/lib/api";
import { Overview, TimePoint, RankingUf, Filters } from "@/types";

export function Dashboard() {
  const [filters, setFilters] = useState<Filters>({});
  const [overview, setOverview] = useState<Overview | null>(null);
  const [timeseries, setTimeseries] = useState<TimePoint[]>([]);
  const [ranking, setRanking] = useState<RankingUf[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let isCancelled = false;
    async function load() {
      try {
        setLoading(true);
        setError(null);
        const [ov, ts, rk] = await Promise.all([
          getOverview(filters),
          getTimeseries(filters),
          getRankingUfs(filters),
        ]);
        if (!isCancelled) {
          setOverview(ov);
          setTimeseries(ts);
          setRanking(rk);
        }
      } catch (e: any) {
        if (!isCancelled) setError(e?.message ?? 'Erro ao carregar dados');
      } finally {
        if (!isCancelled) setLoading(false);
      }
    }
    load();
    return () => {
      isCancelled = true;
    };
  }, [filters]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Dashboard Geral</h1>
        <p className="text-muted-foreground">
          Panorama completo da vacinação contra COVID-19 no Brasil
        </p>
      </div>

      <FilterBar />

      {error && (
        <div className="text-sm text-red-600">{error}</div>
      )}

      <Kpis data={overview ?? undefined} />

      <TimeSeries data={timeseries} />

      <RankingTable data={ranking} />
    </div>
  );
}
