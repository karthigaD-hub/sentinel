import { apiClient } from './client';
import type { RAGSearchResponse, RAGQueryResponse, RAGStatus, RAGIngestRequest, ThreatIntelStatus, ThreatIntelItem } from './types';

export const ragApi = {
  status: () =>
    apiClient.get<RAGStatus>('/api/v1/rag/status').then((r) => r.data),

  search: (data: { query: string; top_k?: number }) =>
    apiClient.post<RAGSearchResponse>('/api/v1/rag/search', data).then((r) => r.data),

  query: (data: { query: string; top_k?: number }) =>
    apiClient.post<RAGQueryResponse>('/api/v1/rag/query', data).then((r) => r.data),

  ingest: (data: RAGIngestRequest) =>
    apiClient.post<{ ingested: boolean; chunks_created: number; document_id: string }>('/api/v1/rag/ingest', data).then((r) => r.data),
};

export const threatIntelApi = {
  status: () =>
    apiClient.get<ThreatIntelStatus>('/api/v1/threat-intel').then((r) => r.data),

  item: (referenceId: string) =>
    apiClient.get<ThreatIntelItem>(`/api/v1/threat-intel/${referenceId}`).then((r) => r.data),
};
