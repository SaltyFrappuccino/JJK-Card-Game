import { create } from 'zustand';
import type { Game, Lobby, Player } from '../types';
import type { GameState, LobbyInfo } from '../types';

interface PlayerState {
  id: string | null;
  nickname: string | null;
}

interface GameStore {
  player: PlayerState;
  lobby: LobbyInfo | null;
  game: GameState | null;
  error: string | null;
  setPlayer: (player: PlayerState) => void;
  setLobby: (lobby: LobbyInfo | null) => void;
  setGame: (game: GameState | null) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

const useGameStore = create<GameStore>((set) => ({
  player: { id: null, nickname: null },
  lobby: null,
  game: null,
  error: null,
  setPlayer: (player) => set({ player }),
  setLobby: (lobby) => set({ lobby }),
  setGame: (game) => set({ game }),
  setError: (error) => set({ error }),
  reset: () => set({
    player: { id: null, nickname: null },
    lobby: null,
    game: null,
    error: null,
  }),
}));

export default useGameStore; 