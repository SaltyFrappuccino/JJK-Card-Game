import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import useGameStore from '../store/gameStore';
import { useWS } from '../hooks/useSocket';
import PlayerPod from '../components/PlayerPod';
import CardComponent from '../components/Card';
import type { Card, Player } from '../types';

const GamePage: React.FC = () => {
  const { game, player: self, reset: resetGame } = useGameStore();
  const { emitPlayCard, emitEndTurn } = useWS();
  const navigate = useNavigate();

  const [selectedCard, setSelectedCard] = useState<Card | null>(null);
  const [targeting, setTargeting] = useState(false);

  const currentPlayer = useMemo(() => game ? game.players[game.current_turn_player_index] : null, [game]);
  const selfPlayer = useMemo(() => game?.players.find(p => p.id === self?.id), [game, self]);

  const handleCardClick = (card: Card) => {
    if (selectedCard === card) {
      // Deselect on second click
      setSelectedCard(null);
      setTargeting(false);
    } else {
      setSelectedCard(card);
      setTargeting(true);
    }
  };
  
  const handlePlayerSelect = (targetId: string) => {
    if (selectedCard && selfPlayer?.id) {
      emitPlayCard(selectedCard.name, targetId);
      setSelectedCard(null);
      setTargeting(false);
    }
  };

  const handleEndTurn = () => {
    emitEndTurn();
  };
  
  const handleReturnToMenu = () => {
    resetGame();
    navigate('/');
  };

  if (!game || !selfPlayer) {
    return <div>Loading game... If you are stuck here, please return to the main menu. <button onClick={handleReturnToMenu}>Menu</button></div>;
  }

  if (game.game_state === 'FINISHED') {
    const winner = game.players.find(p => p.status === 'ALIVE');
    return (
      <div className="game-over-screen">
        <h1>Game Over</h1>
        <h2>{winner ? `${winner.nickname} is the winner!` : 'It\'s a draw!'}</h2>
        <button onClick={handleReturnToMenu}>Return to Main Menu</button>
      </div>
    );
  }
  
  const isMyTurn = currentPlayer?.id === selfPlayer.id;

  // Reorder players so that selfPlayer is at the bottom center
  const playerOrder = [...game.players];
  const selfIndex = playerOrder.findIndex(p => p.id === selfPlayer.id);
  const orderedPlayers = selfIndex !== -1 ? [...playerOrder.slice(selfIndex), ...playerOrder.slice(0, selfIndex)] : playerOrder;

  return (
    <div className="game-page">
      <div className="turn-indicator">Ход: {currentPlayer?.nickname}</div>
      <div className="game-board">
        <div className="player-pods-container">
          {orderedPlayers.filter(p=> p.id !== selfPlayer.id).map(p => (
            <PlayerPod 
              key={p.id} 
              player={p} 
              isCurrent={p.id === currentPlayer?.id}
              isTargetable={targeting}
              onSelect={handlePlayerSelect}
            />
          ))}
        </div>
      </div>
      <div className="game-log">
        <h3>Game Log</h3>
        <div>
          {game.game_log.map((entry, i) => <p key={i} className="game-log-entry">{entry}</p>).reverse()}
        </div>
      </div>
      <div className="player-ui">
        <div className="own-player-pod">
           <PlayerPod player={selfPlayer} isCurrent={isMyTurn} isTargetable={targeting} onSelect={handlePlayerSelect} isSelf={true} onEndTurn={handleEndTurn} />
        </div>
        <div className="player-hand">
          {selfPlayer.hand.map((card, i) => (
            <CardComponent 
              key={`${card.name}-${i}`} 
              card={card} 
              isPlayable={isMyTurn && (selfPlayer.energy ?? 0) >= card.cost}
              onClick={() => handleCardClick(card)}
              index={i}
              total={selfPlayer.hand.length}
              isSelected={selectedCard === card}
            />
          ))}
        </div>
        <div className="game-controls">
          <div className="deck-info">
            Deck: {selfPlayer.deck.length} | Discard: {selfPlayer.discard_pile.length}
          </div>
        </div>
      </div>
    </div>
  );
};

export default GamePage; 