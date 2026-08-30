import { type FormEvent, useState } from 'react';
import { Link } from '@tanstack/react-router';
import { ShieldCheck, Mail, Loader2, ArrowLeft } from 'lucide-react';
import { authApi } from '../api/authApi';
import { toast } from 'sonner';

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await authApi.forgotPassword();
      toast.info('If email delivery were configured, a reset link would be sent.');
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
          <h1 className="font-display text-2xl font-bold text-navy-50">Reset Password</h1>
          <p className="text-sm text-navy-400">Enter your email to receive a reset link</p>
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
                placeholder="analyst@example.com"
              />
            </div>
          </div>

          <button type="submit" disabled={submitting} className="btn-primary w-full">
            {submitting ? <Loader2 className="mx-auto h-4 w-4 animate-spin" /> : 'Send Reset Link'}
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
