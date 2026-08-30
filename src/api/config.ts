const baseURL = import.meta.env.VITE_API_BASE_URL || '';

export const apiConfig = {
  baseURL,
  timeout: 30000,
  wsBaseURL: baseURL.replace(/^http/, 'ws'),
};

export function buildWsUrl(token: string): string {
  const wsBase = apiConfig.wsBaseURL || window.location.origin.replace(/^http/, 'ws');
  const base = wsBase.replace(/\/$/, '');
  return `${base}/api/v1/ws?token=${encodeURIComponent(token)}`;
}
