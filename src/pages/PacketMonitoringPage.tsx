import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Radio, Play, Square, Search, Loader2, Network } from 'lucide-react';
import { captureApi } from '../api/captureApi';
import { useAuthStore } from '../store/authStore';
import { LoadingState, EmptyState, BackendOfflineState, CaptureUnavailable } from '../components/StateComponents';
import { toast } from 'sonner';
import { cn } from '../utils/cn';

export function PacketMonitoringPage() {
  const [selectedInterface, setSelectedInterface] = useState('');
  const [search, setSearch] = useState('');
  const queryClient = useQueryClient();
  const { hasPermission } = useAuthStore();

  const interfacesQuery = useQuery({ queryKey: ['capture', 'interfaces'], queryFn: captureApi.interfaces });
  const statusQuery = useQuery({ queryKey: ['capture', 'status'], queryFn: captureApi.status, refetchInterval: 3000 });
  const statsQuery = useQuery({ queryKey: ['capture', 'statistics'], queryFn: captureApi.statistics, refetchInterval: 3000 });
  const packetsQuery = useQuery({ queryKey: ['capture', 'packets'], queryFn: captureApi.packets, refetchInterval: 3000 });

  const startMutation = useMutation({
    mutationFn: (iface: string) => captureApi.start(iface),
    onSuccess: () => {
      toast.success('Capture started');
      queryClient.invalidateQueries({ queryKey: ['capture'] });
    },
    onError: (err: unknown) => {
      toast.error((err as { message?: string })?.message || 'Failed to start capture');
    },
  });

  const stopMutation = useMutation({
    mutationFn: () => captureApi.stop(),
    onSuccess: () => {
      toast.info('Capture stopped');
      queryClient.invalidateQueries({ queryKey: ['capture'] });
    },
    onError: (err: unknown) => {
      toast.error((err as { message?: string })?.message || 'Failed to stop capture');
    },
  });

  const canStart = hasPermission('capture:start');
  const canStop = hasPermission('capture:stop');

  if (interfacesQuery.isError || statusQuery.isError) {
    const err = interfacesQuery.error || statusQuery.error;
    if (err && (err as { type?: string }).type === 'network') {
      return <BackendOfflineState />;
    }
  }

  const status = statusQuery.data;
  const stats = statsQuery.data;
  const packets = packetsQuery.data;

  if (status && !status.available) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-2xl font-bold text-navy-50">Packet Monitoring</h1>
          <p className="text-sm text-navy-400">Real-time network packet capture and analysis</p>
        </div>
        <CaptureUnavailable />
      </div>
    );
  }

  const flows = stats?.flow_details || [];
  const filteredFlows = search
    ? flows.filter((f) =>
        f.source_ip.includes(search) ||
        f.destination_ip.includes(search) ||
        f.protocol.toLowerCase().includes(search.toLowerCase())
      )
    : flows;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold text-navy-50">Packet Monitoring</h1>
        <p className="text-sm text-navy-400">Real-time network packet capture and analysis</p>
      </div>

      <div className="glass-panel p-5">
        <div className="flex flex-wrap items-end gap-4">
          <div className="flex-1 min-w-[200px]">
            <label htmlFor="interface" className="mb-1.5 block text-sm font-medium text-navy-200">Network Interface</label>
            <select
              id="interface"
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
              <button
                onClick={() => stopMutation.mutate()}
                disabled={!canStop || stopMutation.isPending}
                className="btn-danger flex items-center gap-2"
              >
                {stopMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Square className="h-4 w-4" />}
                Stop Capture
              </button>
            ) : (
              <button
                onClick={() => selectedInterface && startMutation.mutate(selectedInterface)}
                disabled={!canStart || !selectedInterface || startMutation.isPending}
                className="btn-primary flex items-center gap-2"
              >
                {startMutation.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Play className="h-4 w-4" />}
                Start Capture
              </button>
            )}
          </div>
        </div>

        {!canStart && !status?.running && (
          <p className="mt-2 text-xs text-warning-500">Your role does not permit starting packet capture.</p>
        )}
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="glass-card p-4">
          <div className="flex items-center gap-2 text-navy-400">
            <Radio className="h-4 w-4" />
            <span className="text-xs uppercase tracking-wider">Capture Status</span>
          </div>
          <p className={cn('mt-2 font-display text-xl font-bold', status?.running ? 'text-success-400' : 'text-navy-300')}>
            {status?.running ? 'Running' : 'Stopped'}
          </p>
          {status?.interface && <p className="font-mono text-xs text-navy-400">{status.interface}</p>}
        </div>

        <div className="glass-card p-4">
          <div className="flex items-center gap-2 text-navy-400">
            <Network className="h-4 w-4" />
            <span className="text-xs uppercase tracking-wider">Packets Captured</span>
          </div>
          <p className="mt-2 font-display text-xl font-bold text-cyber-400">
            {packets?.packets_captured ?? 0}
          </p>
        </div>

        <div className="glass-card p-4">
          <div className="flex items-center gap-2 text-navy-400">
            <Network className="h-4 w-4" />
            <span className="text-xs uppercase tracking-wider">Active Flows</span>
          </div>
          <p className="mt-2 font-display text-xl font-bold text-cyan-400">
            {stats?.active_flows ?? 0}
          </p>
        </div>
      </div>

      <div className="glass-panel p-5">
        <div className="mb-4 flex items-center justify-between gap-4">
          <h3 className="font-display text-sm font-semibold text-navy-100">Active Network Flows</h3>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-navy-400" />
            <input
              type="text"
              placeholder="Search by IP or protocol..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="input-field w-64 pl-10 text-sm"
            />
          </div>
        </div>

        {statsQuery.isLoading ? (
          <LoadingState title="Loading flows..." />
        ) : filteredFlows.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-navy-700 text-left text-xs uppercase text-navy-400">
                  <th className="pb-2 pr-4 font-medium">Source IP</th>
                  <th className="pb-2 pr-4 font-medium">Src Port</th>
                  <th className="pb-2 pr-4 font-medium">Destination IP</th>
                  <th className="pb-2 pr-4 font-medium">Dst Port</th>
                  <th className="pb-2 pr-4 font-medium">Protocol</th>
                  <th className="pb-2 pr-4 font-medium">Packets</th>
                  <th className="pb-2 pr-4 font-medium">Bytes</th>
                  <th className="pb-2 pr-4 font-medium">Duration</th>
                </tr>
              </thead>
              <tbody>
                {filteredFlows.map((flow, i) => (
                  <tr key={i} className="border-b border-navy-800/50 hover:bg-navy-800/30">
                    <td className="py-2 pr-4 font-mono text-navy-100">{flow.source_ip}</td>
                    <td className="py-2 pr-4 font-mono text-navy-300">{flow.source_port ?? '-'}</td>
                    <td className="py-2 pr-4 font-mono text-navy-100">{flow.destination_ip}</td>
                    <td className="py-2 pr-4 font-mono text-navy-300">{flow.destination_port ?? '-'}</td>
                    <td className="py-2 pr-4"><span className="badge border-cyan-500/30 bg-cyan-500/10 text-cyan-400">{flow.protocol}</span></td>
                    <td className="py-2 pr-4 font-mono text-navy-200">{flow.packet_count}</td>
                    <td className="py-2 pr-4 font-mono text-navy-200">{flow.byte_count}</td>
                    <td className="py-2 pr-4 font-mono text-navy-200">{flow.duration_seconds.toFixed(1)}s</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <EmptyState title="No active flows" message="Start a capture to see network flow data." />
        )}
      </div>
    </div>
  );
}
