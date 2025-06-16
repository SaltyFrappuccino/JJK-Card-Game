export interface Card {
  name: string;
  type: string;
  rarity: string;
  cost: number;
  description: string;
  source_player_id?: string;
  duration?: number;
}

export interface Character {
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

export enum PlayerStatus {
  ALIVE = "ALIVE",
  DEFEATED = "DEFEATED",
}

export interface Player {
  id: string;
  nickname: string;
  character?: Character;
  hp?: number;
  energy?: number;
  block: number;
  hand: Card[];
  deck: Card[];
  discard_pile: Card[];
  effects: Effect[];
  status: PlayerStatus;
}

export interface LobbyInfo {
  id: string;
  host_id: string;
  players: Player[];
}

export enum GameStateEnum {
  LOBBY = "LOBBY",
  IN_GAME = "IN_GAME",
  FINISHED = "FINISHED",
}

export interface GameState {
  game_id: string;
  players: Player[];
  current_turn_player_index: number;
  round_number: number;
  game_state: GameStateEnum;
  active_domain?: Card;
  game_log: string[];
} 