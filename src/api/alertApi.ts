import { apiClient } from './client';
import type { AlertRead, PaginatedResponse } from './types';

export const alertApi = {
  list: (page = 1, pageSize = 50) =>
    apiClient.get<PaginatedResponse<AlertRead>>(`/api/v1/alerts?page=${page}&page_size=${pageSize}`).then((r) => r.data),

  get: (alertId: string) =>
    apiClient.get<AlertRead>(`/api/v1/alerts/${alertId}`).then((r) => r.data),

  acknowledge: (alertId: string) =>
    apiClient.post<AlertRead>(`/api/v1/alerts/${alertId}/acknowledge`).then((r) => r.data),

  resolve: (alertId: string) =>
    apiClient.post<AlertRead>(`/api/v1/alerts/${alertId}/resolve`).then((r) => r.data),

  reopen: (alertId: string) =>
    apiClient.post<AlertRead>(`/api/v1/alerts/${alertId}/reopen`).then((r) => r.data),
};
