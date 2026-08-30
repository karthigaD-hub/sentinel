import { apiClient } from './client';
import type { QuantumStatus, QuantumKeygenResult, QuantumTestResult } from './types';

export const quantumApi = {
  status: () =>
    apiClient.get<QuantumStatus>('/api/v1/quantum/status').then((r) => r.data),

  keygen: () =>
    apiClient.post<QuantumKeygenResult>('/api/v1/quantum/keygen').then((r) => r.data),

  test: () =>
    apiClient.post<QuantumTestResult>('/api/v1/quantum/test').then((r) => r.data),
};
