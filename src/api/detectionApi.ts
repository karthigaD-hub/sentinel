import { apiClient } from './client';
import type { DetectionStatus, DetectionResultItem, DetectionStatistics, DetectionHistory, ModelStatus, ModelMetrics, PaginatedResponse } from './types';

export const detectionApi = {
  status: () =>
    apiClient.get<DetectionStatus>('/api/v1/detection/status').then((r) => r.data),

  start: (interface_: string) =>
    apiClient.post<{ status: string; interface: string }>(`/api/v1/detection/start?interface=${encodeURIComponent(interface_)}`).then((r) => r.data),

  stop: () =>
    apiClient.post<{ status: string }>('/api/v1/detection/stop').then((r) => r.data),

  results: (page = 1, pageSize = 50) =>
    apiClient.get<PaginatedResponse<DetectionResultItem>>(`/api/v1/detection/results?page=${page}&page_size=${pageSize}`).then((r) => r.data),

  statistics: () =>
    apiClient.get<DetectionStatistics>('/api/v1/detection/statistics').then((r) => r.data),

  history: (hours = 24) =>
    apiClient.get<DetectionHistory>(`/api/v1/detection/history?hours=${hours}`).then((r) => r.data),

  modelStatus: () =>
    apiClient.get<ModelStatus>('/api/v1/detection/model/status').then((r) => r.data),

  modelMetrics: () =>
    apiClient.get<ModelMetrics>('/api/v1/detection/model/metrics').then((r) => r.data),
};
