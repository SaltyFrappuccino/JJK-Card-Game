import axios from 'axios';
import type { LobbyInfo } from '../types';

const apiClient = axios.create({
  baseURL: 'http://185.188.182.11:8002/api',
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
  createTrainingLobby: (nickname: string) =>
    apiClient.post<LobbyJoinResponse>('/lobby/training', { nickname }),
  joinLobby: (lobbyId: string, nickname: string) => 
    apiClient.post<LobbyJoinResponse>(`/lobby/${lobbyId}/join`, { nickname }),
  selectCharacter: (lobbyId: string, playerId: string, characterId: string) =>
    apiClient.post<LobbyInfo>(`/lobby/${lobbyId}/character`, { player_id: playerId, character_id: characterId }),
  startGame: (lobbyId: string, playerId: string) =>
    apiClient.post(`/lobby/${lobbyId}/start`, { player_id: playerId }),
}; 