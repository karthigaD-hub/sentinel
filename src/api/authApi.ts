import { apiClient } from './client';
import type { LoginRequest, TokenResponse, UserCreate, User, MessageResponse } from './types';

export const authApi = {
  register: (data: UserCreate) =>
    apiClient.post<User>('/api/v1/auth/register', data).then((r) => r.data),

  login: (data: LoginRequest) =>
    apiClient.post<TokenResponse>('/api/v1/auth/login', data).then((r) => r.data),

  refresh: (refreshToken: string) =>
    apiClient.post<TokenResponse>('/api/v1/auth/refresh', refreshToken, {
      headers: { 'Content-Type': 'text/plain' },
    }).then((r) => r.data),

  logout: () =>
    apiClient.post<MessageResponse>('/api/v1/auth/logout').then((r) => r.data),

  me: () =>
    apiClient.get<User>('/api/v1/auth/me').then((r) => r.data),

  forgotPassword: () =>
    apiClient.post<MessageResponse>('/api/v1/auth/forgot-password').then((r) => r.data),

  resetPassword: () =>
    apiClient.post<MessageResponse>('/api/v1/auth/reset-password').then((r) => r.data),
};
