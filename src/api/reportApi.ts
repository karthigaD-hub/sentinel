import { apiClient } from './client';
import type { PaginatedResponse } from './types';

export const reportApi = {
  list: () =>
    apiClient.get<PaginatedResponse>('/api/v1/reports').then((r) => r.data),

  generate: () =>
    apiClient.post('/api/v1/reports/generate').then((r) => r.data),
};
