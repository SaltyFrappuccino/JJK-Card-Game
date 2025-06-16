import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../services/api';
import useGameStore from '../store/gameStore';

const HomePage: React.FC = () => {
    const [nickname, setNickname] = useState('');
    const [lobbyCode, setLobbyCode] = useState('');
    const navigate = useNavigate();
    const { setPlayer, setLobby } = useGameStore();

    const handleCreateLobby = async () => {
        if (nickname.trim()) {
            try {
                const { data } = await api.createLobby(nickname);
                setPlayer({ id: data.player_id, nickname: nickname });
                setLobby(data.lobby_info);
                navigate(`/lobby/${data.lobby_info.id}`);
            } catch (error: any) {
                console.error("Failed to create lobby:", error);
                alert(`Не удалось создать лобби: ${error.response?.data?.detail || 'Попробуйте снова.'}`);
            }
        } else {
            alert('Пожалуйста, введите никнейм.');
        }
    };

    const handleJoinLobby = async () => {
        if (nickname.trim() && lobbyCode.trim()) {
            try {
                const { data } = await api.joinLobby(lobbyCode, nickname);
                setPlayer({ id: data.player_id, nickname: nickname });
                setLobby(data.lobby_info);
                navigate(`/lobby/${data.lobby_info.id}`);
            } catch (error: any) {
                console.error("Failed to join lobby:", error);
                alert(`Не удалось присоединиться к лобби: ${error.response?.data?.detail || 'Проверьте код и попробуйте снова.'}`);
            }
        } else {
            alert('Пожалуйста, введите никнейм и код лобби.');
        }
    };

    const handleTraining = async () => {
        if (nickname.trim()) {
            try {
                const { data } = await api.createTrainingLobby(nickname);
                setPlayer({ id: data.player_id, nickname: nickname });
                setLobby(data.lobby_info);
                navigate(`/lobby/${data.lobby_info.id}`);
            } catch (error: any) {
                console.error("Failed to create training lobby:", error);
                alert(`Не удалось войти в тренировку: ${error.response?.data?.detail || 'Попробуйте снова.'}`);
            }
        } else {
            alert('Пожалуйста, введите никнейм.');
        }
    };

    return (
        <div className="home-container">
            <h1>Jujutsu Kaisen: Heian Cards Clash</h1>
            <div className="menu-box">
                <input
                    type="text"
                    placeholder="Ваш никнейм"
                    value={nickname}
                    onChange={(e) => setNickname(e.target.value)}
                    className="input-field"
                />
                <button onClick={handleCreateLobby} className="btn btn-primary">Создать лобби</button>
            </div>
            <div className="menu-box">
                <input
                    type="text"
                    placeholder="Код лобби"
                    value={lobbyCode}
                    onChange={(e) => setLobbyCode(e.target.value.toUpperCase())}
                    className="input-field"
                />
                <button onClick={handleJoinLobby} className="btn btn-secondary">Присоединиться</button>
            </div>
            <div className="menu-box">
                <button onClick={handleTraining} className="btn">Тренировка</button>
            </div>
        </div>
    );
};

export default HomePage; 