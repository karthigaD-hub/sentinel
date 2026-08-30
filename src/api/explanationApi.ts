import { apiClient } from './client';
import type { ExplanationResponse } from './types';

export const explanationApi = {
  get: (detectionId: string) =>
    apiClient.get<ExplanationResponse>(`/api/v1/detection/${detectionId}/explanation`).then((r) => r.data),
};
