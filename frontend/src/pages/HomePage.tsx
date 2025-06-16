import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import useGameStore from '../store/gameStore';

const HomePage: React.FC = () => {
  const [nickname, setNickname] = useState('');
  const [lobbyCode, setLobbyCode] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { setPlayer, setLobby, setError } = useGameStore();

  const handleCreateLobby = async () => {
    if (!nickname) {
      setError('Please enter a nickname.');
      return;
    }
    setIsLoading(true);
    try {
      const { data } = await api.createLobby(nickname);
      setPlayer({ id: data.player_id, nickname });
      setLobby(data.lobby_info);

      navigate(`/lobby/${data.lobby_info.id}`);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to create lobby.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleJoinLobby = async () => {
    if (!nickname || !lobbyCode) {
      setError('Please enter a nickname and lobby code.');
      return;
    }
    setIsLoading(true);
    try {
      const { data } = await api.joinLobby(lobbyCode, nickname);
      setPlayer({ id: data.player_id, nickname });
      setLobby(data.lobby_info);

      navigate(`/lobby/${data.lobby_info.id}`);
    } catch (error: any) {
      setError(error.response?.data?.detail || 'Failed to join lobby.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="home-page">
      <h1>Jujutsu Kaisen: Cursed Clash</h1>
      <div className="form-container">
        <input
          type="text"
          placeholder="Введите ваш ник"
          value={nickname}
          onChange={(e) => setNickname(e.target.value)}
          maxLength={32}
          className="nickname-input"
        />
        <div className="lobby-actions">
          <div className="create-lobby">
            <button onClick={handleCreateLobby} disabled={isLoading || !nickname}>
              {isLoading ? 'Создание...' : 'Создать игру'}
            </button>
          </div>
          <div className="join-lobby">
            <input
              type="text"
              placeholder="Код лобби"
              value={lobbyCode}
              onChange={(e) => setLobbyCode(e.target.value.toUpperCase())}
              className="lobby-code-input"
            />
            <button onClick={handleJoinLobby} disabled={isLoading || !nickname || !lobbyCode}>
              {isLoading ? 'Подключение...' : 'Присоединиться'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default HomePage; 