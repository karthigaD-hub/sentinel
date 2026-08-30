import { useQuery, useMutation } from '@tanstack/react-query';
import { Atom, ShieldCheck, KeyRound, Lock, Send, CheckCircle2, XCircle, Loader2, ArrowDown } from 'lucide-react';
import { quantumApi } from '../api/quantumApi';
import { BackendOfflineState, QuantumUnavailable } from '../components/StateComponents';
import { toast } from 'sonner';
import { cn } from '../utils/cn';

const PIPELINE_STEPS = [
  { label: 'Threat Detected', icon: ShieldCheck, color: 'text-danger-400' },
  { label: 'Alert Created', icon: ShieldCheck, color: 'text-warning-500' },
  { label: 'Kyber KEM', icon: KeyRound, color: 'text-cyber-400' },
  { label: 'Shared Secret', icon: KeyRound, color: 'text-cyan-400' },
  { label: 'AES-256-GCM', icon: Lock, color: 'text-success-400' },
  { label: 'Secure Alert', icon: Lock, color: 'text-success-400' },
  { label: 'Receiver', icon: Send, color: 'text-cyber-400' },
  { label: 'Kyber Decapsulation', icon: KeyRound, color: 'text-cyan-400' },
  { label: 'AES-GCM Decryption', icon: Lock, color: 'text-success-400' },
];

export function QuantumSecurityPage() {
  const statusQuery = useQuery({ queryKey: ['quantum', 'status'], queryFn: quantumApi.status, refetchInterval: 30000 });

  const testMutation = useMutation({
    mutationFn: quantumApi.test,
    onSuccess: (data) => {
      if (data.available) {
        toast.success('Kyber KEM test passed — keygen, encapsulation, and decapsulation verified');
      } else {
        toast.error(data.reason || 'Kyber test failed');
      }
    },
    onError: (e: unknown) => toast.error((e as { message?: string })?.message || 'Test failed'),
  });

  if (statusQuery.isError && (statusQuery.error as { type?: string })?.type === 'network') {
    return <BackendOfflineState />;
  }

  const status = statusQuery.data;

  if (status && !status.kyber_available) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-2xl font-bold text-navy-50">Quantum Security</h1>
          <p className="text-sm text-navy-400">Post-quantum key establishment and alert encryption</p>
        </div>
        <QuantumUnavailable />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold text-navy-50">Quantum Security</h1>
        <p className="text-sm text-navy-400">Post-quantum key establishment and alert encryption</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="glass-card p-4">
          <div className="flex items-center gap-2 text-navy-400">
            <Atom className="h-4 w-4" />
            <span className="text-xs uppercase tracking-wider">Kyber Available</span>
          </div>
          <p className={cn('mt-2 font-display text-lg font-bold', status?.kyber_available ? 'text-success-400' : 'text-danger-400')}>
            {status?.kyber_available ? 'Yes' : 'No'}
          </p>
        </div>
        <div className="glass-card p-4">
          <div className="flex items-center gap-2 text-navy-400">
            <KeyRound className="h-4 w-4" />
            <span className="text-xs uppercase tracking-wider">Kyber Variant</span>
          </div>
          <p className="mt-2 font-display text-lg font-bold text-cyber-400">{status?.kyber_variant || 'N/A'}</p>
        </div>
        <div className="glass-card p-4">
          <div className="flex items-center gap-2 text-navy-400">
            <Lock className="h-4 w-4" />
            <span className="text-xs uppercase tracking-wider">AES-GCM</span>
          </div>
          <p className={cn('mt-2 font-display text-lg font-bold', status?.aes_gcm_available ? 'text-success-400' : 'text-danger-400')}>
            {status?.aes_gcm_available ? 'Available' : 'Unavailable'}
          </p>
        </div>
      </div>

      <div className="glass-panel p-5">
        <h3 className="mb-2 font-display text-sm font-semibold text-navy-100">Secure Alert Pipeline</h3>
        <p className="mb-6 text-sm text-navy-400">
          Kyber is used for post-quantum key establishment. AES-GCM protects the alert payload.
        </p>

        <div className="flex flex-col items-center gap-0">
          {PIPELINE_STEPS.map((step, i) => {
            const Icon = step.icon;
            return (
              <div key={i} className="flex flex-col items-center">
                <div className="glass-card flex items-center gap-3 px-5 py-3" style={{ minWidth: '280px' }}>
                  <Icon className={cn('h-5 w-5', step.color)} />
                  <span className="text-sm font-medium text-navy-100">{step.label}</span>
                </div>
                {i < PIPELINE_STEPS.length - 1 && (
                  <ArrowDown className="my-1 h-4 w-4 text-navy-500" />
                )}
              </div>
            );
          })}
        </div>
      </div>

      <div className="glass-panel p-5">
        <h3 className="mb-4 font-display text-sm font-semibold text-navy-100">Kyber KEM Test</h3>
        <p className="mb-4 text-sm text-navy-400">
          Run a full Kyber key generation, encapsulation, and decapsulation cycle to verify the post-quantum key exchange.
        </p>
        <button
          onClick={() => testMutation.mutate()}
          disabled={testMutation.isPending || !status?.kyber_available}
          className="btn-primary flex items-center gap-2"
        >
          {testMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Atom className="h-4 w-4" />}
          Run Kyber Test
        </button>

        {testMutation.data && (
          <div className="mt-4 space-y-2">
            {testMutation.data.available ? (
              <>
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle2 className="h-4 w-4 text-success-400" />
                  <span className="text-navy-100">Keygen: <span className="font-mono text-success-400">{testMutation.data.keygen}</span></span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle2 className="h-4 w-4 text-success-400" />
                  <span className="text-navy-100">Encapsulation: <span className="font-mono text-success-400">{testMutation.data.encapsulation}</span></span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle2 className="h-4 w-4 text-success-400" />
                  <span className="text-navy-100">Decapsulation: <span className="font-mono text-success-400">{testMutation.data.decapsulation}</span></span>
                </div>
                <div className="flex items-center gap-2 text-sm">
                  {testMutation.data.shared_secret_verified ? (
                    <CheckCircle2 className="h-4 w-4 text-success-400" />
                  ) : (
                    <XCircle className="h-4 w-4 text-danger-400" />
                  )}
                  <span className="text-navy-100">Shared Secret Verified: <span className="font-mono">{testMutation.data.shared_secret_verified ? 'Yes' : 'No'}</span></span>
                </div>
              </>
            ) : (
              <div className="flex items-center gap-2 text-sm">
                <XCircle className="h-4 w-4 text-danger-400" />
                <span className="text-navy-100">{testMutation.data.reason}</span>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="glass-panel p-5">
        <h3 className="mb-3 font-display text-sm font-semibold text-navy-100">How It Works</h3>
        <div className="space-y-2 text-sm text-navy-300">
          <p><span className="font-mono text-cyber-400">Kyber KEM</span> generates a post-quantum key pair. The public key is used by the sender to encapsulate a shared secret, producing a ciphertext.</p>
          <p>The receiver decapsulates the ciphertext using their private key, recovering the same shared secret. Both parties verify the secret matches.</p>
          <p><span className="font-mono text-success-400">AES-256-GCM</span> then encrypts the alert payload using the shared secret as the encryption key, providing confidentiality and integrity.</p>
          <p className="text-xs text-navy-400 mt-3">The frontend does not perform quantum computation. All cryptographic operations run on the backend.</p>
        </div>
      </div>
    </div>
  );
}
