import { type FormEvent, useState } from 'react';
import { useNavigate, Link } from '@tanstack/react-router';
import { ShieldCheck, Mail, Lock, Loader2, Shield, Eye, Terminal } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { toast } from 'sonner';
import { cn } from '../utils/cn';
import type { UserRole } from '../api/types';

const ROLE_INFO: { value: UserRole; label: string; description: string; icon: typeof Shield }[] = [
  { value: 'admin', label: 'Administrator', description: 'Full access including user management', icon: Shield },
  { value: 'analyst', label: 'Security Analyst', description: 'Threat detection and alert management', icon: Terminal },
  { value: 'viewer', label: 'Viewer', description: 'Read-only dashboards and alerts', icon: Eye },
];

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [selectedRole, setSelectedRole] = useState<UserRole>('analyst');
  const [submitting, setSubmitting] = useState(false);
  const { login } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await login(email, password);
      toast.success('Welcome to Q-Sentinel');
      navigate({ to: '/dashboard' });
    } catch (err: unknown) {
      const message = (err as { message?: string })?.message || 'Invalid email or password';
      toast.error(message);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center soc-grid px-4">
      <div className="w-full max-w-md space-y-6">
        <div className="flex flex-col items-center gap-3">
          <ShieldCheck className="h-12 w-12 text-cyber-400 text-glow" />
          <h1 className="font-display text-2xl font-bold text-navy-50">Q-Sentinel</h1>
          <p className="text-sm text-navy-400">AI-Powered Zero-Day Cyber Defense</p>
        </div>

        <form onSubmit={handleSubmit} className="glass-panel space-y-4 p-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-navy-200">Your Role</label>
            <div className="grid grid-cols-3 gap-2">
              {ROLE_INFO.map((option) => {
                const Icon = option.icon;
                const selected = selectedRole === option.value;
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setSelectedRole(option.value)}
                    className={cn(
                      'flex flex-col items-center gap-1.5 rounded-lg border p-3 transition-all',
                      selected
                        ? 'border-cyber-400/60 bg-cyber-400/10'
                        : 'border-navy-700 bg-navy-800/30 hover:border-navy-600'
                    )}
                  >
                    <Icon className={cn('h-5 w-5', selected ? 'text-cyber-400' : 'text-navy-400')} />
                    <span className={cn('text-xs font-medium text-center', selected ? 'text-cyber-300' : 'text-navy-200')}>
                      {option.label}
                    </span>
                  </button>
                );
              })}
            </div>
            <p className="text-xs text-navy-400">
              {ROLE_INFO.find((r) => r.value === selectedRole)?.description}
            </p>
          </div>

          <div className="space-y-1.5">
            <label htmlFor="email" className="text-sm font-medium text-navy-200">Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-navy-400" />
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-field pl-10"
                placeholder="analyst@example.com"
                autoComplete="email"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label htmlFor="password" className="text-sm font-medium text-navy-200">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-navy-400" />
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-field pl-10"
                placeholder="Enter your password"
                autoComplete="current-password"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="btn-primary w-full"
          >
            {submitting ? <Loader2 className="mx-auto h-4 w-4 animate-spin" /> : 'Sign In'}
          </button>

          <div className="flex items-center justify-between text-sm">
            <Link to="/forgot-password" className="text-cyber-400 hover:text-cyber-300 transition-colors">
              Forgot password?
            </Link>
            <Link to="/register" className="text-navy-300 hover:text-navy-100 transition-colors">
              Create account
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
}
