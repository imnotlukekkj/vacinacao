import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { TimePoint } from "@/types";

export function TimeSeries({ data = [] }: { data?: TimePoint[] }) {
  if (!data || !data.length) {
    return (
      <div className="w-full h-80 rounded-2xl border p-4 flex items-center justify-center">
        <div className="text-sm text-gray-500">Sem dados disponíveis.</div>
      </div>
    );
  }

  const rows = data.map((d) => ({
    label: `${d.ano}-${String(d.mês).padStart(2, "0")}`,
    distribuida: d.distribuídas ?? 0,
    aplicada: d.aplicadas ?? 0,
  }));

  return (
    <div className="w-full h-80 rounded-2xl border p-4">
      <h3 className="text-lg font-semibold mb-4">Evolução Mensal (2021)</h3>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={rows}>
          <XAxis dataKey="label" />
          <YAxis />
          <Tooltip />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="distribuida" 
            name="Distribuídas" 
            stroke="#8884d8" 
            strokeWidth={2}
            dot={false} 
          />
          <Line 
            type="monotone" 
            dataKey="aplicada" 
            name="Aplicadas" 
            stroke="#82ca9d" 
            strokeWidth={2}
            dot={false} 
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}