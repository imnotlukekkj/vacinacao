import { Overview } from "@/types";

export function Kpis({ data }: { data?: Overview }) {
  const k = data ?? { distribuidas: 0, aplicadas: 0, eficiencia: 0, esavi: 0 };
  const items = [
    { 
      label: "Doses Distribuídas", 
      // Usar a chave 'distribuidas' (sem acento) para total de doses
      value: `${(k.distribuidas / 1000000).toFixed(1)}M`,
      subtitle: "Total acumulado",
      bgColor: "bg-blue-600",
      textColor: "text-white",
      icon: "📊"
    },
    { 
      label: "Doses Aplicadas", 
      value: `${(k.aplicadas / 1000000).toFixed(1)}M`,
      subtitle: "Total acumulado",
      bgColor: "bg-green-600",
      textColor: "text-white",
      icon: "📈"
    },
    { 
      label: "Eficiência", 
      value: `${k.eficiencia.toFixed(1)}%`,
      subtitle: "Aplicadas / Distribuídas",
      bgColor: "bg-orange-400",
      textColor: "text-white",
      icon: "📊"
    },
    // { 
//      label: "ESAVI", 
//      value: k.esavi.toLocaleString(),
//     subtitle: `${((k.esavi / k.aplicadas) * 100000).toFixed(2)} por 100k doses`,
//      bgColor: "bg-yellow-400",
//      textColor: "text-white",
//      icon: "⚠️"
//    },
  ];
  
  return (
    <div className="grid md:grid-cols-4 gap-4">
      {items.map(i => (
        <div key={i.label} className={`rounded-2xl ${i.bgColor} ${i.textColor} p-6 hover:shadow-lg transition-all duration-200`}>
          <div className="flex justify-between items-start mb-2">
            <div className="text-sm font-medium opacity-90">{i.label}</div>
            <div className="text-lg">{i.icon}</div>
          </div>
          <div className="text-3xl font-bold mb-1">{i.value}</div>
          <div className="text-sm opacity-80">{i.subtitle}</div>
        </div>
      ))}
    </div>
  );
}