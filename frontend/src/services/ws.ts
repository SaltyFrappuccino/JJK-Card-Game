export const createWS = (lobbyId: string, playerId: string) =>
  new WebSocket(`ws://185.188.182.11:8002/ws/${lobbyId}/${playerId}`); 