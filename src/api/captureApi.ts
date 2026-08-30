import { apiClient } from './client';
import type { CaptureStatus, InterfaceInfo, CaptureStatistics, CapturePacketsResponse } from './types';

export const captureApi = {
  interfaces: () =>
    apiClient.get<InterfaceInfo[]>('/api/v1/capture/interfaces').then((r) => r.data),

  status: () =>
    apiClient.get<CaptureStatus>('/api/v1/capture/status').then((r) => r.data),

  start: (interface_: string) =>
    apiClient.post<{ status: string; interface: string }>(`/api/v1/capture/start?interface=${encodeURIComponent(interface_)}`).then((r) => r.data),

  stop: () =>
    apiClient.post<{ status: string }>('/api/v1/capture/stop').then((r) => r.data),

  statistics: () =>
    apiClient.get<CaptureStatistics>('/api/v1/capture/statistics').then((r) => r.data),

  packets: () =>
    apiClient.get<CapturePacketsResponse>('/api/v1/capture/packets').then((r) => r.data),
};
