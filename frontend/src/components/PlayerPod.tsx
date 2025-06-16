import React from 'react';
import type { Player } from '../types';
import clsx from 'clsx';
import { effectsInfo } from '../assets/effectsInfo';
import { Tooltip } from 'react-tooltip'
import 'react-tooltip/dist/react-tooltip.css'

interface PlayerPodProps {
  player: Player;
  isCurrent: boolean;
  isTargetable: boolean;
  onSelect?: (playerId: string) => void;
  isSelf?: boolean;
  onEndTurn?: () => void;
  viewerIsGojo?: boolean;
}

const PlayerPod: React.FC<PlayerPodProps> = ({ player, isCurrent, isTargetable, onSelect, isSelf = false, onEndTurn, viewerIsGojo = false }) => {
  const hpPercent = player.hp && player.character ? (player.hp / player.character.max_hp) * 100 : 0;
  const canSeeEnergy = isSelf || viewerIsGojo;
  const energyPercent = canSeeEnergy && player.energy && player.character ? (player.energy / player.character.max_energy) * 100 : 100;

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
          <span className="energy-text">{canSeeEnergy ? `${player.energy} / ${player.character?.max_energy}` : '???'}</span>
        </div>
      </div>
      {player.block > 0 && <div className="block-indicator">Block: {player.block}</div>}
      <div className="effects">
        {player.effects.map((effect, index) => {
          const abbreviation = effect.name.split(' ').map(word => word[0]).join('').toUpperCase();
          const description = effectsInfo[effect.name as keyof typeof effectsInfo] || 'Нет описания';
          const fullDescription = `${description} (Осталось ходов: ${effect.duration})`;
          const tooltipId = `tooltip-${player.id}-${effect.name.replace(/[^a-zA-Z0-9]/g, '')}-${index}`;

          return (
            <div key={index} className="effect-icon-container">
              <div 
                className="effect-icon"
                data-tooltip-id={tooltipId}
                data-tooltip-content={fullDescription}
                data-tooltip-place="top"
              >
                {abbreviation}
              </div>
              <Tooltip id={tooltipId} />
            </div>
          );
        })}
      </div>
      {isSelf && isCurrent && onEndTurn && (
        <button className="end-turn-button" onClick={onEndTurn}>Конец хода</button>
      )}
    </div>
  );
};

export default PlayerPod; 