import { type FormEvent, useState } from 'react';
import { useNavigate, Link } from '@tanstack/react-router';
import { ShieldCheck, Mail, Lock, User, Loader2, Shield, Eye, Terminal } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { toast } from 'sonner';
import { cn } from '../utils/cn';
import type { UserRole } from '../api/types';

const ROLE_OPTIONS: { value: UserRole; label: string; description: string; icon: typeof Shield }[] = [
  { value: 'admin', label: 'Administrator', description: 'Full system access, user management, all operations', icon: Shield },
  { value: 'analyst', label: 'Security Analyst', description: 'Threat detection, packet capture, alert management', icon: Terminal },
  { value: 'viewer', label: 'Viewer', description: 'Read-only access to dashboards and alerts', icon: Eye },
];

export function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState<UserRole>('viewer');
  const [submitting, setSubmitting] = useState(false);
  const { register } = useAuthStore();
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await register(email, password, fullName, role);
      toast.success('Account created successfully');
      navigate({ to: '/dashboard' });
    } catch (err: unknown) {
      const message = (err as { message?: string })?.message || 'Registration failed';
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
          <h1 className="font-display text-2xl font-bold text-navy-50">Create Account</h1>
          <p className="text-sm text-navy-400">Choose your role and register</p>
        </div>

        <form onSubmit={handleSubmit} className="glass-panel space-y-4 p-6">
          <div className="space-y-1.5">
            <label htmlFor="fullName" className="text-sm font-medium text-navy-200">Full Name</label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-navy-400" />
              <input
                id="fullName"
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="input-field pl-10"
                placeholder="Jane Analyst"
              />
            </div>
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
                minLength={12}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-field pl-10"
                placeholder="At least 12 characters"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-navy-200">Select Your Role</label>
            <div className="space-y-2">
              {ROLE_OPTIONS.map((option) => {
                const Icon = option.icon;
                const selected = role === option.value;
                return (
                  <button
                    key={option.value}
                    type="button"
                    onClick={() => setRole(option.value)}
                    className={cn(
                      'flex w-full items-start gap-3 rounded-lg border p-3 text-left transition-all',
                      selected
                        ? 'border-cyber-400/60 bg-cyber-400/10'
                        : 'border-navy-700 bg-navy-800/30 hover:border-navy-600'
                    )}
                  >
                    <Icon className={cn('mt-0.5 h-5 w-5 shrink-0', selected ? 'text-cyber-400' : 'text-navy-400')} />
                    <div className="flex-1">
                      <p className={cn('text-sm font-medium', selected ? 'text-cyber-300' : 'text-navy-100')}>
                        {option.label}
                      </p>
                      <p className="text-xs text-navy-400">{option.description}</p>
                    </div>
                    {selected && (
                      <ShieldCheck className="h-4 w-4 shrink-0 text-cyber-400" />
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          <button type="submit" disabled={submitting} className="btn-primary w-full">
            {submitting ? <Loader2 className="mx-auto h-4 w-4 animate-spin" /> : 'Create Account'}
          </button>

          <Link to="/login" className="block text-center text-sm text-cyber-400 hover:text-cyber-300 transition-colors">
            Already have an account? Sign in
          </Link>
        </form>
      </div>
    </div>
  );
}
