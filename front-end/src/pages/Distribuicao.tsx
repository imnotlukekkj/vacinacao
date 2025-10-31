import { useEffect, useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FilterBar } from "@/components/FilterBar";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from "recharts";
import { getTimeseries, getRankingUfs } from "@/lib/api";
import { Filters, TimePoint, RankingUf } from "@/types";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";

export function Distribuicao() {
  const [filters, setFilters] = useState<Filters>({});
  const [timeseries, setTimeseries] = useState<TimePoint[]>([]);
  const [ranking, setRanking] = useState<RankingUf[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        setLoading(true);
        setError(null);
        const [ts, rk] = await Promise.all([
          getTimeseries(filters),
          getRankingUfs(filters),
        ]);
        if (!cancelled) {
          setTimeseries(ts);
          setRanking(rk);
        }
      } catch (e: any) {
        if (!cancelled) setError(e?.message ?? 'Erro ao carregar dados');
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [filters]);

  const totalDistribuidas = ranking.reduce((sum, state) => sum + state.distribuídas, 0);
  const totalAplicadas = ranking.reduce((sum, state) => sum + state.aplicadas, 0);
  const taxaUtilizacao = totalDistribuidas ? ((totalAplicadas / totalDistribuidas) * 100).toFixed(1) : '0.0';

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Distribuição de Doses</h1>
        <p className="text-muted-foreground">
          Análise da distribuição de vacinas por região, período e fabricante
        </p>
      </div>

      <FilterBar />

      <div className="grid md:grid-cols-2 gap-6">
        <Card className="shadow-lg border-0">
          <CardHeader>
            <CardTitle className="text-foreground">Total de Doses Distribuídas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-4xl font-bold text-primary">
              {(totalDistribuidas / 1000000).toFixed(1)}M
            </div>
            <p className="text-sm text-muted-foreground mt-2">
              Taxa de utilização: {taxaUtilizacao}%
            </p>
          </CardContent>
        </Card>

        <Card className="shadow-lg border-0">
          <CardHeader>
            <CardTitle className="text-foreground">Evolução Mensal</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={200}>
              <LineChart data={timeseries.map(t => ({ month: `${t.ano}-${String(t.mês).padStart(2,'0')}`, distribuidas: t.distribuídas }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Line 
                  type="monotone" 
                  dataKey="distribuidas" 
                  stroke="hsl(var(--chart-2))" 
                  strokeWidth={2}
                  name="Distribuídas"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card className="shadow-lg border-0">
        <CardHeader>
          <CardTitle className="text-foreground">Distribuição por Estado</CardTitle>
        </CardHeader>
        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Estado</TableHead>
                <TableHead className="text-right">Distribuídas</TableHead>
                <TableHead className="text-right">Aplicadas</TableHead>
                <TableHead className="text-right">Taxa de Uso</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {ranking.map((state) => (
                <TableRow key={state.uf}>
                  <TableCell className="font-medium">{state.nome}</TableCell>
                  <TableCell className="text-right">{(state.distribuídas / 1000000).toFixed(2)}M</TableCell>
                  <TableCell className="text-right">{(state.aplicadas / 1000000).toFixed(2)}M</TableCell>
                  <TableCell className="text-right">{state.eficiência.toFixed(1)}%</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
      {/* Gráfico por fabricante removido até existir endpoint específico */}
    </div>
  );
}
