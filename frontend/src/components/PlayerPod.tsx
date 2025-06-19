import React from 'react';
import type { Player } from '../types';
import clsx from 'clsx';
import { effectsInfo } from '../assets/effectsInfo';
import { Tooltip } from 'react-tooltip'
import 'react-tooltip/dist/react-tooltip.css'
import { ALL_CHARACTERS } from '../assets/content';

interface PlayerPodProps {
  player: Player;
  isCurrent: boolean;
  isTargetable: boolean;
  onSelect?: (playerId: string, event?: React.MouseEvent) => void;
  isSelf?: boolean;
  onEndTurn?: () => void;
  viewerIsGojo?: boolean;
  isTraining?: boolean;
  onRemoveDummy?: (dummyId: string) => void;
  style?: React.CSSProperties;
}

const PlayerPod: React.FC<PlayerPodProps> = ({ player, isCurrent, isTargetable, onSelect, isSelf = false, onEndTurn, viewerIsGojo = false, isTraining = false, onRemoveDummy, style }) => {
  const fullCharacterData = player.character ? ALL_CHARACTERS.find(c => c.id === player.character!.id) : null;

  const maxHp = player.character?.max_hp || player.max_hp || 1;
  const hpPercent = player.hp ? (player.hp / maxHp) * 100 : 0;
  
  const canSeeEnergy = isSelf || viewerIsGojo;
  const maxEnergy = player.character?.max_energy || 1;
  const energyPercent = canSeeEnergy && player.energy ? (player.energy / maxEnergy) * 100 : 100;

  const isBlindfolded = player.effects.some(e => e.name === 'gojo_blindfold');
  
  const portraitSrc = isBlindfolded
    ? fullCharacterData?.portrait_blindfolded
    : fullCharacterData?.portrait;

  // Get character glow class
  const getCharacterGlowClass = (characterId: string | undefined): string => {
    switch (characterId) {
      case 'gojo_satoru': return 'character-glow-gojo';
      case 'sukuna_ryomen': return 'character-glow-sukuna';
      case 'jogo': return 'character-glow-jogo';
      case 'mahito': return 'character-glow-mahito';
      case 'yuta_okkotsu': return 'character-glow-yuta';
      case 'itadori_yuji': return 'character-glow-itadori';
      default: return '';
    }
  };

  const characterGlowClass = getCharacterGlowClass(player.character?.id);

  return (
    <div
      style={style}
      className={clsx('player-pod', {
        'current-player': isCurrent,
        'targetable': isTargetable,
        'defeated': player.status === 'DEFEATED',
        'self-player': isSelf,
      }, characterGlowClass)}
      onClick={(event) => onSelect && isTargetable && player.status !== 'DEFEATED' && onSelect(player.id, event)}
      onContextMenu={(event) => onSelect && isTargetable && player.status !== 'DEFEATED' && onSelect(player.id, event)}
    >
      {fullCharacterData && portraitSrc && (
        <img 
          src={portraitSrc} 
          alt={fullCharacterData.name} 
          className="player-portrait"
          data-tooltip-id={`passive-tooltip-${player.id}`}
          data-tooltip-html={`<strong>${fullCharacterData.passive_ability_name}</strong><br />${fullCharacterData.passive_ability_description}`}
        />
      )}
      {fullCharacterData && <Tooltip id={`passive-tooltip-${player.id}`} />}

      <div className="player-info">
        <span className="nickname">{player.nickname}</span>
        <span className="character-name">{player.character?.name}</span>
      </div>
      <div className="status-bars">
        <div className="hp-bar">
          <div className="hp-fill" style={{ width: `${hpPercent}%` }}></div>
          <span className="hp-text">{player.hp} / {maxHp}</span>
        </div>
        <div className="energy-bar">
          <div className="energy-fill" style={{ width: `${energyPercent}%` }}></div>
          <span className="energy-text">{canSeeEnergy ? `${player.energy} / ${player.character?.max_energy ?? '??'}` : '???'}</span>
        </div>
      </div>
      {player.block > 0 && <div className="block-indicator">Block: {player.block}</div>}
      {player.character?.id === 'mahito' && (
        <div className="souls-indicator">
          Искажённые души: {player.distorted_souls ?? 0}
        </div>
      )}
      <div className="effects">
        {player.effects.map((effect, index) => {
          const abbreviation = effect.name.split(' ').map(word => word[0]).join('').toUpperCase();
          const effectInfo = effectsInfo[effect.name as keyof typeof effectsInfo];
          
          const tooltipContent = effectInfo 
            ? `<strong>${effectInfo.title}</strong><br />${effectInfo.description}<br />(Осталось ходов: ${effect.duration})` 
            : `Нет описания<br />(Осталось ходов: ${effect.duration})`;

          const tooltipId = `tooltip-${player.id}-${effect.name.replace(/[^a-zA-Z0-9]/g, '')}-${index}`;
          
          const effectClassName = clsx('effect-icon', {
            'effect-icon--positive': effectInfo?.type === 'POSITIVE',
            'effect-icon--negative': effectInfo?.type === 'NEGATIVE',
          });

          const tooltipClassName = clsx({
            'tooltip-positive': effectInfo?.type === 'POSITIVE',
            'tooltip-negative': effectInfo?.type === 'NEGATIVE',
          });

          return (
            <div key={index} className="effect-icon-container">
              <div 
                className={effectClassName}
                data-tooltip-id={tooltipId}
                data-tooltip-html={tooltipContent}
                data-tooltip-place="top"
              >
                {abbreviation}
              </div>
              <Tooltip id={tooltipId} html={tooltipContent} className={tooltipClassName} />
            </div>
          );
        })}
      </div>
      {isSelf && isCurrent && onEndTurn && (
        <button className="end-turn-button" onClick={onEndTurn}>Конец хода</button>
      )}
      {isTraining && player.id.startsWith("dummy") && onRemoveDummy && (
        <button className="remove-dummy-btn" onClick={() => onRemoveDummy(player.id)}>Удалить</button>
      )}
    </div>
  );
};

export default PlayerPod; 