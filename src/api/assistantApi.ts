import { apiClient } from './client';
import type { ChatRequest, ChatResponse, AssistantHistoryItem } from './types';

export const assistantApi = {
  chat: (data: ChatRequest) =>
    apiClient.post<ChatResponse>('/api/v1/assistant/chat', data).then((r) => r.data),

  history: () =>
    apiClient.get<AssistantHistoryItem[]>('/api/v1/assistant/history').then((r) => r.data),
};
