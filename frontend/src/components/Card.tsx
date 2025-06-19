import React, { useRef, useState } from 'react';
import type { Card as CardType } from '../types';
import clsx from 'clsx';
import { motion } from 'framer-motion';
import { ALL_CARDS } from '../assets/content';
import './../styles/components.css'

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

const cleanLabel = (text: string) => text.replace(/^\*\*/, '').trim();

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

  main = main.replace(/<br\s*\/?>/gi, ' ');

  const parts: React.ReactNode[] = [];
  if (main) parts.push(<span key="main">{main}</span>);
  if (condition) parts.push(<span key="cond" className="card-condition">{condition}</span>);
  if (synergy) parts.push(<span key="syn" className="card-synergy">{synergy}</span>);
  return <>{parts}</>;
};

const rarityClass = (rarity: string) => `rarity-${rarity.toLowerCase()}`;

export const Card: React.FC<CardProps> = ({ card, isPlayable, onClick, index = 0, total = 1, isSelected = false, className }) => {
  const cardRef = useRef<HTMLDivElement>(null);
  const [transform, setTransform] = useState('');
  
  const angle = (index - (total - 1) / 2) * 10;
  const yOffset = isSelected ? -80 : 0;
  const scaleVal = isSelected ? 1.25 : 1;
  const z = isSelected ? 150 : index;

  const nameCss = SPECIAL_NAME_STYLES[card.name] ?? '';
  const isKamino = card.id === 'sukuna_kamino';

  const cardInfo = ALL_CARDS.find(c => c.id === card.id);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!cardRef.current) return;
    
    const rect = cardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    const centerX = rect.width / 2;
    const centerY = rect.height / 2;
    
    const rotateX = (y - centerY) / 10;
    const rotateY = (centerX - x) / 10;
    
    setTransform(`perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateZ(20px)`);
  };

  const handleMouseLeave = () => {
    setTransform('');
  };

  return (
    <motion.div
      ref={cardRef}
      className={clsx('card', rarityClass(card.rarity), { 'is-playable': isPlayable, 'is-selected': isSelected }, className)}
      style={{ 
        marginLeft: index === 0 ? 0 : -170, 
        zIndex: z, 
        transformOrigin: 'bottom center',
        transform: transform
      }}
      initial={{ rotate: angle, y: yOffset, scale: scaleVal }}
      animate={{ rotate: angle, y: yOffset, scale: scaleVal, zIndex: z }}
      whileHover={{ scale: isSelected ? 1.3 : 1.2, y: isSelected ? -90 : -30, rotate: 0, zIndex: 200 }}
      onClick={onClick}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
    >
      {cardInfo?.image && (
        <div className="card-image-container">
          <img src={cardInfo.image} alt={card.name} className="card-image" />
        </div>
      )}
      <div className="card-header">
        <span className={clsx('card-name', nameCss, { 'card-name-fire': isKamino })} data-text={card.name}>{card.name}</span>
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