import { useQuery } from '@tanstack/react-query';
import {
  Activity, BellRing, Radio, BrainCircuit,
  Zap, AlertTriangle, CheckCircle2, XCircle, Loader2,
  ShieldAlert, TrendingUp, Cpu, Lock,
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
  Area, AreaChart,
} from 'recharts';
import { dashboardApi } from '../api/dashboardApi';
import { captureApi } from '../api/captureApi';
import { alertApi } from '../api/alertApi';
import { useWsStore } from '../store/wsStore';
import { LoadingState, ErrorState, BackendOfflineState, EmptyState } from '../components/StateComponents';
import { cn } from '../utils/cn';
import type { AlertRead } from '../api/types';

const PIE_COLORS = ['#22d3ee', '#3399ff', '#f59e0b', '#ef4444', '#22c55e'];

function StatCard({ icon: Icon, label, value, color, loading }: {
  icon: typeof Activity; label: string; value: string | number; color: string; loading?: boolean;
}) {
  return (
    <div className="glass-card p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-xs font-mono uppercase tracking-wider text-navy-400">{label}</p>
          {loading ? (
            <Loader2 className="mt-2 h-6 w-6 animate-spin text-navy-400" />
          ) : (
            <p className={cn('mt-1 font-display text-2xl font-bold', color)}>{value}</p>
          )}
        </div>
        <div className={cn('rounded-lg p-3', color.replace('text-', 'bg-').replace('-400', '-500/10'))}>
          <Icon className={cn('h-6 w-6', color)} />
        </div>
      </div>
    </div>
  );
}

function WsIndicator() {
  const { connectionState } = useWsStore();
  const config = {
    connected: { label: 'WebSocket Connected', icon: CheckCircle2, color: 'text-success-400' },
    reconnecting: { label: 'WebSocket Reconnecting', icon: Loader2, color: 'text-warning-500', spin: true },
    disconnected: { label: 'WebSocket Disconnected', icon: XCircle, color: 'text-danger-400' },
  }[connectionState];
  const Icon = config.icon;
  return (
    <div className="glass-card flex items-center gap-2.5 px-4 py-3">
      <Icon className={cn('h-4 w-4', config.color, config.spin && 'animate-spin')} />
      <span className={cn('text-sm font-medium', config.color)}>{config.label}</span>
    </div>
  );
}

