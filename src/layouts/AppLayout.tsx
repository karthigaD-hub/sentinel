import { type ReactNode, useEffect } from 'react';
import { Link, Outlet, useNavigate, useRouterState } from '@tanstack/react-router';
import {
  LayoutDashboard, Radio, ShieldAlert, BrainCircuit, BookOpen,
  Bot, BellRing, FileText, Atom, Settings, Info, LogOut,
  ShieldCheck, Wifi, WifiOff, Loader2,
} from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { useWsStore } from '../store/wsStore';
import { useWebSocket } from '../hooks/useWebSocket';
import { cn } from '../utils/cn';

const NAV_ITEMS = [
  { label: 'Dashboard', to: '/dashboard', icon: LayoutDashboard, permission: 'dashboard:view' },
  { label: 'Packet Monitoring', to: '/packets', icon: Radio, permission: 'capture:view' },
  { label: 'Threat Detection', to: '/detection', icon: ShieldAlert, permission: 'detection:view' },
  { label: 'Explainable AI', to: '/explainable-ai', icon: BrainCircuit, permission: 'detection:view' },
  { label: 'Threat Intelligence', to: '/threat-intel', icon: BookOpen, permission: 'threatintel:view' },
  { label: 'AI Security Assistant', to: '/assistant', icon: Bot, permission: 'assistant:use' },
  { label: 'Alert Management', to: '/alerts', icon: BellRing, permission: 'alerts:view' },
  { label: 'Reports', to: '/reports', icon: FileText, permission: 'reports:view' },
  { label: 'Quantum Security', to: '/quantum', icon: Atom, permission: 'quantum:view' },
  { label: 'Settings', to: '/settings', icon: Settings, permission: 'settings:view' },
  { label: 'About', to: '/about', icon: Info, permission: null },
];

function WsStatusBadge() {
  const { connectionState } = useWsStore();
  const config = {
    connected: { icon: Wifi, label: 'CONNECTED', color: 'text-success-400' },
    reconnecting: { icon: Loader2, label: 'RECONNECTING', color: 'text-warning-500', spin: true },
    disconnected: { icon: WifiOff, label: 'DISCONNECTED', color: 'text-danger-400' },
  }[connectionState];
  const Icon = config.icon;
  return (
    <span className={cn('flex items-center gap-1.5 text-xs font-mono', config.color)}>
      <Icon className={cn('h-3.5 w-3.5', config.spin && 'animate-spin')} />
      {config.label}
    </span>
  );
}

function Sidebar() {
  const { hasPermission } = useAuthStore();
  const pathname = useRouterState({ select: (s) => s.location.pathname });

  return (
    <aside className="fixed left-0 top-0 z-30 flex h-screen w-64 flex-col border-r border-navy-700/60 bg-navy-950/80 backdrop-blur-xl">
      <div className="flex h-16 items-center gap-2.5 border-b border-navy-700/60 px-5">
        <ShieldCheck className="h-7 w-7 text-cyber-400" />
        <span className="font-display text-lg font-bold text-navy-50">Q-Sentinel</span>
      </div>
      <nav className="flex-1 overflow-y-auto px-3 py-4">
        <ul className="space-y-1">
          {NAV_ITEMS.map((item) => {
            if (item.permission && !hasPermission(item.permission)) return null;
            const Icon = item.icon;
            const active = pathname === item.to || pathname.startsWith(item.to + '/');
            return (
              <li key={item.to}>
                <Link
                  to={item.to}
                  className={cn('nav-link', active && 'nav-link-active')}
                >
                  <Icon className="h-4.5 w-4.5 shrink-0" />
                  <span className="text-sm font-medium">{item.label}</span>
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>
      <div className="border-t border-navy-700/60 px-4 py-3">
        <WsStatusBadge />
      </div>
    </aside>
  );
}

function Header() {
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate({ to: '/login' });
  };

  return (
    <header className="sticky top-0 z-20 flex h-16 items-center justify-between border-b border-navy-700/60 bg-navy-950/80 px-6 backdrop-blur-xl">
      <div className="flex items-center gap-2 text-sm text-navy-400">
        <ShieldCheck className="h-4 w-4 text-cyber-400" />
        <span className="font-mono">AI-Powered Zero-Day Cyber Defense</span>
      </div>
      <div className="flex items-center gap-4">
        <div className="text-right">
          <p className="text-sm font-medium text-navy-100">{user?.full_name || user?.email}</p>
          <p className="text-xs font-mono text-navy-400 uppercase">{user?.role}</p>
        </div>
        <button
          onClick={handleLogout}
          className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-navy-300 transition-colors hover:bg-navy-800/50 hover:text-danger-400"
          aria-label="Log out"
        >
          <LogOut className="h-4 w-4" />
          <span className="hidden sm:inline">Logout</span>
        </button>
      </div>
    </header>
  );
}

export function AppLayout({ children }: { children?: ReactNode }) {
  useWebSocket();
  const { fetchUser, isAuthenticated, isLoading } = useAuthStore();

  useEffect(() => {
    if (isAuthenticated && !isLoading) {
      fetchUser();
    }
  }, []);

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen soc-grid">
      <Sidebar />
      <div className="ml-64 flex min-h-screen flex-col">
        <Header />
        <main className="flex-1 p-6">
          {children || <Outlet />}
        </main>
      </div>
    </div>
  );
}
