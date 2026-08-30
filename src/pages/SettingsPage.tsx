import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { User, Shield, BrainCircuit, Radio, Bell, Bot, BookOpen, Atom } from 'lucide-react';
import { settingsApi } from '../api/settingsApi';
import { useAuthStore } from '../store/authStore';
import { BackendOfflineState } from '../components/StateComponents';
import { cn } from '../utils/cn';

const SECTIONS = [
  { id: 'account', label: 'Account', icon: User },
  { id: 'security', label: 'Security', icon: Shield },
  { id: 'detection', label: 'Detection', icon: BrainCircuit },
  { id: 'capture', label: 'Capture', icon: Radio },
  { id: 'notifications', label: 'Notifications', icon: Bell },
  { id: 'ai', label: 'AI', icon: Bot },
  { id: 'rag', label: 'RAG', icon: BookOpen },
  { id: 'quantum', label: 'Quantum', icon: Atom },
];

export function SettingsPage() {
  const [activeSection, setActiveSection] = useState('account');
  const systemQuery = useQuery({ queryKey: ['system', 'status'], queryFn: settingsApi.systemStatus, refetchInterval: 30000 });
  const { user, hasPermission } = useAuthStore();

  if (systemQuery.isError && (systemQuery.error as { type?: string })?.type === 'network') {
    return <BackendOfflineState />;
  }

  const system = systemQuery.data;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-bold text-navy-50">Settings</h1>
        <p className="text-sm text-navy-400">System configuration and preferences</p>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-4">
        <div className="glass-panel p-3 lg:col-span-1">
          <nav className="space-y-1">
            {SECTIONS.map((section) => {
              const Icon = section.icon;
              const active = activeSection === section.id;
              return (
                <button
                  key={section.id}
                  onClick={() => setActiveSection(section.id)}
                  className={cn('nav-link w-full', active && 'nav-link-active')}
                >
                  <Icon className="h-4 w-4" />
                  <span className="text-sm">{section.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        <div className="glass-panel p-5 lg:col-span-3">
          {activeSection === 'account' && (
            <div className="space-y-4">
              <h3 className="font-display text-sm font-semibold text-navy-100">Account Information</h3>
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div>
                  <label className="text-xs text-navy-400">Email</label>
                  <p className="mt-1 font-mono text-sm text-navy-100">{user?.email}</p>
                </div>
                <div>
                  <label className="text-xs text-navy-400">Full Name</label>
                  <p className="mt-1 text-sm text-navy-100">{user?.full_name || 'Not set'}</p>
                </div>
                <div>
                  <label className="text-xs text-navy-400">Role</label>
                  <p className="mt-1 font-mono text-sm text-cyber-400 uppercase">{user?.role}</p>
                </div>
                <div>
                  <label className="text-xs text-navy-400">Verified</label>
                  <p className="mt-1 text-sm text-navy-100">{user?.is_verified ? 'Yes' : 'No'}</p>
                </div>
              </div>
            </div>
          )}

          {activeSection === 'security' && (
            <div className="space-y-4">
              <h3 className="font-display text-sm font-semibold text-navy-100">Security Configuration</h3>
              <div className="space-y-3">
                <div className="glass-card p-3">
                  <p className="text-xs text-navy-400">Database Configured</p>
                  <p className="font-mono text-sm text-navy-100">{system?.database_configured ? 'Yes' : 'No'}</p>
                </div>
                <div className="glass-card p-3">
                  <p className="text-xs text-navy-400">Redis Configured</p>
                  <p className="font-mono text-sm text-navy-100">{system?.redis_configured ? 'Yes' : 'No'}</p>
                </div>
                <div className="glass-card p-3">
                  <p className="text-xs text-navy-400">API Status</p>
                  <p className="font-mono text-sm text-success-400">{system?.api ? 'Online' : 'Offline'}</p>
                </div>
              </div>
              <p className="text-xs text-navy-400">Secret keys, private keys, passwords, and database credentials are never exposed in the frontend.</p>
            </div>
          )}

          {activeSection === 'detection' && (
            <div className="space-y-4">
              <h3 className="font-display text-sm font-semibold text-navy-100">Detection Configuration</h3>
              <div className="glass-card p-3">
                <p className="text-xs text-navy-400">Model Directory</p>
                <p className="font-mono text-sm text-navy-100">{system?.model_directory || 'Not configured'}</p>
              </div>
              <p className="text-sm text-navy-300">Detection uses an Autoencoder for anomaly detection and XGBoost for attack classification. Models must be trained before detection can run.</p>
            </div>
          )}

          {activeSection === 'capture' && (
            <div className="space-y-4">
              <h3 className="font-display text-sm font-semibold text-navy-100">Packet Capture Configuration</h3>
              <p className="text-sm text-navy-300">Packet capture uses the Scapy library and requires local network interface permissions. Capture availability depends on the runtime environment.</p>
              <p className="text-xs text-navy-400">You {hasPermission('capture:start') ? 'can' : 'cannot'} start/stop captures with your current role.</p>
            </div>
          )}

          {activeSection === 'notifications' && (
            <div className="space-y-4">
              <h3 className="font-display text-sm font-semibold text-navy-100">Notification Preferences</h3>
              <p className="text-sm text-navy-300">Real-time notifications are delivered via WebSocket. You will receive alerts for new detections, alert creation, capture status changes, and quantum events.</p>
            </div>
          )}

          {activeSection === 'ai' && (
            <div className="space-y-4">
              <h3 className="font-display text-sm font-semibold text-navy-100">AI Configuration</h3>
              <p className="text-sm text-navy-300">The AI assistant uses a configurable LLM provider. The backend must have LLM_PROVIDER, LLM_MODEL, and LLM_API_KEY set in the environment.</p>
              <p className="text-xs text-navy-400">API keys are never exposed in the frontend.</p>
            </div>
          )}

          {activeSection === 'rag' && (
            <div className="space-y-4">
              <h3 className="font-display text-sm font-semibold text-navy-100">RAG Configuration</h3>
              <p className="text-sm text-navy-300">The RAG knowledge base uses sentence-transformer embeddings for semantic search. Documents are chunked, embedded, and indexed for retrieval.</p>
              <p className="text-xs text-navy-400">Ingest threat intelligence documents (MITRE ATT&CK, CVE, OWASP) via the Threat Intelligence page.</p>
            </div>
          )}

          {activeSection === 'quantum' && (
            <div className="space-y-4">
              <h3 className="font-display text-sm font-semibold text-navy-100">Quantum Security Configuration</h3>
              <p className="text-sm text-navy-300">Post-quantum key establishment uses the Kyber KEM. Alert payloads are encrypted with AES-256-GCM using the shared secret derived from Kyber.</p>
              <p className="text-xs text-navy-400">The Kyber variant and cryptographic operations are managed by the backend. No private keys are exposed to the frontend.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
