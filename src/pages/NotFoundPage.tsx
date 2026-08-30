import { Link } from '@tanstack/react-router';
import { Compass, ArrowLeft } from 'lucide-react';

export function NotFoundPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-4 soc-grid">
      <Compass className="h-12 w-12 text-cyber-400" />
      <h1 className="font-display text-3xl font-bold text-navy-50">404</h1>
      <p className="text-sm text-navy-400">The page you are looking for does not exist.</p>
      <Link to="/dashboard" className="btn-primary flex items-center gap-2">
        <ArrowLeft className="h-4 w-4" />
        Back to Dashboard
      </Link>
    </div>
  );
}
