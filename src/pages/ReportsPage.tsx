import { useQuery } from '@tanstack/react-query';
import { FileText } from 'lucide-react';
import { reportApi } from '../api/reportApi';
import { dashboardApi } from '../api/dashboardApi';
import { captureApi } from '../api/captureApi';
import { LoadingState, EmptyState, BackendOfflineState } from '../components/StateComponents';
import { formatTimestamp } from '../utils/cn';

export function ReportsPage() {
  const reportsQuery = useQuery({ queryKey: ['reports'], queryFn: reportApi.list });
  const detectionStatsQuery = useQuery({ queryKey: ['detection', 'statistics'], queryFn: dashboardApi.detectionStatistics });
  const captureStatsQuery = useQuery({ queryKey: ['capture', 'statistics'], queryFn: captureApi.statistics });
  const modelStatusQuery = useQuery({ queryKey: ['detection', 'model'], queryFn: dashboardApi.modelStatus });

  if (reportsQuery.isError && (reportsQuery.error as { type?: string })?.type === 'network') {
    return <BackendOfflineState />;
  }

  const reports = reportsQuery.data;
  const detectionStats = detectionStatsQuery.data;
  const captureStats = captureStatsQuery.data;
  const modelStatus = modelStatusQuery.data;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold text-navy-50">Reports</h1>
        <p className="text-sm text-navy-400">Security analytics and system summary</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="glass-card p-4">
          <p className="text-xs uppercase tracking-wider text-navy-400">Packets Captured</p>
          <p className="mt-2 font-display text-xl font-bold text-cyber-400">{captureStats?.packets_captured ?? 0}</p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs uppercase tracking-wider text-navy-400">Total Detections</p>
          <p className="mt-2 font-display text-xl font-bold text-cyan-400">{detectionStats?.total_detections ?? 0}</p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs uppercase tracking-wider text-navy-400">Model Available</p>
          <p className="mt-2 font-display text-xl font-bold text-navy-100">{modelStatus?.model_available ? 'Yes' : 'No'}</p>
        </div>
        <div className="glass-card p-4">
          <p className="text-xs uppercase tracking-wider text-navy-400">Active Flows</p>
          <p className="mt-2 font-display text-xl font-bold text-navy-100">{captureStats?.active_flows ?? 0}</p>
        </div>
      </div>

      {modelStatus?.metrics_available && modelStatus.metrics && (
        <div className="glass-panel p-5">
          <h3 className="mb-4 font-display text-sm font-semibold text-navy-100">Model Performance Metrics</h3>
          <div className="grid grid-cols-2 gap-4 sm:grid-cols-5">
            {modelStatus.metrics.accuracy != null && (
              <div className="glass-card p-3 text-center">
                <p className="text-xs text-navy-400">Accuracy</p>
                <p className="font-mono text-lg text-success-400">{(modelStatus.metrics.accuracy * 100).toFixed(1)}%</p>
              </div>
            )}
            {modelStatus.metrics.precision != null && (
              <div className="glass-card p-3 text-center">
                <p className="text-xs text-navy-400">Precision</p>
                <p className="font-mono text-lg text-cyan-400">{(modelStatus.metrics.precision * 100).toFixed(1)}%</p>
              </div>
            )}
            {modelStatus.metrics.recall != null && (
              <div className="glass-card p-3 text-center">
                <p className="text-xs text-navy-400">Recall</p>
                <p className="font-mono text-lg text-cyber-400">{(modelStatus.metrics.recall * 100).toFixed(1)}%</p>
              </div>
            )}
            {modelStatus.metrics.f1 != null && (
              <div className="glass-card p-3 text-center">
                <p className="text-xs text-navy-400">F1</p>
                <p className="font-mono text-lg text-warning-500">{(modelStatus.metrics.f1 * 100).toFixed(1)}%</p>
              </div>
            )}
            {modelStatus.metrics.roc_auc != null && (
              <div className="glass-card p-3 text-center">
                <p className="text-xs text-navy-400">ROC-AUC</p>
                <p className="font-mono text-lg text-success-400">{(modelStatus.metrics.roc_auc * 100).toFixed(1)}%</p>
              </div>
            )}
          </div>
        </div>
      )}

      <div className="glass-panel p-5">
        <h3 className="mb-4 font-display text-sm font-semibold text-navy-100">Generated Reports</h3>
        {reportsQuery.isLoading ? (
          <LoadingState title="Loading reports..." />
        ) : reports && reports.items.length > 0 ? (
          <div className="space-y-2">
            {reports.items.map((report, i) => {
              const r = report as Record<string, unknown>;
              return (
              <div key={i} className="glass-card flex items-center gap-3 p-4">
                <FileText className="h-5 w-5 text-cyber-400" />
                <div>
                  <p className="text-sm font-medium text-navy-100">{String(r.title || r.name || `Report ${i + 1}`)}</p>
                  <p className="text-xs text-navy-400">{formatTimestamp(String(r.created_at || r.date || ''))}</p>
                </div>
              </div>
              );
            })}
          </div>
        ) : (
          <EmptyState title="No reports" message="No reports have been generated. Report generation requires a configured worker." />
        )}
      </div>
    </div>
  );
}
