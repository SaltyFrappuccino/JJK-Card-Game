import { useEffect, useRef } from 'react';
import { createWS } from '../services/ws';
import useGameStore from '../store/gameStore';
import { useNavigate } from 'react-router-dom';

export const useWS = () => {
  const { lobby, player, game, setLobby, setGame, setError } = useGameStore();
  const wsRef = useRef<WebSocket | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!lobby?.id || !player.id) return;
    const ws = createWS(lobby.id, player.id);
    wsRef.current = ws;

    ws.onmessage = (e) => {
      const { type, payload } = JSON.parse(e.data);
      if (type === 'lobby_update') setLobby(payload);
      if (type === 'game_state') {
        setGame(payload);
        if (payload.game_state === 'IN_GAME') {
          navigate(`/game/${payload.game_id}`);
        }
      }
      if (type === 'error') setError(payload);
    };

    ws.onerror = () => setError('WebSocket error');

    return () => {
      ws.close();
    };
  }, [lobby?.id, player.id]);

  const send = (type: string, payload: any) => {
    if (wsRef.current?.readyState === 1) {
      wsRef.current.send(JSON.stringify({ type, payload }));
    }
  };

  const emitPlayCard = (cardId: string, targetId?: string, targetsIds?: string[]) => {
    const gameId = game?.game_id;
    if (gameId) {
      send('play_card', { game_id: gameId, card_id: cardId, target_id: targetId, targets_ids: targetsIds });
    }
  };

  const emitEndTurn = () => {
    const gameId = game?.game_id;
    if (gameId) {
      send('end_turn', { game_id: gameId });
    }
  };

  const emitDiscardCards = (cardIds: string[]) => {
    const gameId = game?.game_id;
    if (gameId) {
      send('discard_cards', { game_id: gameId, card_ids: cardIds });
    }
  };

  const emitAddDummy = () => {
    const gameId = game?.game_id;
    if (gameId) {
      send('add_dummy', { game_id: gameId });
    }
  };

  const emitRemoveDummy = (dummyId: string) => {
    const gameId = game?.game_id;
    if (gameId) {
      send('remove_dummy', { game_id: gameId, dummy_id: dummyId });
    }
  };

  return { send, emitPlayCard, emitEndTurn, emitDiscardCards, emitAddDummy, emitRemoveDummy };
}; 