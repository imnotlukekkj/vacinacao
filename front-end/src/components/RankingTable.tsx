import { RankingUf } from "@/types";

export function RankingTable({ data }: { data?: RankingUf[] }) {
  if (!data || !data.length) {
    return (
      <div className="rounded-2xl border p-4">
        <div className="text-sm text-gray-500">Sem dados disponíveis.</div>
      </div>
    );
  }

  const sortedData = data.slice().sort((a, b) => b.eficiência - a.eficiência);

  return (
    <div className="rounded-2xl border p-4">
      <h3 className="text-lg font-semibold mb-4">Ranking por Eficiência</h3>
      <div className="overflow-auto">
        <table className="min-w-full text-sm">
          <thead>
            <tr className="border-b">
              <th className="p-2 text-left">UF</th>
              <th className="p-2 text-right">Distribuídas</th>
              <th className="p-2 text-right">Aplicadas</th>
              <th className="p-2 text-right">Eficiência (%)</th>
            </tr>
          </thead>
          <tbody>
            {sortedData.map((row) => (
              <tr key={row.uf} className="border-t hover:bg-gray-50">
                <td className="p-2 font-medium">{row.nome}</td>
                <td className="p-2 text-right">{row.distribuídas.toLocaleString()}</td>
                <td className="p-2 text-right">{row.aplicadas.toLocaleString()}</td>
                <td className="p-2 text-right font-semibold">{row.eficiência.toFixed(2)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
