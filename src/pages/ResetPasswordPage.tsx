import { type FormEvent, useState } from 'react';
import { Link } from '@tanstack/react-router';
import { ShieldCheck, Lock, Loader2, ArrowLeft } from 'lucide-react';
import { authApi } from '../api/authApi';
import { toast } from 'sonner';

export function ResetPasswordPage() {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }
    if (password.length < 12) {
      toast.error('Password must be at least 12 characters');
      return;
    }
    setSubmitting(true);
    try {
      await authApi.resetPassword();
      toast.info('Password reset is not configured in this environment.');
    } catch (err: unknown) {
      const message = (err as { message?: string })?.message || 'Password reset is not configured';
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
          <h1 className="font-display text-2xl font-bold text-navy-50">Set New Password</h1>
        </div>

        <form onSubmit={handleSubmit} className="glass-panel space-y-4 p-6">
          <div className="space-y-1.5">
            <label htmlFor="password" className="text-sm font-medium text-navy-200">New Password</label>
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

          <div className="space-y-1.5">
            <label htmlFor="confirm" className="text-sm font-medium text-navy-200">Confirm Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-navy-400" />
              <input
                id="confirm"
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="input-field pl-10"
                placeholder="Re-enter password"
              />
            </div>
          </div>

          <button type="submit" disabled={submitting} className="btn-primary w-full">
            {submitting ? <Loader2 className="mx-auto h-4 w-4 animate-spin" /> : 'Reset Password'}
          </button>

          <Link to="/login" className="flex items-center gap-1.5 text-sm text-navy-300 hover:text-navy-100 transition-colors">
            <ArrowLeft className="h-4 w-4" />
            Back to login
          </Link>
        </form>
      </div>
    </div>
  );
}
