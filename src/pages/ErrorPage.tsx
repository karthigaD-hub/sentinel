import { Link } from '@tanstack/react-router';
import { AlertTriangle, ArrowLeft } from 'lucide-react';

export function ErrorPage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-4 px-4 soc-grid">
      <AlertTriangle className="h-12 w-12 text-danger-400" />
      <h1 className="font-display text-3xl font-bold text-navy-50">Server Error</h1>
      <p className="text-sm text-navy-400">Something went wrong on the server side.</p>
      <Link to="/dashboard" className="btn-primary flex items-center gap-2">
        <ArrowLeft className="h-4 w-4" />
        Back to Dashboard
      </Link>
    </div>
  );
}
