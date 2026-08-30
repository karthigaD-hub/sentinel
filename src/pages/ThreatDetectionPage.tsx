import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ShieldAlert, Play, Square, Loader2, Activity, BrainCircuit } from 'lucide-react';
import { detectionApi } from '../api/detectionApi';
import { captureApi } from '../api/captureApi';
import { useAuthStore } from '../store/authStore';
import { LoadingState, EmptyState, BackendOfflineState, ModelUnavailable } from '../components/StateComponents';
import { toast } from 'sonner';
import { cn, formatTimestamp, classificationColor } from '../utils/cn';

export function ThreatDetectionPage() {
  const [page, setPage] = useState(1);
  const [selectedInterface, setSelectedInterface] = useState('');
  const queryClient = useQueryClient();
  const { hasPermission } = useAuthStore();

  const statusQuery = useQuery({ queryKey: ['detection', 'status'], queryFn: detectionApi.status, refetchInterval: 5000 });
  const statsQuery = useQuery({ queryKey: ['detection', 'statistics'], queryFn: detectionApi.statistics, refetchInterval: 10000 });
  const resultsQuery = useQuery({ queryKey: ['detection', 'results', page], queryFn: () => detectionApi.results(page, 50), refetchInterval: 10000 });
  const modelStatusQuery = useQuery({ queryKey: ['detection', 'model'], queryFn: detectionApi.modelStatus });
  const interfacesQuery = useQuery({ queryKey: ['capture', 'interfaces'], queryFn: captureApi.interfaces });

  const startMutation = useMutation({
    mutationFn: (iface: string) => detectionApi.start(iface),
    onSuccess: () => {
      toast.success('Detection started');
      queryClient.invalidateQueries({ queryKey: ['detection'] });
    },
    onError: (err: unknown) => toast.error((err as { message?: string })?.message || 'Failed to start detection'),
  });

  const stopMutation = useMutation({
    mutationFn: () => detectionApi.stop(),
    onSuccess: () => {
      toast.info('Detection stopped');
      queryClient.invalidateQueries({ queryKey: ['detection'] });
    },
    onError: (err: unknown) => toast.error((err as { message?: string })?.message || 'Failed to stop detection'),
  });

  if (statusQuery.isError && (statusQuery.error as { type?: string })?.type === 'network') {
    return <BackendOfflineState />;
  }

  const status = statusQuery.data;
  const modelStatus = modelStatusQuery.data;
  const results = resultsQuery.data;
  const canStart = hasPermission('capture:start');
  const canStop = hasPermission('capture:stop');

  if (modelStatus && !modelStatus.model_available) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-2xl font-bold text-navy-50">Threat Detection</h1>
          <p className="text-sm text-navy-400">AI-powered anomaly detection and attack classification</p>
        </div>
        <ModelUnavailable />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold text-navy-50">Threat Detection</h1>
        <p className="text-sm text-navy-400">AI-powered anomaly detection and attack classification</p>
      </div>

      <div className="glass-panel p-5">
        <div className="flex flex-wrap items-end gap-4">
          <div className="flex-1 min-w-[200px]">
            <label htmlFor="iface" className="mb-1.5 block text-sm font-medium text-navy-200">Network Interface</label>
            <select
              id="iface"
              value={selectedInterface}
              onChange={(e) => setSelectedInterface(e.target.value)}
              className="input-field"
              disabled={status?.running}
            >
              <option value="">Select interface...</option>
              {interfacesQuery.data?.map((iface) => (
                <option key={iface.name} value={iface.name}>
                  {iface.name} {iface.address ? `(${iface.address})` : ''}
                </option>
              ))}
            </select>
          </div>
          <div className="flex gap-2">
            {status?.running ? (
              <button onClick={() => stopMutation.mutate()} disabled={!canStop || stopMutation.isPending} className="btn-danger flex items-center gap-2">
                {stopMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Square className="h-4 w-4" />}
                Stop Detection
              </button>
            ) : (
              <button onClick={() => selectedInterface && startMutation.mutate(selectedInterface)} disabled={!canStart || !selectedInterface || startMutation.isPending} className="btn-primary flex items-center gap-2">
                {startMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                Start Detection
              </button>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="glass-card p-4">
          <div className="flex items-center gap-2 text-navy-400">
            <Activity className="h-4 w-4" />
            <span className="text-xs uppercase tracking-wider">Detection Status</span>
          </div>
          <p className={cn('mt-2 font-display text-xl font-bold', status?.running ? 'text-success-400' : 'text-navy-300')}>
            {status?.running ? 'Active' : 'Inactive'}
          </p>
        </div>
        <div className="glass-card p-4">
          <div className="flex items-center gap-2 text-navy-400">
            <ShieldAlert className="h-4 w-4" />
            <span className="text-xs uppercase tracking-wider">Total Detections</span>
          </div>
          <p className="mt-2 font-display text-xl font-bold text-cyber-400">{statsQuery.data?.total_detections ?? 0}</p>
        </div>
        <div className="glass-card p-4">
          <div className="flex items-center gap-2 text-navy-400">
            <BrainCircuit className="h-4 w-4" />
            <span className="text-xs uppercase tracking-wider">Model Available</span>
          </div>
          <p className={cn('mt-2 font-display text-xl font-bold', status?.model_available ? 'text-success-400' : 'text-warning-500')}>
            {status?.model_available ? 'Yes' : 'No'}
          </p>
        </div>
      </div>

      {modelStatus?.metrics_available && modelStatus.metrics && (
        <div className="glass-panel p-5">
          <h3 className="mb-4 font-display text-sm font-semibold text-navy-100">Model Metrics</h3>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
            {modelStatus.metrics.accuracy != null && (
              <div className="glass-card p-3">
                <p className="text-xs text-navy-400">Accuracy</p>
                <p className="font-mono text-lg text-success-400">{(modelStatus.metrics.accuracy * 100).toFixed(1)}%</p>
              </div>
            )}
            {modelStatus.metrics.precision != null && (
              <div className="glass-card p-3">
                <p className="text-xs text-navy-400">Precision</p>
                <p className="font-mono text-lg text-cyan-400">{(modelStatus.metrics.precision * 100).toFixed(1)}%</p>
              </div>
            )}
            {modelStatus.metrics.recall != null && (
              <div className="glass-card p-3">
                <p className="text-xs text-navy-400">Recall</p>
                <p className="font-mono text-lg text-cyber-400">{(modelStatus.metrics.recall * 100).toFixed(1)}%</p>
              </div>
            )}
            {modelStatus.metrics.f1 != null && (
              <div className="glass-card p-3">
                <p className="text-xs text-navy-400">F1 Score</p>
                <p className="font-mono text-lg text-warning-500">{(modelStatus.metrics.f1 * 100).toFixed(1)}%</p>
              </div>
            )}
            {modelStatus.metrics.roc_auc != null && (
              <div className="glass-card p-3">
                <p className="text-xs text-navy-400">ROC-AUC</p>
                <p className="font-mono text-lg text-success-400">{(modelStatus.metrics.roc_auc * 100).toFixed(1)}%</p>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="glass-panel p-5">
        <h3 className="mb-4 font-display text-sm font-semibold text-navy-100">Detection Results</h3>
        {resultsQuery.isLoading ? (
          <LoadingState title="Loading detections..." />
        ) : results && results.items.length > 0 ? (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-navy-700 text-left text-xs uppercase text-navy-400">
                    <th className="pb-2 pr-4 font-medium">Timestamp</th>
                    <th className="pb-2 pr-4 font-medium">Label</th>
                    <th className="pb-2 pr-4 font-medium">Confidence</th>
                    <th className="pb-2 pr-4 font-medium">Model Version</th>
                  </tr>
                </thead>
                <tbody>
                  {results.items.map((det) => (
                    <tr key={det.id} className="border-b border-navy-800/50 hover:bg-navy-800/30">
                      <td className="py-2 pr-4 font-mono text-xs text-navy-300">{formatTimestamp(det.detected_at)}</td>
                      <td className="py-2 pr-4">
                        <span className={cn('badge', classificationColor(det.label))}>{det.label}</span>
                      </td>
                      <td className="py-2 pr-4 font-mono text-navy-200">{(det.confidence * 100).toFixed(1)}%</td>
                      <td className="py-2 pr-4 font-mono text-xs text-navy-400">{det.model_version}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-4 flex items-center justify-between">
              <p className="text-xs text-navy-400">
                Page {results.page} of {Math.max(1, Math.ceil(results.total / results.page_size))} — {results.total} total
              </p>
              <div className="flex gap-2">
                <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page <= 1} className="btn-secondary text-sm">Previous</button>
                <button onClick={() => setPage((p) => p + 1)} disabled={results.items.length < results.page_size} className="btn-secondary text-sm">Next</button>
              </div>
            </div>
          </>
        ) : (
          <EmptyState title="No detections" message="No threats have been detected yet. Start detection to monitor network traffic." />
        )}
      </div>
    </div>
  );
}