function SecurityWorkflowPanel() {
  return (
    <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
      <div className="glass-panel p-5">
        <div className="mb-4 flex items-center gap-2">
          <ShieldAlert className="h-5 w-5 text-danger-400" />
          <h3 className="font-display text-sm font-semibold text-navy-100">Security Investigation</h3>
        </div>
        <div className="space-y-3">
          <div className="flex items-center justify-between rounded-lg border border-navy-700 bg-navy-800/30 p-3">
            <div>
              <p className="text-sm font-medium text-navy-100">Packet Capture</p>
              <p className="text-xs text-navy-400">Monitor network interface for threats</p>
            </div>
            <span className="badge border-success-500/30 bg-success-500/10 text-success-400">Available</span>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-navy-700 bg-navy-800/30 p-3">
            <div>
              <p className="text-sm font-medium text-navy-100">Threat Detection</p>
              <p className="text-xs text-navy-400">ML-based anomaly + attack classification</p>
            </div>
            <span className="badge border-success-500/30 bg-success-500/10 text-success-400">Available</span>
          </div>
          <div className="flex items-center justify-between rounded-lg border border-navy-700 bg-navy-800/30 p-3">
            <div>
              <p className="text-sm font-medium text-navy-100">Alert Triage & AI Investigation</p>
              <p className="text-xs text-navy-400">Acknowledge, resolve, and investigate with AI</p>
            </div>
            <span className="badge border-success-500/30 bg-success-500/10 text-success-400">Available</span>
          </div>
        </div>
      </div>

      <div className="glass-panel p-5">
        <div className="mb-4 flex items-center gap-2">
          <TrendingUp className="h-5 w-5 text-cyan-400" />
          <h3 className="font-display text-sm font-semibold text-navy-100">Detection Pipeline</h3>
        </div>
        <div className="space-y-3">
          <div className="flex items-center gap-3">
            <Cpu className="h-4 w-4 text-cyber-400" />
            <div className="flex-1">
              <p className="text-sm text-navy-100">Autoencoder (Anomaly Detection)</p>
              <p className="text-xs text-navy-400">Reconstruction error threshold analysis</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <BrainCircuit className="h-4 w-4 text-cyan-400" />
            <div className="flex-1">
              <p className="text-sm text-navy-100">XGBoost (Attack Classification)</p>
              <p className="text-xs text-navy-400">Multi-class attack type classification</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Lock className="h-4 w-4 text-success-400" />
            <div className="flex-1">
              <p className="text-sm text-navy-100">Post-Quantum Encryption</p>
              <p className="text-xs text-navy-400">Kyber key exchange + AES-GCM alert encryption</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export function DashboardPage() {
  const healthQuery = useQuery({ queryKey: ['health'], queryFn: dashboardApi.health, refetchInterval: 30000 });
  const captureStatusQuery = useQuery({ queryKey: ['capture', 'status'], queryFn: captureApi.status, refetchInterval: 5000 });
  const captureStatsQuery = useQuery({ queryKey: ['capture', 'statistics'], queryFn: captureApi.statistics, refetchInterval: 5000 });
  const detectionStatusQuery = useQuery({ queryKey: ['detection', 'status'], queryFn: dashboardApi.detectionStatus, refetchInterval: 5000 });
  const detectionStatsQuery = useQuery({ queryKey: ['detection', 'statistics'], queryFn: dashboardApi.detectionStatistics, refetchInterval: 10000 });
  const detectionHistoryQuery = useQuery({ queryKey: ['detection', 'history'], queryFn: () => dashboardApi.detectionHistory(24), refetchInterval: 15000 });
  const modelStatusQuery = useQuery({ queryKey: ['detection', 'model'], queryFn: dashboardApi.modelStatus, refetchInterval: 30000 });
  const alertsQuery = useQuery({ queryKey: ['alerts', 'dashboard'], queryFn: () => alertApi.list(1, 100), refetchInterval: 10000 });

  if (healthQuery.isError) {
    return <BackendOfflineState />;
  }
  if (healthQuery.isLoading) {
    return <LoadingState title="Initializing dashboard..." />;
  }

  const captureStatus = captureStatusQuery.data;
  const captureStats = captureStatsQuery.data;
  const detectionStatus = detectionStatusQuery.data;
  const detectionStats = detectionStatsQuery.data;
  const detectionHistory = detectionHistoryQuery.data;
  const modelStatus = modelStatusQuery.data;
  const alerts = alertsQuery.data?.items || [];

  const criticalAlerts = alerts.filter((a: AlertRead) => a.severity.toLowerCase() === 'critical');
  const openAlerts = alerts.filter((a: AlertRead) => a.status === 'open');
  const acknowledgedAlerts = alerts.filter((a: AlertRead) => a.status === 'acknowledged');
  const resolvedAlerts = alerts.filter((a: AlertRead) => a.status === 'resolved');

  const severityData = [
    { name: 'Critical', value: alerts.filter((a: AlertRead) => a.severity.toLowerCase() === 'critical').length },
    { name: 'High', value: alerts.filter((a: AlertRead) => a.severity.toLowerCase() === 'high').length },
    { name: 'Medium', value: alerts.filter((a: AlertRead) => a.severity.toLowerCase() === 'medium').length },
    { name: 'Low', value: alerts.filter((a: AlertRead) => a.severity.toLowerCase() === 'low').length },
  ].filter((d) => d.value > 0);

  const statusData = [
    { name: 'Open', value: openAlerts.length },
    { name: 'Acknowledged', value: acknowledgedAlerts.length },
    { name: 'Resolved', value: resolvedAlerts.length },
  ].filter((d) => d.value > 0);

  const hasAlertData = severityData.length > 0 || statusData.length > 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="font-display text-2xl font-bold text-navy-50">Security Operations Dashboard</h1>
          <p className="text-sm text-navy-400">Real-time threat detection and network monitoring</p>
        </div>
        <WsIndicator />
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-5">
        <StatCard icon={Radio} label="Packets Captured" value={captureStatus?.packets_captured ?? 0} color="text-cyber-400" loading={captureStatusQuery.isLoading} />
        <StatCard icon={Activity} label="Active Flows" value={captureStats?.active_flows ?? 0} color="text-cyan-400" loading={captureStatsQuery.isLoading} />
        <StatCard icon={Zap} label="Detections" value={detectionStats?.total_detections ?? 0} color="text-warning-500" loading={detectionStatsQuery.isLoading} />
        <StatCard icon={BellRing} label="Total Alerts" value={alertsQuery.data?.total ?? 0} color="text-warning-500" loading={alertsQuery.isLoading} />
        <StatCard icon={AlertTriangle} label="Critical Threats" value={criticalAlerts.length} color="text-danger-400" loading={alertsQuery.isLoading} />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="glass-panel p-5">
          <h3 className="mb-3 font-display text-sm font-semibold text-navy-100">Capture Status</h3>
          {captureStatusQuery.isLoading ? (
            <LoadingState title="Loading capture status..." />
          ) : captureStatus ? (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                {captureStatus.running ? (
                  <span className="badge border-success-500/30 bg-success-500/10 text-success-400">
                    <Activity className="mr-1 h-3 w-3" /> Running
                  </span>
                ) : (
                  <span className="badge border-navy-600 bg-navy-700/50 text-navy-300">Stopped</span>
                )}
                <span className="text-sm text-navy-300">
                  {captureStatus.interface ? `Interface: ${captureStatus.interface}` : 'No interface selected'}
                </span>
              </div>
              {!captureStatus.available && (
                <p className="text-xs text-warning-500">{captureStatus.reason}</p>
              )}
            </div>
          ) : (
            <ErrorState title="Capture status unavailable" />
          )}
        </div>

        <div className="glass-panel p-5">
          <h3 className="mb-3 font-display text-sm font-semibold text-navy-100">Detection Status</h3>
          {detectionStatusQuery.isLoading ? (
            <LoadingState title="Loading detection status..." />
          ) : detectionStatus ? (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                {detectionStatus.running ? (
                  <span className="badge border-success-500/30 bg-success-500/10 text-success-400">
                    <Activity className="mr-1 h-3 w-3" /> Active
                  </span>
                ) : (
                  <span className="badge border-navy-600 bg-navy-700/50 text-navy-300">Inactive</span>
                )}
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <p className="text-xs text-navy-400">Model Available</p>
                  <p className="font-mono text-sm text-navy-100">{detectionStatus.model_available ? 'Yes' : 'No'}</p>
                </div>
                <div>
                  <p className="text-xs text-navy-400">Detections</p>
                  <p className="font-mono text-sm text-navy-100">{detectionStatus.detections_count}</p>
                </div>
              </div>
            </div>
          ) : (
            <ErrorState title="Detection status unavailable" />
          )}
        </div>

        <div className="glass-panel p-5">
          <h3 className="mb-3 font-display text-sm font-semibold text-navy-100">Model Status</h3>
          {modelStatusQuery.isLoading ? (
            <LoadingState title="Loading model status..." />
          ) : modelStatus ? (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                {modelStatus.model_available ? (
                  <span className="badge border-success-500/30 bg-success-500/10 text-success-400">
                    <BrainCircuit className="mr-1 h-3 w-3" /> Trained
                  </span>
                ) : (
                  <span className="badge border-warning-500/30 bg-warning-500/10 text-warning-500">Not Trained</span>
                )}
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <p className="text-xs text-navy-400">Version</p>
                  <p className="font-mono text-sm text-navy-100">{modelStatus.model_version || 'N/A'}</p>
                </div>
                <div>
                  <p className="text-xs text-navy-400">Feature Schema</p>
                  <p className="font-mono text-sm text-navy-100">{modelStatus.feature_schema_available ? 'Yes' : 'No'}</p>
                </div>
              </div>
            </div>
          ) : (
            <ErrorState title="Model status unavailable" />
          )}
        </div>
      </div>

      <SecurityWorkflowPanel />

      {detectionHistory && detectionHistory.buckets.length > 0 && (
        <div className="glass-panel p-5">
          <h3 className="mb-4 font-display text-sm font-semibold text-navy-100">Detection History (Last 24 Hours)</h3>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={detectionHistory.buckets}>
              <defs>
                <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3399ff" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#3399ff" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorCritical" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e3560" />
              <XAxis dataKey="timestamp" stroke="#7a99c9" fontSize={10} tickFormatter={(v) => new Date(v).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })} />
              <YAxis stroke="#7a99c9" fontSize={12} allowDecimals={false} />
              <Tooltip
                contentStyle={{ background: '#0f1c38', border: '1px solid #1e3560', borderRadius: '8px' }}
                labelFormatter={(v) => new Date(v).toLocaleString('en-US')}
              />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              <Area type="monotone" dataKey="total" name="Total" stroke="#3399ff" fill="url(#colorTotal)" strokeWidth={2} />
              <Area type="monotone" dataKey="critical" name="Critical" stroke="#ef4444" fill="url(#colorCritical)" strokeWidth={2} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      )}

      {detectionStats && (
        (Object.keys(detectionStats.by_label).length > 0 ||
         Object.keys(detectionStats.by_severity).length > 0 ||
         Object.keys(detectionStats.by_classification).length > 0) && (
          <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
            {Object.keys(detectionStats.by_label).length > 0 && (
              <div className="glass-panel p-5">
                <h3 className="mb-3 font-display text-sm font-semibold text-navy-100">Detections by Attack Type</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={Object.entries(detectionStats.by_label).map(([name, value]) => ({ name, value })).sort((a, b) => b.value - a.value)}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e3560" />
                    <XAxis dataKey="name" stroke="#7a99c9" fontSize={10} angle={-20} textAnchor="end" height={60} />
                    <YAxis stroke="#7a99c9" fontSize={12} allowDecimals={false} />
                    <Tooltip contentStyle={{ background: '#0f1c38', border: '1px solid #1e3560', borderRadius: '8px' }} />
                    <Bar dataKey="value" fill="#22d3ee" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
            {Object.keys(detectionStats.by_severity).length > 0 && (
              <div className="glass-panel p-5">
                <h3 className="mb-3 font-display text-sm font-semibold text-navy-100">Detections by Severity</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={Object.entries(detectionStats.by_severity).map(([name, value]) => ({ name, value }))}
                      dataKey="value"
                      nameKey="name"
                      cx="50%"
                      cy="50%"
                      outerRadius={70}
                      label
                    >
                      {Object.entries(detectionStats.by_severity).map(([sev], i) => {
                        const color = sev.toLowerCase() === 'critical' ? '#ef4444' : sev.toLowerCase() === 'high' ? '#f59e0b' : sev.toLowerCase() === 'medium' ? '#22d3ee' : '#22c55e';
                        return <Cell key={i} fill={color} />;
                      })}
                    </Pie>
                    <Tooltip contentStyle={{ background: '#0f1c38', border: '1px solid #1e3560', borderRadius: '8px' }} />
                    <Legend wrapperStyle={{ fontSize: '12px' }} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            )}
            {Object.keys(detectionStats.by_classification).length > 0 && (
              <div className="glass-panel p-5">
                <h3 className="mb-3 font-display text-sm font-semibold text-navy-100">Detections by Classification</h3>
                <ResponsiveContainer width="100%" height={200}>
                  <BarChart data={Object.entries(detectionStats.by_classification).map(([name, value]) => ({ name, value }))}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e3560" />
                    <XAxis dataKey="name" stroke="#7a99c9" fontSize={10} angle={-20} textAnchor="end" height={60} />
                    <YAxis stroke="#7a99c9" fontSize={12} allowDecimals={false} />
                    <Tooltip contentStyle={{ background: '#0f1c38', border: '1px solid #1e3560', borderRadius: '8px' }} />
                    <Bar dataKey="value" fill="#3399ff" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>
        )
      )}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <div className="glass-panel p-5">
          <h3 className="mb-4 font-display text-sm font-semibold text-navy-100">Alert Severity Distribution</h3>
          {alertsQuery.isLoading ? (
            <LoadingState title="Loading alerts..." />
          ) : hasAlertData ? (
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={severityData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e3560" />
                <XAxis dataKey="name" stroke="#7a99c9" fontSize={12} />
                <YAxis stroke="#7a99c9" fontSize={12} allowDecimals={false} />
                <Tooltip contentStyle={{ background: '#0f1c38', border: '1px solid #1e3560', borderRadius: '8px' }} />
                <Bar dataKey="value" fill="#3399ff" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState title="No alerts" message="No alerts have been generated." />
          )}
        </div>

        <div className="glass-panel p-5">
          <h3 className="mb-4 font-display text-sm font-semibold text-navy-100">Alert Status Distribution</h3>
          {alertsQuery.isLoading ? (
            <LoadingState title="Loading alerts..." />
          ) : hasAlertData ? (
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie data={statusData} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={80} label>
                  {statusData.map((_, i) => (
                    <Cell key={i} fill={PIE_COLORS[i % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: '#0f1c38', border: '1px solid #1e3560', borderRadius: '8px' }} />
                <Legend wrapperStyle={{ fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <EmptyState title="No alerts" message="No alerts have been generated." />
          )}
        </div>
      </div>

      <div className="glass-panel p-5">
        <h3 className="mb-4 font-display text-sm font-semibold text-navy-100">Active Network Flows</h3>
        {captureStatsQuery.isLoading ? (
          <LoadingState title="Loading flow data..." />
        ) : captureStatsQuery.data && captureStatsQuery.data.flow_details.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-navy-700 text-left text-xs uppercase text-navy-400">
                  <th className="pb-2 pr-4 font-medium">Source IP</th>
                  <th className="pb-2 pr-4 font-medium">Destination IP</th>
                  <th className="pb-2 pr-4 font-medium">Protocol</th>
                  <th className="pb-2 pr-4 font-medium">Packets</th>
                  <th className="pb-2 pr-4 font-medium">Bytes</th>
                  <th className="pb-2 font-medium">Duration</th>
                </tr>
              </thead>
              <tbody>
                {captureStatsQuery.data.flow_details.map((flow, i) => (
                  <tr key={i} className="border-b border-navy-800/50">
                    <td className="py-2 pr-4 font-mono text-navy-100">{flow.source_ip}</td>
                    <td className="py-2 pr-4 font-mono text-navy-100">{flow.destination_ip}</td>
                    <td className="py-2 pr-4 font-mono text-cyan-400">{flow.protocol}</td>
                    <td className="py-2 pr-4 font-mono text-navy-200">{flow.packet_count}</td>
                    <td className="py-2 pr-4 font-mono text-navy-200">{flow.byte_count}</td>
                    <td className="py-2 font-mono text-navy-200">{flow.duration_seconds.toFixed(1)}s</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState title="No active flows" message="No network flows have been captured." />
        )}
      </div>
    </div>
  );
}
