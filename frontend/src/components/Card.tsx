import React from 'react';
import type { Card as CardType } from '../types';
import clsx from 'clsx';
import { motion } from 'framer-motion';

interface CardProps {
  card: CardType;
  isPlayable: boolean;
  onClick?: () => void;
  index?: number;
  total?: number;
  isSelected?: boolean;
  className?: string;
}

const SPECIAL_NAME_STYLES: Record<string, string> = {
  'Проклятая техника: "Синий"': 'name-blue',
  'Обратная проклятая техника: "Красный"': 'name-red',
  'Мнимая техника: "Фиолетовый"': 'name-purple',
};

const cleanLabel = (text: string) => text.replace(/^\*\*/,'').trim();

const prepareDescription = (description: string) => {
  let main = description;
  let condition = '';
  let synergy = '';

  const condRegex = /\*?\*?\s*Условие:[\s\S]*/i;
  const synRegex = /\*?\*?\s*Синергия:[\s\S]*/i;

  const condMatch = description.match(condRegex);
  if (condMatch) {
    condition = cleanLabel(condMatch[0]);
    main = main.replace(condMatch[0], '').trim();
  }
  const synMatch = description.match(synRegex);
  if (synMatch) {
    synergy = cleanLabel(synMatch[0]);
    main = main.replace(synMatch[0], '').trim();
  }

  const parts: React.ReactNode[] = [];
  if (main) parts.push(<span key="main">{main}</span>);
  if (condition) parts.push(<span key="cond" className="card-condition">{condition}</span>);
  if (synergy) parts.push(<span key="syn" className="card-synergy">{synergy}</span>);
  return parts;
};

const rarityClass = (rarity: string) => {
  switch (rarity) {
    case 'Обычная': return 'rarity-common';
    case 'Необычная': return 'rarity-uncommon';
    case 'Редкая': return 'rarity-rare';
    case 'Эпическая': return 'rarity-epic';
    case 'Легендарная': return 'rarity-legendary';
    default: return '';
  }
};

export const Card: React.FC<CardProps> = ({ card, isPlayable, onClick, index = 0, total = 1, isSelected = false, className }) => {
  const angle = (index - (total - 1) / 2) * 10;
  const yOffset = isSelected ? -80 : 0;
  const scaleVal = isSelected ? 1.25 : 1;
  const z = isSelected ? 150 : index;

  const nameCss = SPECIAL_NAME_STYLES[card.name] ?? '';

  return (
    <motion.div
      className={clsx('card', rarityClass(card.rarity), { 'is-playable': isPlayable, 'is-selected': isSelected }, className)}
      style={{ marginLeft: index === 0 ? 0 : -170, zIndex: z, transformOrigin: 'bottom center' }}
      initial={{ rotate: angle, y: yOffset, scale: scaleVal }}
      animate={{ rotate: angle, y: yOffset, scale: scaleVal, zIndex: z }}
      whileHover={{ scale: isSelected ? 1.3 : 1.2, y: isSelected ? -90 : -30, rotate: 0, zIndex: 200 }}
      onClick={onClick}
    >
      <div className="card-image">Image</div>
      <div className="card-header">
        <span className={clsx('card-name', nameCss)}>{card.name}</span>
        <span className="card-cost">{card.cost}</span>
      </div>
      <div className="card-body">
        <p className="card-description">{prepareDescription(card.description)}</p>
      </div>
      <div className="card-footer">
        <span className="card-type">{card.type}</span>
        <span className="card-rarity">{card.rarity}</span>
      </div>
    </motion.div>
  );
}; 