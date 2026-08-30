import { apiClient } from './client';
import type { HealthStatus, SystemStatus, DetectionStatus, DetectionStatistics, ModelStatus, ModelMetrics } from './types';

export const dashboardApi = {
  health: () =>
    apiClient.get<HealthStatus>('/health').then((r) => r.data),

  systemStatus: () =>
    apiClient.get<SystemStatus>('/api/v1/system/status').then((r) => r.data),

  detectionStatus: () =>
    apiClient.get<DetectionStatus>('/api/v1/detection/status').then((r) => r.data),

  detectionStatistics: () =>
    apiClient.get<DetectionStatistics>('/api/v1/detection/statistics').then((r) => r.data),

  modelStatus: () =>
    apiClient.get<ModelStatus>('/api/v1/detection/model/status').then((r) => r.data),

  modelMetrics: () =>
    apiClient.get<ModelMetrics>('/api/v1/detection/model/metrics').then((r) => r.data),
};
