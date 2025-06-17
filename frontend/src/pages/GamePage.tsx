import React, { useState, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import useGameStore from '../store/gameStore';
import { useWS } from '../hooks/useSocket';
import PlayerPod from '../components/PlayerPod';
import { Card } from '../components/Card';
import type { Card as CardType } from '../types';

const getMultiTargetCount = (card: CardType): number | null => {
  if (card.id === 'jogo_ember_insects') {
    return 3;
  }
  return null;
};

const GamePage: React.FC = () => {
  const { game, player: self, reset: resetGame } = useGameStore();
  const { emitPlayCard, emitEndTurn, emitDiscardCards, emitAddDummy, emitRemoveDummy } = useWS();
  const navigate = useNavigate();

  const [selectedCard, setSelectedCard] = useState<CardType | null>(null);
  const [targeting, setTargeting] = useState(false);
  const [discardMode, setDiscardMode] = useState(false);
  const [discardSelection, setDiscardSelection] = useState<CardType[]>([]);
  const [multiTargetSelection, setMultiTargetSelection] = useState<string[]>([]);

  const multiTargetCount = useMemo(() => selectedCard ? getMultiTargetCount(selectedCard) : null, [selectedCard]);
  const currentPlayer = useMemo(() => game ? game.players[game.current_turn_player_index] : null, [game]);
  const selfPlayer = useMemo(() => game?.players.find(p => p.id === self?.id), [game, self]);
  const hasDiscardedThisRound = selfPlayer && game ? selfPlayer.last_discard_round === game.round_number : false;
  const isMyTurn = useMemo(() => currentPlayer?.id === selfPlayer?.id, [currentPlayer, selfPlayer]);

  const handleCardClick = React.useCallback((card: CardType) => {
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
      setMultiTargetSelection([]);
    } else {
      setSelectedCard(card);
      setTargeting(true);
      setMultiTargetSelection([]);
    }
  }, [discardMode, isMyTurn, selfPlayer, selectedCard, discardSelection]);

  React.useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (!isMyTurn || !selfPlayer) return;

      const key = event.key;
      let cardIndex = -1;

      if (key >= '1' && key <= '9') {
        cardIndex = parseInt(key) - 1;
      } else if (key === '0') {
        cardIndex = 9;
      }

      if (cardIndex !== -1 && selfPlayer.hand.length > cardIndex) {
        const cardToPlay = selfPlayer.hand[cardIndex];
        // Check if playable before triggering the click
        if ((selfPlayer.energy ?? 0) >= cardToPlay.cost) {
          handleCardClick(cardToPlay);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => {
      window.removeEventListener('keydown', handleKeyDown);
    };
  }, [isMyTurn, selfPlayer, handleCardClick]);

  const handlePlayerSelect = (targetId: string, event?: React.MouseEvent) => {
    if (!selectedCard || !selfPlayer?.id) return;

    // If it's a multi-target card
    if (multiTargetCount) {
      if (event?.type === 'contextmenu') {
        event.preventDefault();
        const newSelection = [...multiTargetSelection];
        const indexToRemove = newSelection.lastIndexOf(targetId);
        if (indexToRemove > -1) {
          newSelection.splice(indexToRemove, 1);
          setMultiTargetSelection(newSelection);
        }
        return;
      }

      if (multiTargetSelection.length < multiTargetCount) {
        const newSelection = [...multiTargetSelection, targetId];
        setMultiTargetSelection(newSelection);

        if (newSelection.length === multiTargetCount) {
          // Auto-confirm when max targets are selected
          emitPlayCard(selectedCard.id, undefined, newSelection);
          setSelectedCard(null);
          setTargeting(false);
          setMultiTargetSelection([]);
        }
      }
    } else { // If it's a single-target card
      emitPlayCard(selectedCard.id, targetId);
      setSelectedCard(null);
      setTargeting(false);
    }
  };

  const confirmMultiTarget = () => {
    if (!selectedCard || multiTargetSelection.length === 0) return;
    
    emitPlayCard(selectedCard.id, undefined, multiTargetSelection);
    setSelectedCard(null);
    setTargeting(false);
    setMultiTargetSelection([]);
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
    emitDiscardCards(discardSelection.map(c=>c.id));
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
        <h1>Игра окончена</h1>
        <h2>{winner ? `${winner.nickname} — победитель!` : 'Ничья!'}</h2>
        <button onClick={handleReturnToMenu}>Вернуться в главное меню</button>
      </div>
    );
  }
  
  const viewerIsGojo = selfPlayer?.character?.id === 'gojo_satoru';

  // Reorder players so that selfPlayer is at the bottom center
  const playerOrder = [...game.players];
  const selfIndex = playerOrder.findIndex(p => p.id === selfPlayer.id);
  const orderedPlayers = selfIndex !== -1 ? [...playerOrder.slice(selfIndex), ...playerOrder.slice(0, selfIndex)] : playerOrder;

  return (
    <div className="game-page">
      <div className="turn-indicator">Ход: {currentPlayer?.nickname}</div>
      {targeting && multiTargetCount && (
        <div className="targeting-indicator">
            Выберите целей: {multiTargetSelection.length} / {multiTargetCount}
            <br />
            (ПКМ для отмены выбора)
            {multiTargetSelection.length > 0 && (
              <button onClick={confirmMultiTarget} style={{marginLeft: '10px'}}>Подтвердить</button>
            )}
        </div>
      )}
      <div className="game-board">
        <div className="player-pods-container">
          {orderedPlayers.filter(p=> p.id !== selfPlayer.id).map(p => (
            <PlayerPod 
              key={p.id} 
              player={p} 
              isCurrent={p.id === currentPlayer?.id}
              isTargetable={targeting}
              onSelect={(targetId, event) => handlePlayerSelect(targetId, event)}
              viewerIsGojo={viewerIsGojo}
              isTraining={game.is_training}
              onRemoveDummy={emitRemoveDummy}
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
           <PlayerPod player={selfPlayer} isCurrent={isMyTurn} isTargetable={targeting} onSelect={(targetId, event) => handlePlayerSelect(targetId, event)} isSelf={true} onEndTurn={handleEndTurn} viewerIsGojo={viewerIsGojo} />
        </div>
        <div className="player-hand">
          {selfPlayer.hand.map((card, i) => (
            <Card 
              key={`${card.id}-${i}`} 
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
          {game.is_training && (
            <div className="training-controls">
              <button onClick={() => emitAddDummy()}>Добавить манекен</button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default GamePage; 