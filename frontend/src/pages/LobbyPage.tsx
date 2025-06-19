import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import useGameStore from '../store/gameStore';
import { useWS } from '../hooks/useSocket';
import { api } from '../services/api';
import { ALL_CHARACTERS } from '../assets/content';
import type { Character } from '../types';

// Import background images
import shinjukuBg1 from '../assets/backgrounds/shinjuku_background_1.png';
import shinjukuBg2 from '../assets/backgrounds/shinjuku_background_2.png';
import shibuyaBg1 from '../assets/backgrounds/shibuya 1.jpg';
import shibuyaBg2 from '../assets/backgrounds/shibuya 2.jpg';
import shibuyaFromJjk from '../assets/backgrounds/shibuya from jjk.jpg';
import shibuyaFromJjk2 from '../assets/backgrounds/shibuya from jjk 2.jpg';

const BACKGROUND_OPTIONS = [
  { id: 'none', name: 'Без фона', image: null },
  { id: 'shinjuku1', name: 'Синдзюку 1', image: shinjukuBg1 },
  { id: 'shinjuku2', name: 'Синдзюку 2', image: shinjukuBg2 },
  { id: 'shibuya1', name: 'Сибуя 1', image: shibuyaBg1 },
  { id: 'shibuya2', name: 'Сибуя 2', image: shibuyaBg2 },
  { id: 'shibuyajjk1', name: 'Сибуя JJK 1', image: shibuyaFromJjk },
  { id: 'shibuyajjk2', name: 'Сибуя JJK 2', image: shibuyaFromJjk2 }
];

const SliderSetting: React.FC<{
  label: string;
  value: number;
  min: number;
  max: number;
  unit: string;
  onChange: (value: number) => void;
  disabled?: boolean;
}> = React.memo(({ label, value, min, max, unit, onChange, disabled = false }) => {
  const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (disabled) return;
    const newValue = parseInt(e.target.value);
    onChange(newValue);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (disabled) return;
    const newValue = parseInt(e.target.value);
    if (!isNaN(newValue) && newValue >= min && newValue <= max) {
      onChange(newValue);
    }
  };

  return (
    <div className={`slider-setting ${disabled ? 'disabled' : ''}`}>
      <label>{label}</label>
      <div className="slider-container">
        <div className="slider-wrapper">
          <input
            type="range"
            min={min}
            max={max}
            value={value}
            onChange={handleSliderChange}
            className="custom-slider"
            disabled={disabled}
          />
        </div>
        <input
          type="number"
          value={value}
          onChange={handleInputChange}
          min={min}
          max={max}
          className="slider-input"
          disabled={disabled}
        />
        <span className="slider-unit">{unit}</span>
      </div>
      {disabled && <div className="disabled-overlay">Только хост может изменять настройки</div>}
    </div>
  );
});

const LobbyPage: React.FC = () => {
  useWS(); // Initialize WebSocket listeners
  const { lobby, player, selectedBackground, setLobby, setError, setSelectedBackground } = useGameStore();
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const navigate = useNavigate();

  const isHost = lobby?.host_id === player?.id;

  // Получаем настройки из лобби вместо локального состояния
  const hpPercentage = lobby?.game_settings?.hp_percentage || 100;
  const maxEnergyPercentage = lobby?.game_settings?.max_energy_percentage || 100;
  const startingEnergyPercentage = lobby?.game_settings?.starting_energy_percentage || 100;
  const currentBackground = lobby?.game_settings?.background || selectedBackground || "none";

  // Создаем callback функции для изменения настроек (только для хоста)
  const handleHpChange = useCallback(async (value: number) => {
    if (!isHost || !lobby || !player?.id) return;
    try {
      await api.updateGameSettings(lobby.id, player.id, value, maxEnergyPercentage, startingEnergyPercentage, currentBackground);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Не удалось обновить настройки.');
    }
  }, [isHost, lobby, player?.id, maxEnergyPercentage, startingEnergyPercentage, currentBackground, setError]);

  const handleMaxEnergyChange = useCallback(async (value: number) => {
    if (!isHost || !lobby || !player?.id) return;
    try {
      await api.updateGameSettings(lobby.id, player.id, hpPercentage, value, startingEnergyPercentage, currentBackground);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Не удалось обновить настройки.');
    }
  }, [isHost, lobby, player?.id, hpPercentage, startingEnergyPercentage, currentBackground, setError]);

  const handleStartingEnergyChange = useCallback(async (value: number) => {
    if (!isHost || !lobby || !player?.id) return;
    try {
      await api.updateGameSettings(lobby.id, player.id, hpPercentage, maxEnergyPercentage, value, currentBackground);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Не удалось обновить настройки.');
    }
  }, [isHost, lobby, player?.id, hpPercentage, maxEnergyPercentage, currentBackground, setError]);

  const handleBackgroundChange = useCallback(async (backgroundId: string) => {
    if (!isHost || !lobby || !player?.id) return;
    try {
      await api.updateGameSettings(lobby.id, player.id, hpPercentage, maxEnergyPercentage, startingEnergyPercentage, backgroundId);
      setSelectedBackground(backgroundId);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Не удалось обновить настройки.');
    }
  }, [isHost, lobby, player?.id, hpPercentage, maxEnergyPercentage, startingEnergyPercentage, setSelectedBackground, setError]);

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
      // Начинаем игру (настройки уже синхронизированы в реальном времени)
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

      <div className="game-settings-container">
        <button className="settings-btn" onClick={() => setShowSettings(!showSettings)}>
          {showSettings ? 'Скрыть настройки' : `${isHost ? 'Настройки' : 'Посмотреть настройки'}`}
        </button>
        
        {showSettings && (
          <div className="game-settings">
            <h3>Настройки игры {!isHost && '(только просмотр)'}</h3>
            
            <div className="setting-group">
              <label>Фон игры:</label>
              <div className={`background-options ${!isHost ? 'disabled' : ''}`}>
                {BACKGROUND_OPTIONS.map(bg => (
                  <div 
                    key={bg.id}
                    className={`background-option ${currentBackground === bg.id ? 'selected' : ''} ${!isHost ? 'disabled' : ''}`}
                    onClick={() => isHost && handleBackgroundChange(bg.id)}
                  >
                    {bg.image ? (
                      <img src={bg.image} alt={bg.name} className="background-preview" />
                    ) : (
                      <div className="no-background-preview">Без фона</div>
                    )}
                    <span className="background-name">{bg.name}</span>
                    {bg.id === currentBackground && !isHost && (
                      <div className="current-setting-indicator">Текущий</div>
                    )}
                  </div>
                ))}
              </div>
              {!isHost && <div className="setting-note">Хост выбрал: {BACKGROUND_OPTIONS.find(bg => bg.id === currentBackground)?.name || 'Без фона'}</div>}
            </div>

            <SliderSetting
              label="Процент ХП"
              value={hpPercentage}
              min={1}
              max={300}
              unit="%"
              onChange={handleHpChange}
              disabled={!isHost}
            />

            <SliderSetting
              label="Максимальный ПЭ"
              value={maxEnergyPercentage}
              min={1}
              max={300}
              unit="%"
              onChange={handleMaxEnergyChange}
              disabled={!isHost}
            />

            <SliderSetting
              label="Начальный ПЭ"
              value={startingEnergyPercentage}
              min={0}
              max={100}
              unit="%"
              onChange={handleStartingEnergyChange}
              disabled={!isHost}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default LobbyPage; 