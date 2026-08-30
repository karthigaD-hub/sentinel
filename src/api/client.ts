import axios, { type AxiosInstance, type InternalAxiosRequestConfig } from 'axios';
import { apiConfig } from './config';
import { tokens } from './tokens';

let isRefreshing = false;
let refreshPromise: Promise<string | null> | null = null;

async function doRefresh(): Promise<string | null> {
  const refreshToken = tokens.getRefreshToken();
  if (!refreshToken) return null;
  try {
    const res = await axios.post(`${apiConfig.baseURL}/api/v1/auth/refresh`, refreshToken, {
      headers: { 'Content-Type': 'text/plain' },
      timeout: apiConfig.timeout,
    });
    const { access_token, refresh_token } = res.data;
    tokens.setTokens(access_token, refresh_token);
    return access_token;
  } catch {
    tokens.clearTokens();
    return null;
  }
}

export const apiClient: AxiosInstance = axios.create({
  baseURL: apiConfig.baseURL,
  timeout: apiConfig.timeout,
  headers: { 'Content-Type': 'application/json' },
});

apiClient.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = tokens.getAccessToken();
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.code === 'ECONNABORTED' || !error.response) {
      return Promise.reject({
        type: 'network',
        message: 'Backend unavailable. Check your connection.',
        status: 0,
      });
    }

    const status = error.response.status;

    if (status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      if (!isRefreshing) {
        isRefreshing = true;
        refreshPromise = doRefresh().finally(() => {
          isRefreshing = false;
        });
      }
      const newToken = await refreshPromise;
      if (newToken) {
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return apiClient(originalRequest);
      }
      tokens.clearTokens();
      window.location.href = '/login';
      return Promise.reject({ type: 'auth', message: 'Session expired. Please log in again.', status: 401 });
    }

    const message =
      error.response?.data?.detail ||
      error.response?.data?.message ||
      (status === 403 ? 'You do not have permission to perform this action.' :
       status === 422 ? 'The request data was invalid.' :
       status === 429 ? 'Too many requests. Please slow down.' :
       status >= 500 ? 'The server encountered an error. Try again later.' :
       error.message);

    return Promise.reject({ type: 'http', message, status });
  }
);
