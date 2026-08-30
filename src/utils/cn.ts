import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export function formatTimestamp(iso: string): string {
  try {
    return new Date(iso).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  } catch {
    return iso;
  }
}

export function formatRelativeTime(iso: string): string {
  try {
    const now = Date.now();
    const then = new Date(iso).getTime();
    const diff = Math.max(0, now - then);
    const seconds = Math.floor(diff / 1000);
    if (seconds < 60) return `${seconds}s ago`;
    const minutes = Math.floor(seconds / 60);
    if (minutes < 60) return `${minutes}m ago`;
    const hours = Math.floor(minutes / 60);
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    return `${days}d ago`;
  } catch {
    return iso;
  }
}

export function severityColor(severity: string): string {
  const s = severity.toLowerCase();
  if (s === 'critical') return 'text-danger-400 bg-danger-500/10 border-danger-500/30';
  if (s === 'high') return 'text-warning-500 bg-warning-500/10 border-warning-500/30';
  if (s === 'medium') return 'text-cyan-400 bg-cyan-500/10 border-cyan-500/30';
  if (s === 'low') return 'text-success-400 bg-success-500/10 border-success-500/30';
  return 'text-navy-300 bg-navy-700/50 border-navy-600';
}

export function statusColor(status: string): string {
  const s = status.toLowerCase();
  if (s === 'open' || s === 'new') return 'text-danger-400 bg-danger-500/10 border-danger-500/30';
  if (s === 'acknowledged') return 'text-warning-500 bg-warning-500/10 border-warning-500/30';
  if (s === 'resolved') return 'text-success-400 bg-success-500/10 border-success-500/30';
  return 'text-navy-300 bg-navy-700/50 border-navy-600';
}

export function classificationColor(classification: string): string {
  const c = classification.toUpperCase();
  if (c === 'KNOWN_ATTACK') return 'text-danger-400 bg-danger-500/10 border-danger-500/30';
  if (c === 'POTENTIAL_UNKNOWN_ANOMALY') return 'text-warning-500 bg-warning-500/10 border-warning-500/30';
  return 'text-success-400 bg-success-500/10 border-success-500/30';
}
