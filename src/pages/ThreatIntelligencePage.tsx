import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { BookOpen, Search, Loader2, FileText, Database } from 'lucide-react';
import { threatIntelApi, ragApi } from '../api/ragApi';
import { LoadingState, ErrorState, EmptyState, BackendOfflineState, RAGUnavailable } from '../components/StateComponents';


export function ThreatIntelligencePage() {
  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');

  const statusQuery = useQuery({ queryKey: ['threat-intel', 'status'], queryFn: threatIntelApi.status });
  const ragStatusQuery = useQuery({ queryKey: ['rag', 'status'], queryFn: ragApi.status });
  const searchQuery = useQuery({
    queryKey: ['rag', 'search', submittedQuery],
    queryFn: () => ragApi.search({ query: submittedQuery, top_k: 10 }),
    enabled: !!submittedQuery,
  });

  if (statusQuery.isError && (statusQuery.error as { type?: string })?.type === 'network') {
    return <BackendOfflineState />;
  }

  const status = statusQuery.data;
  const ragStatus = ragStatusQuery.data;
  const searchResults = searchQuery.data;

  const isRagAvailable = status?.available && ragStatus?.available;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      setSubmittedQuery(query.trim());
    }
  };

  if (!isRagAvailable && status && !status.available) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="font-display text-2xl font-bold text-navy-50">Threat Intelligence</h1>
          <p className="text-sm text-navy-400">RAG-powered MITRE ATT&CK, CVE, and OWASP knowledge base</p>
        </div>
        <RAGUnavailable />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold text-navy-50">Threat Intelligence</h1>
        <p className="text-sm text-navy-400">RAG-powered MITRE ATT&CK, CVE, and OWASP knowledge base</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <div className="glass-card p-4">
          <div className="flex items-center gap-2 text-navy-400">
            <Database className="h-4 w-4" />
            <span className="text-xs uppercase tracking-wider">RAG Status</span>
          </div>
          <p className={`mt-2 font-display text-lg font-bold ${isRagAvailable ? 'text-success-400' : 'text-warning-500'}`}>
            {isRagAvailable ? 'Available' : 'Unavailable'}
          </p>
        </div>
        <div className="glass-card p-4">
          <div className="flex items-center gap-2 text-navy-400">
            <FileText className="h-4 w-4" />
            <span className="text-xs uppercase tracking-wider">Documents</span>
          </div>
          <p className="mt-2 font-display text-lg font-bold text-cyber-400">{status?.documents ?? 0}</p>
        </div>
        <div className="glass-card p-4">
          <div className="flex items-center gap-2 text-navy-400">
            <BookOpen className="h-4 w-4" />
            <span className="text-xs uppercase tracking-wider">Chunks Indexed</span>
          </div>
          <p className="mt-2 font-display text-lg font-bold text-cyan-400">{ragStatus?.chunks_indexed ?? 0}</p>
        </div>
      </div>

      {ragStatus && ragStatus.ingested_sources.length > 0 && (
        <div className="glass-panel p-5">
          <h3 className="mb-3 font-display text-sm font-semibold text-navy-100">Ingested Sources</h3>
          <div className="flex flex-wrap gap-2">
            {ragStatus.ingested_sources.map((src) => (
              <span key={src} className="badge border-cyber-500/30 bg-cyber-500/10 text-cyber-400">{src}</span>
            ))}
          </div>
        </div>
      )}

      <div className="glass-panel p-5">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-navy-400" />
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search threat intelligence (MITRE techniques, CVEs, OWASP categories)..."
              className="input-field pl-10"
            />
          </div>
          <button type="submit" disabled={!query.trim() || searchQuery.isPending} className="btn-primary flex items-center gap-2">
            {searchQuery.isPending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
            Search
          </button>
        </form>
      </div>

      {submittedQuery && (
        <div className="glass-panel p-5">
          <h3 className="mb-4 font-display text-sm font-semibold text-navy-100">Search Results for "{submittedQuery}"</h3>
          {searchQuery.isLoading ? (
            <LoadingState title="Searching knowledge base..." />
          ) : searchQuery.isError ? (
            <ErrorState title="Search failed" message={(searchQuery.error as { message?: string })?.message} />
          ) : searchResults && searchResults.available && searchResults.results.length > 0 ? (
            <div className="space-y-3">
              {searchResults.results.map((result, i) => (
                <div key={i} className="glass-card p-4">
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <span className="badge border-cyber-500/30 bg-cyber-500/10 text-cyber-400">{result.source}</span>
                        <span className="font-mono text-xs text-navy-400">{result.external_id}</span>
                        <span className="font-mono text-xs text-navy-400">Score: {(result.score * 100).toFixed(1)}%</span>
                      </div>
                      <p className="mt-2 text-sm text-navy-100">{result.chunk_text}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : searchResults && !searchResults.available ? (
            <RAGUnavailable />
          ) : (
            <EmptyState title="No results" message="No matching threat intelligence entries found. Try a different query." />
          )}
        </div>
      )}
    </div>
  );
}
