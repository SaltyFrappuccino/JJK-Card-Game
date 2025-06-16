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

const Card: React.FC<CardProps> = ({ card, isPlayable, onClick, index = 0, total = 1, isSelected = false, className }) => {
  const angle = (index - (total - 1) / 2) * 10;
  const yOffset = isSelected ? -80 : 0;
  const scaleVal = isSelected ? 1.25 : 1;
  const z = isSelected ? 150 : index;

  const rarityMap: Record<string, string> = {
    'Обычная': 'common',
    'Необычная': 'uncommon',
    'Редкая': 'rare',
    'Эпическая': 'epic',
    'Легендарная': 'legendary',
    'COMMON': 'common',
    'UNCOMMON': 'uncommon',
    'RARE': 'rare',
    'EPIC': 'epic',
    'LEGENDARY': 'legendary',
  };
  const raritySlug = rarityMap[card.rarity] ?? (card.rarity as string).toLowerCase();

  return (
    <motion.div
      className={clsx('card', `rarity-${raritySlug}`, className, {
        'playable': isPlayable,
        'selected': isSelected,
      })}
      style={{ marginLeft: index === 0 ? 0 : -170, zIndex: z, transformOrigin: 'bottom center' }}
      initial={{ rotate: angle, y: yOffset, scale: scaleVal }}
      animate={{ rotate: angle, y: yOffset, scale: scaleVal, zIndex: z }}
      whileHover={{ scale: isSelected ? 1.3 : 1.2, y: isSelected ? -90 : -30, rotate: 0, zIndex: 200 }}
      onClick={onClick}
    >
      <div className="card-image">Image</div>
      <div className="card-header">
        <span className="card-name">{card.name}</span>
        <span className="card-cost">{card.cost}</span>
      </div>
      <div className="card-body">
        <p className="card-description">{card.description}</p>
      </div>
      <div className="card-footer">
        <span className="card-type">{card.type}</span>
        <span className="card-rarity">{card.rarity}</span>
      </div>
    </motion.div>
  );
};

export default Card; 