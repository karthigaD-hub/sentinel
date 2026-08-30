import { ShieldCheck, Brain, BookOpen, Bot, Atom, Radio, Server, Database, Wifi } from 'lucide-react';

const ARCHITECTURE = [
  { category: 'AI', detail: 'Autoencoder + XGBoost', icon: Brain },
  { category: 'Explainability', detail: 'SHAP', icon: Brain },
  { category: 'Knowledge', detail: 'RAG + MITRE ATT&CK + CVE + OWASP', icon: BookOpen },
  { category: 'LLM', detail: 'Configurable LLM', icon: Bot },
  { category: 'Security', detail: 'Kyber KEM + AES-GCM', icon: Atom },
  { category: 'Network', detail: 'Scapy', icon: Radio },
  { category: 'Backend', detail: 'FastAPI', icon: Server },
  { category: 'Database', detail: 'PostgreSQL', icon: Database },
  { category: 'Realtime', detail: 'WebSocket', icon: Wifi },
];

export function AboutPage() {
  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <ShieldCheck className="h-8 w-8 text-cyber-400 text-glow" />
        <div>
          <h1 className="font-display text-2xl font-bold text-navy-50">Q-Sentinel</h1>
          <p className="text-sm text-navy-400">AI-Powered Zero-Day Cyber Defense with Post-Quantum Security</p>
        </div>
      </div>

      <div className="glass-panel p-6">
        <h2 className="mb-3 font-display text-lg font-semibold text-navy-100">Overview</h2>
        <p className="text-sm leading-relaxed text-navy-300">
          Q-Sentinel is a security operations platform that combines machine learning anomaly detection,
          post-quantum cryptography, and retrieval-augmented generation to detect, explain, and securely
          communicate cyber threats. The system captures live network traffic, extracts flow features,
          runs them through an Autoencoder and XGBoost pipeline, explains detections with SHAP values,
          and encrypts alerts using Kyber key establishment and AES-GCM.
        </p>
      </div>

      <div className="glass-panel p-6">
        <h2 className="mb-4 font-display text-lg font-semibold text-navy-100">Architecture</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {ARCHITECTURE.map((item) => {
            const Icon = item.icon;
            return (
              <div key={item.category} className="glass-card flex items-center gap-3 p-4">
                <div className="rounded-lg bg-cyber-500/10 p-2.5">
                  <Icon className="h-5 w-5 text-cyber-400" />
                </div>
                <div>
                  <p className="text-xs uppercase tracking-wider text-navy-400">{item.category}</p>
                  <p className="font-mono text-sm text-navy-100">{item.detail}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="glass-panel p-6">
        <h2 className="mb-3 font-display text-lg font-semibold text-navy-100">Detection Pipeline</h2>
        <div className="space-y-2 text-sm text-navy-300">
          <p>1. <span className="text-cyber-400">Packet Capture</span> — Scapy captures live network packets from a local interface.</p>
          <p>2. <span className="text-cyber-400">Flow Features</span> — Packet metadata is aggregated into network flow features.</p>
          <p>3. <span className="text-cyber-400">Autoencoder</span> — Anomaly detection identifies deviations from learned normal traffic patterns.</p>
          <p>4. <span className="text-cyber-400">XGBoost</span> — Attack classification identifies the specific attack type.</p>
          <p>5. <span className="text-cyber-400">SHAP Explanation</span> — Feature attributions explain why a detection was made.</p>
          <p>6. <span className="text-cyber-400">RAG Intelligence</span> — Retrieved context from MITRE, CVE, and OWASP knowledge bases enriches analysis.</p>
          <p>7. <span className="text-cyber-400">LLM Assistant</span> — A configurable LLM answers security questions using retrieved evidence.</p>
          <p>8. <span className="text-cyber-400">Kyber + AES-GCM</span> — Alerts are encrypted with post-quantum key establishment.</p>
          <p>9. <span className="text-cyber-400">WebSocket</span> — Real-time events are pushed to connected dashboard clients.</p>
        </div>
      </div>
    </div>
  );
}
