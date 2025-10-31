import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export function Sobre() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground mb-2">Sobre o Painel</h1>
        <p className="text-muted-foreground">
          Metodologia e fontes de dados
        </p>
      </div>

      <Card className="shadow-lg border-0">
        <CardHeader>
          <CardTitle className="text-foreground">Sobre o Projeto</CardTitle>
        </CardHeader>
        <CardContent className="prose prose-slate dark:prose-invert max-w-none">
          <p>
            O <strong>Painel Vacinação Brasil (2020–2024)</strong> é uma ferramenta interativa
            para análise de dados consolidados sobre a campanha de vacinação contra COVID-19
            no território brasileiro.
          </p>

          <h3 className="text-foreground mt-6 mb-3">Bases de Dados</h3>
          <ul className="space-y-2">
            <li>
              <strong>Distribuição de doses:</strong> Quantitativo de doses distribuídas por ano,
              mês, UF, município e fabricante
            </li>
            <li>
              <strong>Aplicação de doses:</strong> Dados de doses aplicadas segmentados por
              características demográficas e tipo de dose
            </li>
            <li>
              <strong>ESAVI:</strong> Eventos adversos pós-vacinação, classificados por gravidade
              e características do paciente
            </li>
          </ul>

          <h3 className="text-foreground mt-6 mb-3">Métricas Calculadas</h3>
          <ul className="space-y-2">
            <li>
              <strong>Eficiência:</strong> Percentual de doses aplicadas em relação às distribuídas
              <code className="ml-2 text-sm">Eficiência (%) = (Aplicadas ÷ Distribuídas) × 100</code>
            </li>
            <li>
              <strong>Taxa de ESAVI:</strong> Eventos adversos por 100 mil doses aplicadas
              <code className="ml-2 text-sm">Taxa = (ESAVI ÷ Aplicadas) × 100.000</code>
            </li>
          </ul>

          <h3 className="text-foreground mt-6 mb-3">Fontes</h3>
          <p>
            Os dados utilizados neste painel são consolidados a partir de bases oficiais do
            Ministério da Saúde, DATASUS e sistemas estaduais de informação em saúde.
          </p>

          <h3 className="text-foreground mt-6 mb-3">Limitações</h3>
          <p>
            A qualidade dos dados pode apresentar variações entre estados e municípios devido
            a diferenças nos sistemas de registro e atualização das informações. Indicadores
            de completude estão disponíveis na seção "Qualidade dos Dados".
          </p>
        </CardContent>
      </Card>

      <Card className="shadow-lg border-0 bg-gradient-card">
        <CardContent className="py-6">
          <p className="text-center text-muted-foreground">
            <strong>Desenvolvido com:</strong> React, TypeScript, Tailwind CSS, Recharts e Shadcn UI
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
