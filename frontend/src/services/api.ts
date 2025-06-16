import axios from 'axios';
import type { LobbyInfo } from '../types';

const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface LobbyJoinResponse {
  lobby_info: LobbyInfo;
  player_id: string;
}

export const api = {
  createLobby: (nickname: string) => 
    apiClient.post<LobbyJoinResponse>('/lobby/create', { nickname }),
  joinLobby: (lobbyId: string, nickname: string) => 
    apiClient.post<LobbyJoinResponse>(`/lobby/${lobbyId}/join`, { nickname }),
  selectCharacter: (lobbyId: string, playerId: string, characterName: string) =>
    apiClient.post<LobbyInfo>(`/lobby/${lobbyId}/character`, { player_id: playerId, character_name: characterName }),
  startGame: (lobbyId: string, playerId: string) =>
    apiClient.post(`/lobby/${lobbyId}/start`, { player_id: playerId }),
}; 