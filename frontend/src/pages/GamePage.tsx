import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import useGameStore from '../store/gameStore';
import { useWS } from '../hooks/useSocket';
import PlayerPod from '../components/PlayerPod';
import CardComponent from '../components/Card';
import type { Card } from '../types';

const GamePage: React.FC = () => {
  const { game, player: self, reset: resetGame } = useGameStore();
  const { emitPlayCard, emitEndTurn, emitDiscardCards } = useWS();
  const navigate = useNavigate();

  const [selectedCard, setSelectedCard] = useState<Card | null>(null);
  const [targeting, setTargeting] = useState(false);
  const [discardMode, setDiscardMode] = useState(false);
  const [discardSelection, setDiscardSelection] = useState<Card[]>([]);

  const currentPlayer = useMemo(() => game ? game.players[game.current_turn_player_index] : null, [game]);
  const selfPlayer = useMemo(() => game?.players.find(p => p.id === self?.id), [game, self]);
  const hasDiscardedThisRound = selfPlayer && game ? selfPlayer.last_discard_round === game.round_number : false;

  const handleCardClick = (card: Card) => {
    if (discardMode) {
      const exists = discardSelection.includes(card);
      let updated = exists ? discardSelection.filter(c=>c!==card) : [...discardSelection, card];
      if (updated.length > 2) updated = updated.slice(1);
      setDiscardSelection(updated);
      return;
    }
    if (!isMyTurn) return;
    const selfEnergy = selfPlayer?.energy ?? 0;
    if (selfEnergy < card.cost) {
      return;
    }
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

  const handleToggleDiscardMode = () => {
    if (!isMyTurn) return;
    if (discardMode) {
      setDiscardMode(false);
      setDiscardSelection([]);
    } else {
      setSelectedCard(null);
      setTargeting(false);
      setDiscardMode(true);
    }
  };

  const handleConfirmDiscard = () => {
    if (discardSelection.length === 0) return;
    emitDiscardCards(discardSelection.map(c=>c.name));
    setDiscardMode(false);
    setDiscardSelection([]);
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
  const viewerIsGojo = selfPlayer?.character?.name === 'Сатору Годзё';

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
              viewerIsGojo={viewerIsGojo}
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
           <PlayerPod player={selfPlayer} isCurrent={isMyTurn} isTargetable={targeting} onSelect={handlePlayerSelect} isSelf={true} onEndTurn={handleEndTurn} viewerIsGojo={viewerIsGojo} />
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
              className={discardSelection.includes(card) ? 'discard-selected' : undefined}
            />
          ))}
        </div>
        <div className="game-controls">
          <div className="deck-info">
            Deck: {selfPlayer.deck.length} | Discard: {selfPlayer.discard_pile.length}
          </div>
          {isMyTurn && (
            <div className="discard-controls">
              {!discardMode && <button onClick={handleToggleDiscardMode} disabled={hasDiscardedThisRound}>Сбросить карты</button>}
              {discardMode && (
                <div style={{display:'flex',gap:'8px'}}>
                  <button onClick={handleConfirmDiscard} disabled={discardSelection.length===0}>Сбросить {discardSelection.length}</button>
                  <button onClick={handleToggleDiscardMode}>Отмена</button>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GamePage; 