import { create } from 'zustand';
import type { WsConnectionState } from '../api/types';

interface WsState {
  connectionState: WsConnectionState;
  lastEvent: string | null;
  setConnectionState: (state: WsConnectionState) => void;
  setLastEvent: (event: string) => void;
}

export const useWsStore = create<WsState>((set) => ({
  connectionState: 'disconnected',
  lastEvent: null,
  setConnectionState: (connectionState) => set({ connectionState }),
  setLastEvent: (event) => set({ lastEvent: event }),
}));
