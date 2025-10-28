import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import { FilterBar } from "@/components/FilterBar";

export function Qualidade() {
  const qualityMetrics = [
    { campo: "Idade", completude: 94.2, status: "Boa" },
    { campo: "Sexo", completude: 96.8, status: "Excelente" },
    { campo: "Município", completude: 88.5, status: "Regular" },
    { campo: "Data de Vacinação", completude: 99.1, status: "Excelente" },
    { campo: "Lote da Vacina", completude: 92.3, status: "Boa" },
    { campo: "Fabricante", completude: 98.7, status: "Excelente" },
    { campo: "Dose", completude: 95.4, status: "Boa" },
    { campo: "Profissional", completude: 89.1, status: "Regular" },
  ];

  const overallQuality = qualityMetrics.reduce((acc, metric) => acc + metric.completude, 0) / qualityMetrics.length;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Qualidade dos Dados</h1>
        <p className="text-muted-foreground">
          Análise da completude e qualidade dos dados de vacinação
        </p>
      </div>

      <FilterBar />

      <div className="grid md:grid-cols-3 gap-6">
        <Card className="shadow-lg border-0">
          <CardHeader>
            <CardTitle className="text-foreground">Qualidade Geral</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="text-4xl font-bold text-foreground mb-2">
                {overallQuality.toFixed(1)}%
              </div>
              <Progress value={overallQuality} className="h-2" />
              <div className="text-sm text-muted-foreground mt-2">
                Completude média dos dados
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-lg border-0">
          <CardHeader>
            <CardTitle className="text-foreground">Campos Excelentes</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="text-4xl font-bold text-green-600 mb-2">
                {qualityMetrics.filter(m => m.status === "Excelente").length}
              </div>
              <div className="text-sm text-muted-foreground">
                Campos com completude ≥ 95%
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-lg border-0">
          <CardHeader>
            <CardTitle className="text-foreground">Campos Críticos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-center">
              <div className="text-4xl font-bold text-red-600 mb-2">
                {qualityMetrics.filter(m => m.status === "Regular").length}
              </div>
              <div className="text-sm text-muted-foreground">
                Campos com completude &lt; 90%
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card className="shadow-lg border-0">
        <CardHeader>
          <CardTitle className="text-foreground">Detalhamento por Campo</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {qualityMetrics.map((metric) => (
              <div key={metric.campo} className="p-4 bg-muted/30 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <div className="font-medium">{metric.campo}</div>
                  <div className={`px-2 py-1 rounded text-xs font-medium ${
                    metric.status === "Excelente" 
                      ? "bg-green-100 text-green-800" 
                      : metric.status === "Boa"
                      ? "bg-blue-100 text-blue-800"
                      : "bg-red-100 text-red-800"
                  }`}>
                    {metric.status}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <Progress value={metric.completude} className="flex-1 h-2" />
                  <div className="text-sm font-medium text-foreground">
                    {metric.completude.toFixed(1)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
