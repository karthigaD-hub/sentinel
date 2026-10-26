import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from '@tanstack/react-router';
import { CheckCircle2, RotateCcw, Bot } from 'lucide-react';
import { alertApi } from '../api/alertApi';
import { useAuthStore } from '../store/authStore';
import { LoadingState, EmptyState, BackendOfflineState } from '../components/StateComponents';
import { toast } from 'sonner';
import { cn, formatTimestamp, severityColor, statusColor } from '../utils/cn';

export function AlertManagementPage() {
  const [page, setPage] = useState(1);
  const queryClient = useQueryClient();
  const { hasPermission } = useAuthStore();
  const navigate = useNavigate();

  const alertsQuery = useQuery({ queryKey: ['alerts', page], queryFn: () => alertApi.list(page, 50), refetchInterval: 10000 });
  const canUpdate = hasPermission('alerts:update');

  const acknowledgeMutation = useMutation({
    mutationFn: alertApi.acknowledge,
    onSuccess: () => { toast.success('Alert acknowledged'); queryClient.invalidateQueries({ queryKey: ['alerts'] }); },
    onError: (e: unknown) => toast.error((e as { message?: string })?.message || 'Failed to acknowledge'),
  });
  const resolveMutation = useMutation({
    mutationFn: alertApi.resolve,
    onSuccess: () => { toast.success('Alert resolved'); queryClient.invalidateQueries({ queryKey: ['alerts'] }); },
    onError: (e: unknown) => toast.error((e as { message?: string })?.message || 'Failed to resolve'),
  });
  const reopenMutation = useMutation({
    mutationFn: alertApi.reopen,
    onSuccess: () => { toast.success('Alert reopened'); queryClient.invalidateQueries({ queryKey: ['alerts'] }); },
    onError: (e: unknown) => toast.error((e as { message?: string })?.message || 'Failed to reopen'),
  });

  if (alertsQuery.isError && (alertsQuery.error as { type?: string })?.type === 'network') {
    return <BackendOfflineState />;
  }

  const alerts = alertsQuery.data;

  const handleInvestigate = (alertTitle: string, alertSeverity: string, alertDescription: string) => {
    const investigationQuery = `I need to investigate this security alert:\n\nAlert: ${alertTitle}\nSeverity: ${alertSeverity}\nDetails: ${alertDescription}\n\nWhat type of attack is this? What does it mean? Why was it detected? What is the severity level? What should I investigate next? What mitigation steps are recommended?`;
    navigate({ to: '/assistant', search: { q: investigationQuery } });
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold text-navy-50">Alert Management</h1>
        <p className="text-sm text-navy-400">Security alert lifecycle management with AI investigation</p>
      </div>

      <div className="glass-panel p-5">
        <h3 className="mb-4 font-display text-sm font-semibold text-navy-100">Alerts</h3>
        {alertsQuery.isLoading ? (
          <LoadingState title="Loading alerts..." />
        ) : alerts && alerts.items.length > 0 ? (
          <>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-navy-700 text-left text-xs uppercase text-navy-400">
                    <th className="pb-2 pr-4 font-medium">Title</th>
                    <th className="pb-2 pr-4 font-medium">Severity</th>
                    <th className="pb-2 pr-4 font-medium">Status</th>
                    <th className="pb-2 pr-4 font-medium">Created</th>
                    <th className="pb-2 pr-4 font-medium">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {alerts.items.map((alert) => (
                    <tr key={alert.id} className="border-b border-navy-800/50 hover:bg-navy-800/30">
                      <td className="py-3 pr-4">
                        <p className="font-medium text-navy-100">{alert.title}</p>
                        <p className="mt-0.5 max-w-md truncate text-xs text-navy-400">{alert.description}</p>
                      </td>
                      <td className="py-3 pr-4">
                        <span className={cn('badge', severityColor(alert.severity))}>{alert.severity}</span>
                      </td>
                      <td className="py-3 pr-4">
                        <span className={cn('badge', statusColor(alert.status))}>{alert.status}</span>
                      </td>
                      <td className="py-3 pr-4 font-mono text-xs text-navy-300">{formatTimestamp(alert.created_at)}</td>
                      <td className="py-3 pr-4">
                        <div className="flex gap-1.5">
                          <button
                            onClick={() => handleInvestigate(alert.title, alert.severity, alert.description)}
                            className="flex items-center gap-1 rounded p-1.5 text-cyber-400 transition-colors hover:bg-cyber-500/10"
                            title="Investigate with AI"
                          >
                            <Bot className="h-4 w-4" />
                          </button>
                          {alert.status === 'open' && (
                            <button
                              onClick={() => acknowledgeMutation.mutate(alert.id)}
                              disabled={!canUpdate || acknowledgeMutation.isPending}
                              className="rounded p-1.5 text-warning-500 hover:bg-warning-500/10 disabled:opacity-50"
                              title="Acknowledge"
                            >
                              <CheckCircle2 className="h-4 w-4" />
                            </button>
                          )}
                          {(alert.status === 'open' || alert.status === 'acknowledged') && (
                            <button
                              onClick={() => resolveMutation.mutate(alert.id)}
                              disabled={!canUpdate || resolveMutation.isPending}
                              className="rounded p-1.5 text-success-400 hover:bg-success-500/10 disabled:opacity-50"
                              title="Resolve"
                            >
                              <CheckCircle2 className="h-4 w-4" />
                            </button>
                          )}
                          {alert.status === 'resolved' && (
                            <button
                              onClick={() => reopenMutation.mutate(alert.id)}
                              disabled={!canUpdate || reopenMutation.isPending}
                              className="rounded p-1.5 text-cyber-400 hover:bg-cyber-500/10 disabled:opacity-50"
                              title="Reopen"
                            >
                              <RotateCcw className="h-4 w-4" />
                            </button>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="mt-4 flex items-center justify-between">
              <p className="text-xs text-navy-400">
                Page {alerts.page} of {Math.max(1, Math.ceil(alerts.total / alerts.page_size))} — {alerts.total} total
              </p>
              <div className="flex gap-2">
                <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page <= 1} className="btn-secondary text-sm">Previous</button>
                <button onClick={() => setPage((p) => p + 1)} disabled={alerts.items.length < alerts.page_size} className="btn-secondary text-sm">Next</button>
              </div>
            </div>
          </>
        ) : (
          <EmptyState title="No alerts" message="No security alerts have been generated." />
        )}
      </div>
    </div>
  );
}
