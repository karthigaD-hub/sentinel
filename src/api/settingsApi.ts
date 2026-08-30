import { apiClient } from './client';
import type { SystemStatus } from './types';

export const settingsApi = {
  systemStatus: () =>
    apiClient.get<SystemStatus>('/api/v1/system/status').then((r) => r.data),
};
