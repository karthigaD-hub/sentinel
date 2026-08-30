import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BrainCircuit } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import { detectionApi } from '../api/detectionApi';
import { explanationApi } from '../api/explanationApi';
import { LoadingState, ErrorState, EmptyState, BackendOfflineState } from '../components/StateComponents';
import { cn } from '../utils/cn';

const SHAP_COLORS = ['#ef4444', '#f59e0b', '#22d3ee', '#3399ff', '#22c55e', '#a5f3fc', '#fbbf24'];

export function ExplainableAIPage() {
  const [selectedDetection, setSelectedDetection] = useState('');
  const [page, setPage] = useState(1);

  const resultsQuery = useQuery({ queryKey: ['detection', 'results', page], queryFn: () => detectionApi.results(page, 50) });
  const explanationQuery = useQuery({
    queryKey: ['explanation', selectedDetection],
    queryFn: () => explanationApi.get(selectedDetection),
    enabled: !!selectedDetection,
  });

  if (resultsQuery.isError && (resultsQuery.error as { type?: string })?.type === 'network') {
    return <BackendOfflineState />;
  }

  const detections = resultsQuery.data?.items || [];
  const explanation = explanationQuery.data;

  const shapData = explanation
    ? Object.entries(explanation.values)
        .map(([name, value]) => ({ name, value: Number(value) }))
        .sort((a, b) => Math.abs(b.value) - Math.abs(a.value))
        .slice(0, 15)
    : [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold text-navy-50">Explainable AI</h1>
        <p className="text-sm text-navy-400">SHAP-based feature attribution for detection results</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="glass-panel p-5 lg:col-span-1">
          <h3 className="mb-4 font-display text-sm font-semibold text-navy-100">Select Detection</h3>
          {resultsQuery.isLoading ? (
            <LoadingState title="Loading detections..." />
          ) : detections.length > 0 ? (
            <div className="space-y-2">
              {detections.map((det) => (
                <button
                  key={det.id}
                  onClick={() => setSelectedDetection(det.id)}
                  className={cn(
                    'w-full rounded-lg border p-3 text-left transition-colors',
                    selectedDetection === det.id
                      ? 'border-cyber-500/40 bg-cyber-500/10'
                      : 'border-navy-700 bg-navy-900/40 hover:border-navy-600 hover:bg-navy-800/40'
                  )}
                >
                  <div className="flex items-center justify-between">
                    <span className="font-mono text-xs text-navy-100">{det.label}</span>
                    <span className="font-mono text-xs text-navy-400">{(det.confidence * 100).toFixed(0)}%</span>
                  </div>
                  <p className="mt-1 font-mono text-xs text-navy-400">{det.id}</p>
                </button>
              ))}
              <div className="flex gap-2 pt-2">
                <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page <= 1} className="btn-secondary text-xs">Prev</button>
                <button onClick={() => setPage((p) => p + 1)} disabled={detections.length < 50} className="btn-secondary text-xs">Next</button>
              </div>
            </div>
          ) : (
            <EmptyState title="No detections" message="No detection results available for explanation." />
          )}
        </div>

        <div className="glass-panel p-5 lg:col-span-2">
          <h3 className="mb-4 font-display text-sm font-semibold text-navy-100">SHAP Feature Contributions</h3>
          {!selectedDetection ? (
            <EmptyState title="No detection selected" message="Select a detection from the list to view its SHAP explanation." />
          ) : explanationQuery.isLoading ? (
            <LoadingState title="Loading explanation..." />
          ) : explanationQuery.isError ? (
            <ErrorState
              title="Explanation unavailable"
              message={(explanationQuery.error as { message?: string })?.message || 'No SHAP explanation exists for this detection.'}
            />
          ) : explanation && shapData.length > 0 ? (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <BrainCircuit className="h-4 w-4 text-cyber-400" />
                <span className="text-sm text-navy-300">Method: <span className="font-mono text-navy-100">{explanation.method}</span></span>
              </div>
              <ResponsiveContainer width="100%" height={350}>
                <BarChart data={shapData} layout="vertical" margin={{ left: 80 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e3560" />
                  <XAxis type="number" stroke="#7a99c9" fontSize={11} />
                  <YAxis type="category" dataKey="name" stroke="#7a99c9" fontSize={11} width={100} />
                  <Tooltip contentStyle={{ background: '#0f1c38', border: '1px solid #1e3560', borderRadius: '8px' }} />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {shapData.map((_, i) => (
                      <Cell key={i} fill={SHAP_COLORS[i % SHAP_COLORS.length]} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <EmptyState title="No SHAP values" message="This detection has no stored SHAP explanation." />
          )}
        </div>
      </div>
    </div>
  );
}
