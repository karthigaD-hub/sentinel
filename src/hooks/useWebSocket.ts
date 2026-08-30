import { useEffect, useRef, useCallback } from 'react';
import { useWsStore } from '../store/wsStore';
import { useAuthStore } from '../store/authStore';
import { buildWsUrl } from '../api/config';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import type { WsEvent } from '../api/types';

const RECONNECT_DELAYS = [1000, 2000, 4000, 8000, 15000, 30000];

export function useWebSocket() {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectAttemptRef = useRef(0);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const setConnectionState = useWsStore((s) => s.setConnectionState);
  const setLastEvent = useWsStore((s) => s.setLastEvent);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const queryClient = useQueryClient();

  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const parsed: WsEvent = JSON.parse(event.data);
      setLastEvent(parsed.event);

      switch (parsed.event) {
        case 'packet_received':
          queryClient.invalidateQueries({ queryKey: ['capture', 'status'] });
          queryClient.invalidateQueries({ queryKey: ['capture', 'statistics'] });
          queryClient.invalidateQueries({ queryKey: ['capture', 'packets'] });
          break;
        case 'capture_started':
          queryClient.invalidateQueries({ queryKey: ['capture', 'status'] });
          queryClient.invalidateQueries({ queryKey: ['detection', 'status'] });
          toast.success('Packet capture started');
          break;
        case 'capture_stopped':
          queryClient.invalidateQueries({ queryKey: ['capture', 'status'] });
          queryClient.invalidateQueries({ queryKey: ['detection', 'status'] });
          toast.info('Packet capture stopped');
          break;
        case 'detection_created':
          queryClient.invalidateQueries({ queryKey: ['detection', 'results'] });
          queryClient.invalidateQueries({ queryKey: ['detection', 'statistics'] });
          queryClient.invalidateQueries({ queryKey: ['dashboard'] });
          toast.warning('New threat detected');
          break;
        case 'alert_created':
          queryClient.invalidateQueries({ queryKey: ['alerts'] });
          queryClient.invalidateQueries({ queryKey: ['dashboard'] });
          toast.error('Security alert created');
          break;
        case 'alert_updated':
          queryClient.invalidateQueries({ queryKey: ['alerts'] });
          break;
        case 'model_status':
          queryClient.invalidateQueries({ queryKey: ['detection', 'model'] });
          break;
        case 'system_status':
          queryClient.invalidateQueries({ queryKey: ['system'] });
          break;
        case 'quantum_event':
          queryClient.invalidateQueries({ queryKey: ['quantum'] });
          break;
      }
    } catch {
      // ignore malformed messages
    }
  }, [queryClient, setLastEvent]);

  const connect = useCallback(() => {
    const token = localStorage.getItem('qsentinel_access_token');
    if (!token) return;

    try {
      const ws = new WebSocket(buildWsUrl(token));
      wsRef.current = ws;

      ws.onopen = () => {
        reconnectAttemptRef.current = 0;
        setConnectionState('connected');
      };

      ws.onmessage = handleMessage;

      ws.onclose = () => {
        setConnectionState('disconnected');
        wsRef.current = null;
        scheduleReconnect();
      };

      ws.onerror = () => {
        setConnectionState('reconnecting');
      };
    } catch {
      scheduleReconnect();
    }
  }, [setConnectionState, handleMessage]);

  const scheduleReconnect = useCallback(() => {
    if (reconnectTimerRef.current) return;
    const delay = RECONNECT_DELAYS[Math.min(reconnectAttemptRef.current, RECONNECT_DELAYS.length - 1)];
    reconnectAttemptRef.current++;
    setConnectionState('reconnecting');
    reconnectTimerRef.current = setTimeout(() => {
      reconnectTimerRef.current = null;
      connect();
    }, delay);
  }, [connect, setConnectionState]);

  useEffect(() => {
    if (!isAuthenticated) {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      setConnectionState('disconnected');
      return;
    }
    connect();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
    };
  }, [isAuthenticated, connect, setConnectionState]);

  return wsRef;
}
