import { create } from 'zustand';
import type { User, UserRole } from '../api/types';
import { tokens } from '../api/tokens';
import { authApi } from '../api/authApi';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string, role?: UserRole) => Promise<void>;
  logout: () => Promise<void>;
  fetchUser: () => Promise<void>;
  hasRole: (...roles: UserRole[]) => boolean;
  hasPermission: (permission: string) => boolean;
}

const ROLE_PERMISSIONS: Record<UserRole, string[]> = {
  admin: [
    'dashboard:view', 'capture:view', 'capture:start', 'capture:stop',
    'detection:view', 'alerts:view', 'alerts:update', 'threatintel:view',
    'assistant:use', 'reports:view', 'quantum:view', 'settings:view', 'settings:update', 'admin:manage',
  ],
  analyst: [
    'dashboard:view', 'capture:view', 'capture:start', 'capture:stop',
    'detection:view', 'alerts:view', 'alerts:update', 'threatintel:view',
    'assistant:use', 'reports:view', 'quantum:view', 'settings:view',
  ],
  viewer: [
    'dashboard:view', 'alerts:view', 'detection:view', 'threatintel:view',
    'reports:view', 'quantum:view', 'settings:view',
  ],
};

export const useAuthStore = create<AuthState>((set, get) => ({
  user: null,
  isAuthenticated: !!tokens.getAccessToken(),
  isLoading: false,

  login: async (email, password) => {
    const tokenResponse = await authApi.login({ email, password });
    tokens.setTokens(tokenResponse.access_token, tokenResponse.refresh_token);
    const user = await authApi.me();
    set({ user, isAuthenticated: true });
  },

  register: async (email, password, fullName, role) => {
    await authApi.register({ email, password, full_name: fullName, role });
    await get().login(email, password);
  },

  logout: async () => {
    try {
      await authApi.logout();
    } catch {
      // ignore — clearing local state is what matters
    }
    tokens.clearTokens();
    set({ user: null, isAuthenticated: false });
  },

  fetchUser: async () => {
    if (!tokens.getAccessToken()) {
      set({ user: null, isAuthenticated: false });
      return;
    }
    try {
      const user = await authApi.me();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      tokens.clearTokens();
      set({ user: null, isAuthenticated: false, isLoading: false });
    }
  },

  hasRole: (...roles: UserRole[]) => {
    const { user } = get();
    return !!user && roles.includes(user.role);
  },

  hasPermission: (permission: string) => {
    const { user } = get();
    if (!user) return false;
    return ROLE_PERMISSIONS[user.role]?.includes(permission) ?? false;
  },
}));
