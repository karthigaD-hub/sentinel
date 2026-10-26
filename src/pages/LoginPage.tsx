import { type FormEvent, useState } from 'react';
import { useNavigate, Link } from '@tanstack/react-router';
import { ShieldCheck, Mail, Lock, Loader2 } from 'lucide-react';
import { useAuthStore } from '../store/authStore';
import { toast } from 'sonner';

export function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
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
                placeholder="you@example.com"
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
