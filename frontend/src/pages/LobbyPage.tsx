import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import useGameStore from '../store/gameStore';
import { useWS } from '../hooks/useSocket';
import { api } from '../services/api';
import { ALL_CHARACTERS } from '../assets/content';
import type { Character } from '../types';

const LobbyPage: React.FC = () => {
  useWS(); // Initialize WebSocket listeners
  const { lobby, player, setLobby, setError } = useGameStore();
  const [selectedCharacter, setSelectedCharacter] = useState<Character | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const navigate = useNavigate();

  const handleCharacterSelect = async (character: Character) => {
    if (!lobby || !player?.id) return;
    
    // Prevent selecting already chosen character
    const isChosen = lobby.players.some(p => p.character?.name === character.name);
    if (isChosen) {
      setError('This character is already taken.');
      return;
    }

    setSelectedCharacter(character);
    try {
      const { data } = await api.selectCharacter(lobby.id, player.id, character.name);
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
  
  const isHost = lobby.host_id === player.id;
  const allPlayersReady = lobby.players.every(p => p.character);

  return (
    <div className="lobby-page">
      <h2>Lobby: {lobby.id}</h2>
      <button onClick={() => navigator.clipboard.writeText(lobby.id)}>Copy Code</button>
      
      <div className="lobby-container">
        <div className="players-list">
          <h3>Players ({lobby.players.length}/8)</h3>
          <ul>
            {lobby.players.map(p => (
              <li key={p.id}>
                {p.nickname} {p.id === lobby.host_id ? '(Host)' : ''}
                {p.character ? ` - ${p.character.name}` : ' - Selecting...'}
              </li>
            ))}
          </ul>
        </div>
        
        <div className="character-selection">
          <h3>Choose your Character</h3>
          <div className="character-carousel">
            {ALL_CHARACTERS.map(char => {
              const isTaken = lobby.players.some(p => p.character?.name === char.name);
              return (
                <div 
                  key={char.name} 
                  className={`character-card ${selectedCharacter?.name === char.name ? 'selected' : ''} ${isTaken ? 'taken' : ''}`}
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
            <h4>Unique Cards:</h4>
            <ul>
              {selectedCharacter.unique_cards.map(card => <li key={card.name}>{card.name}</li>)}
            </ul>
          </div>
        )}
      </div>

      {isHost && (
        <button onClick={handleStartGame} disabled={!allPlayersReady || isStarting}>
          {isStarting ? 'Starting...' : 'Start Game'}
        </button>
      )}
    </div>
  );
};

export default LobbyPage; 