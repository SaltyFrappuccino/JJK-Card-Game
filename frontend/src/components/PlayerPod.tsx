import React from 'react';
import type { Player } from '../types';
import clsx from 'clsx';

interface PlayerPodProps {
  player: Player;
  isCurrent: boolean;
  isTargetable: boolean;
  onSelect?: (playerId: string) => void;
  isSelf?: boolean;
  onEndTurn?: () => void;
}

const PlayerPod: React.FC<PlayerPodProps> = ({ player, isCurrent, isTargetable, onSelect, isSelf = false, onEndTurn }) => {
  const hpPercent = player.hp && player.character ? (player.hp / player.character.max_hp) * 100 : 0;
  const energyPercent = player.energy && player.character ? (player.energy / player.character.max_energy) * 100 : 0;

  return (
    <div
      className={clsx('player-pod', {
        'current-player': isCurrent,
        'targetable': isTargetable,
        'defeated': player.status === 'DEFEATED',
        'self-player': isSelf,
      })}
      onClick={() => onSelect && isTargetable && player.status !== 'DEFEATED' && onSelect(player.id)}
    >
      <div className="player-info">
        <span className="nickname">{player.nickname}</span>
        <span className="character-name">{player.character?.name}</span>
        {player.character && (
          <div className="passive-info tooltip-container">
            <span className="info-icon">ℹ️</span>
            <div className="tooltip-content">
              <strong>{player.character.passive_ability_name}</strong>
              <p>{player.character.passive_ability_description}</p>
            </div>
          </div>
        )}
      </div>
      <div className="status-bars">
        <div className="hp-bar">
          <div className="hp-fill" style={{ width: `${hpPercent}%` }}></div>
          <span className="hp-text">{player.hp} / {player.character?.max_hp}</span>
        </div>
        <div className="energy-bar">
          <div className="energy-fill" style={{ width: `${energyPercent}%` }}></div>
          <span className="energy-text">{player.energy} / {player.character?.max_energy}</span>
        </div>
      </div>
      {player.block > 0 && <div className="block-indicator">Block: {player.block}</div>}
      <div className="effects">
        {player.effects.map((effect, index) => (
          <div key={index} className="effect-icon tooltip-container">
            {effect.name.slice(0, 2).toUpperCase()}
            <div className="tooltip-content">
              <strong>{effect.name}</strong>
              <p>Длительность: {effect.duration}</p>
            </div>
          </div>
        ))}
      </div>
      {isSelf && isCurrent && onEndTurn && (
        <button className="end-turn-button" onClick={onEndTurn}>Конец хода</button>
      )}
    </div>
  );
};

export default PlayerPod; 