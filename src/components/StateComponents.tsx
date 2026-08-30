import { type ReactNode } from 'react';
import { AlertCircle, WifiOff, Lock, Ban, ShieldOff, BrainCircuit, Radio, BookOpen, Atom, Inbox } from 'lucide-react';
import { cn } from '../utils/cn';

interface StateProps {
  title?: string;
  message?: string;
  action?: ReactNode;
  className?: string;
}

export function ErrorState({ title = 'Something went wrong', message = 'An unexpected error occurred.', action, className }: StateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3 py-16 text-center', className)}>
      <AlertCircle className="h-10 w-10 text-danger-400" />
      <h3 className="font-display text-lg font-semibold text-navy-100">{title}</h3>
      <p className="max-w-md text-sm text-navy-300">{message}</p>
      {action}
    </div>
  );
}

export function EmptyState({ title = 'No data available', message = 'There is no data to display yet.', action, className }: StateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3 py-16 text-center', className)}>
      <Inbox className="h-10 w-10 text-navy-400" />
      <h3 className="font-display text-lg font-semibold text-navy-100">{title}</h3>
      <p className="max-w-md text-sm text-navy-300">{message}</p>
      {action}
    </div>
  );
}

export function LoadingState({ title = 'Loading...', message, className }: StateProps) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3 py-16 text-center', className)}>
      <div className="h-8 w-8 animate-spin rounded-full border-2 border-cyber-500 border-t-transparent" />
      <h3 className="font-display text-lg font-semibold text-navy-100">{title}</h3>
      {message && <p className="text-sm text-navy-300">{message}</p>}
    </div>
  );
}

export function BackendOfflineState({ className }: { className?: string }) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3 py-16 text-center', className)}>
      <WifiOff className="h-10 w-10 text-danger-400" />
      <h3 className="font-display text-lg font-semibold text-navy-100">Backend unavailable</h3>
      <p className="max-w-md text-sm text-navy-300">The Q-Sentinel backend is not responding. Verify the backend is running and your network connection is active.</p>
    </div>
  );
}

export function ModelUnavailable({ className }: { className?: string }) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3 py-16 text-center', className)}>
      <BrainCircuit className="h-10 w-10 text-warning-500" />
      <h3 className="font-display text-lg font-semibold text-navy-100">Model not trained</h3>
      <p className="max-w-md text-sm text-navy-300">Detection models have not been trained. Train the Autoencoder and XGBoost models to enable threat detection.</p>
    </div>
  );
}

export function CaptureUnavailable({ className }: { className?: string }) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3 py-16 text-center', className)}>
      <Radio className="h-10 w-10 text-warning-500" />
      <h3 className="font-display text-lg font-semibold text-navy-100">Capture unavailable</h3>
      <p className="max-w-md text-sm text-navy-300">Packet capture requires local network interface permissions and the Scapy library. These are not available in this environment.</p>
    </div>
  );
}

export function RAGUnavailable({ className }: { className?: string }) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3 py-16 text-center', className)}>
      <BookOpen className="h-10 w-10 text-warning-500" />
      <h3 className="font-display text-lg font-semibold text-navy-100">RAG unavailable</h3>
      <p className="max-w-md text-sm text-navy-300">The RAG knowledge index is not configured. Ingest threat intelligence documents to enable retrieval-augmented search.</p>
    </div>
  );
}

export function LLMUnavailable({ className }: { className?: string }) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3 py-16 text-center', className)}>
      <BrainCircuit className="h-10 w-10 text-warning-500" />
      <h3 className="font-display text-lg font-semibold text-navy-100">LLM unavailable</h3>
      <p className="max-w-md text-sm text-navy-300">The LLM provider is not configured. Set LLM_PROVIDER, LLM_MODEL, and LLM_API_KEY in the backend environment.</p>
    </div>
  );
}

export function QuantumUnavailable({ className }: { className?: string }) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3 py-16 text-center', className)}>
      <Atom className="h-10 w-10 text-warning-500" />
      <h3 className="font-display text-lg font-semibold text-navy-100">Quantum unavailable</h3>
      <p className="max-w-md text-sm text-navy-300">The post-quantum Kyber library is not installed. Install the Kyber KEM dependency to enable quantum-resistant key establishment.</p>
    </div>
  );
}

export function PermissionDenied({ className }: { className?: string }) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3 py-16 text-center', className)}>
      <Lock className="h-10 w-10 text-warning-500" />
      <h3 className="font-display text-lg font-semibold text-navy-100">Permission denied</h3>
      <p className="max-w-md text-sm text-navy-300">You do not have permission to view this page. Contact an administrator if you believe this is an error.</p>
    </div>
  );
}

export function ForbiddenState({ className }: { className?: string }) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3 py-16 text-center', className)}>
      <Ban className="h-10 w-10 text-danger-400" />
      <h3 className="font-display text-lg font-semibold text-navy-100">Access forbidden</h3>
      <p className="max-w-md text-sm text-navy-300">Your role does not permit this action. Contact an administrator to request elevated access.</p>
    </div>
  );
}

export function UnauthorizedState({ className }: { className?: string }) {
  return (
    <div className={cn('flex flex-col items-center justify-center gap-3 py-16 text-center', className)}>
      <ShieldOff className="h-10 w-10 text-danger-400" />
      <h3 className="font-display text-lg font-semibold text-navy-100">Authentication required</h3>
      <p className="max-w-md text-sm text-navy-300">You must be signed in to access this page.</p>
    </div>
  );
}
