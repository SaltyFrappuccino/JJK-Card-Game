export interface Card {
  id: string;
  name: string;
  type: string;
  rarity: string;
  cost: number;
  description: string;
  source_player_id?: string;
  duration?: number;
}

export interface Character {
  id: string;
  name: string;
  max_hp: number;
  max_energy: number;
  passive_ability_name: string;
  passive_ability_description: string;
  unique_cards: Card[];
}

export interface Effect {
  name: string;
  duration: number;
  value?: number;
  source_player_id: string;
  target_id?: string;
}

export type PlayerStatus = 'ALIVE' | 'DEFEATED';

export interface Player {
  id: string;
  nickname: string;
  character: Character | null;
  hp: number | null;
  energy: number | null;
  block: number;
  hand: Card[];
  deck: Card[];
  discard_pile: Card[];
  effects: Effect[];
  status: PlayerStatus;
  last_discard_round: number;
  max_hp?: number;
  distorted_souls?: number;
}

export interface LobbyInfo {
  id: string;
  host_id: string;
  players: Player[];
  is_training: boolean;
}

export type GameStateEnum = 'LOBBY' | 'IN_GAME' | 'FINISHED';

export interface GameState {
  game_id: string;
  players: Player[];
  current_turn_player_index: number;
  round_number: number;
  game_state: GameStateEnum;
  active_domain?: Card;
  game_log: string[];
  is_training: boolean;
  turn_start_time?: string;
}

export interface Game {
  game_id: string;
  players: Player[];
  current_turn_player_index: number;
  game_state: 'IN_PROGRESS' | 'FINISHED';
  game_log: string[];
  round_number: number;
  is_training: boolean;
  turn_start_time?: string;
}

export interface Lobby {
  id: string;
  // ... existing code ...
} 