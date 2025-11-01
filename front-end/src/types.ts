// Tipos para os dados da API de vacinação

export interface Filters {
  ano?: number;
  mes?: number;
  uf?: string;
  fabricante?: string;
}

export interface Overview {
  distribuidas: number;
  aplicadas: number;
  eficiencia: number; // percentual
  esavi: number;
}

export interface TimePoint {
  ano: number;
  mês: number;
  uf: string;
  distribuídas: number;
  aplicadas: number;
  eficiência: number;
  esavi: number;
}

export interface RankingUf {
  uf: string;
  nome: string;
  distribuídas: number;
  aplicadas: number;
  eficiência: number;
}

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

// Estados do componente
export type LoadingState = 'idle' | 'loading' | 'success' | 'error';

export interface ComponentState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
}

