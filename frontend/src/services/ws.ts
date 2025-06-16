export const createWS = (lobbyId: string, playerId: string) =>
  new WebSocket(`ws://localhost:8000/ws/${lobbyId}/${playerId}`); 