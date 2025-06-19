import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import useGameStore from '../store/gameStore';
import { useWS } from '../hooks/useSocket';
import { api } from '../services/api';
import { ALL_CHARACTERS } from '../assets/content';
import type { Character } from '../types';

// Import background images
import shinjukuBg1 from '../assets/backgrounds/shinjuku_background_1.png';
import shinjukuBg2 from '../assets/backgrounds/shinjuku_background_2.png';

const BACKGROUND_OPTIONS = [
  { id: 'none', name: 'Без фона', image: null },
  { id: 'shinjuku1', name: 'Синдзюку 1', image: shinjukuBg1 },
  { id: 'shinjuku2', name: 'Синдзюку 2', image: shinjukuBg2 }
];

const LobbyPage: React.FC = () => {
  useWS(); // Initialize WebSocket listeners
  const { lobby, player, selectedBackground, setLobby, setError, setSelectedBackground } = useGameStore();
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const navigate = useNavigate();

  const isHost = lobby?.host_id === player?.id;

  const handleKickPlayer = async (playerIdToKick: string) => {
    if (!lobby || !player?.id || !isHost) return;

    if (window.confirm("Вы уверены, что хотите кикнуть этого игрока?")) {
      try {
        await api.kickPlayer(lobby.id, player.id, playerIdToKick);
      } catch (error: any) {
        setError(error.response?.data?.detail || 'Не удалось кикнуть игрока.');
      }
    }
  };

  const handleCharacterSelect = async (character: Character) => {
    if (!lobby || !player?.id) return;
    
    const isTaken = lobby.players.some(p => p.character?.id === character.id);
    if (isTaken) {
      setError('This character is already taken.');
      return;
    }

    setSelectedCharacter(character);
    try {
      const { data } = await api.selectCharacter(lobby.id, player.id, character.id);
      setLobby(data);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to select character.');
    }
  };

  const handleStartGame = async () => {
    if (!lobby || !player?.id) return;
    setIsStarting(true);
    try {
      await api.startGame(lobby.id, player.id);
      // Navigation will be handled by the 'game_started' socket event in useSocket hook
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to start game.');
      setIsStarting(false);
    }
  };

  if (!lobby || !player) {
    // This could happen on a page refresh. Redirect to home.
    navigate('/');
    return null;
  }
  
  const allPlayersReady = lobby.players.every(p => p.character);
  const isTraining = lobby.is_training;

  return (
    <div className="lobby-page">
      <h2>{isTraining ? 'Тренировка' : `Лобби: ${lobby.id}`}</h2>
      {!isTraining && (
          <button className="copy-code-btn" onClick={() => navigator.clipboard.writeText(lobby.id)}>Скопировать код</button>
      )}
      
      {isHost && (
        <div className="host-controls">
          <button className="settings-btn" onClick={() => setShowSettings(!showSettings)}>
            {showSettings ? 'Скрыть настройки' : 'Настройки'}
          </button>
          
          {showSettings && (
            <div className="game-settings">
              <h3>Настройки игры</h3>
              
              <div className="setting-group">
                <label>Фон игры:</label>
                <div className="background-options">
                  {BACKGROUND_OPTIONS.map(bg => (
                    <div 
                      key={bg.id}
                      className={`background-option ${selectedBackground === bg.id ? 'selected' : ''}`}
                      onClick={() => setSelectedBackground(bg.id)}
                    >
                      {bg.image ? (
                        <img src={bg.image} alt={bg.name} className="background-preview" />
                      ) : (
                        <div className="no-background-preview">Без фона</div>
                      )}
                      <span className="background-name">{bg.name}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      )}
      
      <div className="lobby-container">
        {!isTraining && (
          <div className="players-list">
            <h3>Игроки ({lobby.players.length}/8)</h3>
            <ul>
              {lobby.players.map(p => (
                <li key={p.id}>
                  {p.nickname} {p.id === lobby.host_id ? '(Хост)' : ''}
                  {p.character ? ` - ${p.character.name}` : ' - Выбирает...'}
                  {isHost && p.id !== player.id && (
                    <button className="kick-btn" onClick={() => handleKickPlayer(p.id)}>
                      &times;
                    </button>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
        
        <div className="character-selection">
          <h3>Выберите персонажа</h3>
          <div className="character-carousel">
            {ALL_CHARACTERS.map(char => {
              const isTaken = lobby.players.some(p => p.character?.id === char.id);
              return (
                <div 
                  key={char.id} 
                  className={`character-card ${selectedCharacter?.id === char.id ? 'selected' : ''} ${isTaken ? 'taken' : ''}`}
                  onClick={() => !isTaken && handleCharacterSelect(char)}
                >
                  <h4>{char.name}</h4>
                  {/* Add character image here later */}
                </div>
              );
            })}
          </div>
        </div>

        {selectedCharacter && (
          <div className="character-details">
            <h3>{selectedCharacter.name}</h3>
            <p><strong>{selectedCharacter.passive_ability_name}</strong>: {selectedCharacter.passive_ability_description}</p>
            <h4>Уникальные карты:</h4>
            <ul>
              {selectedCharacter.unique_cards.map(card => <li key={card.id}>{card.name}</li>)}
            </ul>
          </div>
        )}
      </div>

      {isHost && (
        <button className="start-game-btn" onClick={handleStartGame} disabled={(!isTraining && !allPlayersReady) || isStarting}>
          {isStarting ? 'Запуск...' : 'Начать игру'}
        </button>
      )}
    </div>
  );
};

export default LobbyPage; 