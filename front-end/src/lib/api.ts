import { Overview, TimePoint, RankingUf, Filters, ApiResponse } from '@/types';

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL ?? 'http://localhost:8001';

// Função auxiliar para fazer requisições HTTP
async function fetchApi<T>(endpoint: string, params?: Record<string, string | number | boolean | undefined>): Promise<T> {
  const url = new URL(`${API_BASE_URL}${endpoint}`);

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined && value !== null) {
        url.searchParams.append(key, String(value));
      }
    });
  }

  try {
    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const json = await response.json() as ApiResponse<T> | T;
    // Suporta tanto formato ApiResponse<T> quanto T direto
    if (typeof json === 'object' && json && 'success' in (json as any) && 'data' in (json as any)) {
      return (json as ApiResponse<T>).data;
    }
    return json as T;
  } catch (error) {
    console.error(`Erro ao buscar dados de ${endpoint}:`, error);
    throw error;
  }
}

// Buscar dados de overview (KPIs)
export async function getOverview(filters: Filters = {}): Promise<Overview> {
  const params: Record<string, string | number | boolean | undefined> = {};
  
  if (filters.ano) params.ano = filters.ano;
  if (filters.mes) params.mes = filters.mes;
  if (filters.uf) params.uf = filters.uf;
  if (filters.fabricante) params.fabricante = filters.fabricante;

  // Buscar dados brutos e normalizar chaves (aceitar tanto 'distribuídas' quanto 'distribuidas')
  const raw = await fetchApi<any>('/overview', params);

  // Normalizar nomes de campos do backend para o formato esperado pelo frontend
  const distribuidas = raw?.['distribuidas'] ?? raw?.['distribuídas'] ?? 0;
  const aplicadas = raw?.['aplicadas'] ?? 0;
  const eficiencia = raw?.['eficiencia'] ?? raw?.['eficiência'] ?? 0.0;
  const esavi = raw?.['esavi'] ?? 0;

  return {
    distribuidas: distribuidas,
    aplicadas: aplicadas,
    eficiencia: eficiencia,
    esavi: esavi,
  } as Overview;
}

// Buscar série temporal
export async function getTimeseries(filters: Filters = {}): Promise<TimePoint[]> {
  const params: Record<string, string | number | boolean | undefined> = {};
  
  if (filters.ano) params.ano = filters.ano;
  if (filters.mes) params.mes = filters.mes;
  if (filters.uf) params.uf = filters.uf;
  if (filters.fabricante) params.fabricante = filters.fabricante;

  return fetchApi<TimePoint[]>('/timeseries', params);
}

// Buscar ranking de UFs
export async function getRankingUfs(filters: Filters = {}): Promise<RankingUf[]> {
  const params: Record<string, string | number | boolean | undefined> = {};
  
  if (filters.ano) params.ano = filters.ano;
  if (filters.mes) params.mes = filters.mes;
  if (filters.uf) params.uf = filters.uf;
  if (filters.fabricante) params.fabricante = filters.fabricante;

  return fetchApi<RankingUf[]>('/ranking/ufs', params);
}

// Hook personalizado para gerenciar estado de carregamento
export function useApiState<T>() {
  return {
    data: null as T | null,
    loading: false,
    error: null as string | null,
  };
}

