from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class Rarity(str, Enum):
    COMMON = "Обычная"
    UNCOMMON = "Необычная"
    RARE = "Редкая"
    EPIC = "Эпическая"
    LEGENDARY = "Легендарная"

class Effect(BaseModel):
    name: str
    duration: int # in rounds
    value: Optional[int] = None # e.g., for damage over time
    source_player_id: str 
    target_id: Optional[str] = None

class PlayerStatus(str, Enum):
    ALIVE = "ALIVE"
    DEFEATED = "DEFEATED"

class CardType(str, Enum):
    ACTION = "Действие"
    TECHNIQUE = "Техника"
    DOMAIN_EXPANSION = "Расширение Территории"

class Card(BaseModel):
    name: str
    type: CardType
    rarity: Rarity
    cost: int
    description: str
    source_player_id: Optional[str] = None # For domain expansions
    duration: Optional[int] = None # For domain expansions

class Character(BaseModel):
    name: str
    max_hp: int
    max_energy: int
    passive_ability_name: str
    passive_ability_description: str
    unique_cards: List[Card]

class Player(BaseModel):
    id: str  # Session ID will be used here
    nickname: str
    character: Optional[Character] = None
    hp: Optional[int] = None
    energy: Optional[int] = None
    block: int = 0
    hand: List[Card] = []
    deck: List[Card] = []
    discard_pile: List[Card] = []
    effects: List[Effect] = []
    status: PlayerStatus = PlayerStatus.ALIVE

class Lobby(BaseModel):
    id: str
    host_id: str
    players: List[Player] = []
    
class GameState(str, Enum):
    LOBBY = "LOBBY"
    IN_GAME = "IN_GAME"
    FINISHED = "FINISHED"

class Game(BaseModel):
    game_id: str
    players: List[Player]
    current_turn_player_index: int = 0
    round_number: int = 1
    game_state: GameState = GameState.IN_GAME
    active_domain: Optional[Card] = None
    game_log: List[str] = []
