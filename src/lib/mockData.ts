export const generateMonthlyData = () => {
  const months = ['Jan', 'Fev', 'Mar', 'Abr', 'Mai', 'Jun', 'Jul', 'Ago', 'Set', 'Out', 'Nov', 'Dez'];
  return months.map((month, idx) => ({
    month,
    distribuidas: Math.floor(15000000 + Math.random() * 5000000),
    aplicadas: Math.floor(12000000 + Math.random() * 4000000),
    esavi: Math.floor(1000 + Math.random() * 500),
  }));
};

export const generateStateData = () => {
  const states = [
    { uf: 'SP', nome: 'São Paulo', populacao: 46649132 },
    { uf: 'RJ', nome: 'Rio de Janeiro', populacao: 17463349 },
    { uf: 'MG', nome: 'Minas Gerais', populacao: 21411923 },
    { uf: 'BA', nome: 'Bahia', populacao: 14985284 },
    { uf: 'PR', nome: 'Paraná', populacao: 11597484 },
    { uf: 'RS', nome: 'Rio Grande do Sul', populacao: 11466630 },
    { uf: 'PE', nome: 'Pernambuco', populacao: 9674793 },
    { uf: 'CE', nome: 'Ceará', populacao: 9240580 },
    { uf: 'PA', nome: 'Pará', populacao: 8777124 },
    { uf: 'SC', nome: 'Santa Catarina', populacao: 7338473 },
  ];

  return states.map(state => {
    const distribuidas = Math.floor(state.populacao * (0.8 + Math.random() * 0.4));
    const aplicadas = Math.floor(distribuidas * (0.75 + Math.random() * 0.15));
    const eficiencia = ((aplicadas / distribuidas) * 100).toFixed(1);
    
    return {
      ...state,
      distribuidas,
      aplicadas,
      eficiencia: parseFloat(eficiencia),
    };
  }).sort((a, b) => b.eficiencia - a.eficiencia);
};

export const generateFabricanteData = () => {
  const fabricantes = [
    { nome: 'Pfizer/BioNTech', id: 'pfizer' },
    { nome: 'AstraZeneca', id: 'astrazeneca' },
    { nome: 'CoronaVac', id: 'coronavac' },
    { nome: 'Janssen', id: 'janssen' },
  ];

  return fabricantes.map(fab => {
    const distribuidas = Math.floor(30000000 + Math.random() * 20000000);
    const aplicadas = Math.floor(distribuidas * (0.75 + Math.random() * 0.15));
    const esavi = Math.floor(aplicadas * (0.0001 + Math.random() * 0.0001));
    const eficiencia = ((aplicadas / distribuidas) * 100).toFixed(1);
    
    return {
      ...fab,
      distribuidas,
      aplicadas,
      eficiencia: parseFloat(eficiencia),
      esavi,
      taxaEsavi: ((esavi / aplicadas) * 100000).toFixed(2),
    };
  });
};

export const generateEsaviData = () => {
  const tipos = [
    'Dor no local',
    'Febre',
    'Fadiga',
    'Cefaleia',
    'Mialgia',
    'Náusea',
    'Calafrios',
    'Reação alérgica',
  ];

  return tipos.map(tipo => ({
    tipo,
    total: Math.floor(1000 + Math.random() * 5000),
    leves: Math.floor(800 + Math.random() * 4000),
    graves: Math.floor(50 + Math.random() * 500),
  })).sort((a, b) => b.total - a.total);
};
