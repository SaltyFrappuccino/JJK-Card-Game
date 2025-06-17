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
    ANTI_DOMAIN_TECHNIQUE = "Антитерриториальная Техника"

class Card(BaseModel):
    id: str
    name: str
    type: CardType
    rarity: Rarity
    cost: int
    description: str
    source_player_id: Optional[str] = None # For domain expansions
    duration: Optional[int] = None # For domain expansions
    is_copied: bool = False

class Character(BaseModel):
    id: str
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
    max_hp: Optional[int] = None # For dummies mostly
    energy: Optional[int] = None
    block: int = 0
    hand: List[Card] = []
    deck: List[Card] = []
    discard_pile: List[Card] = []
    effects: List[Effect] = []
    status: PlayerStatus = PlayerStatus.ALIVE
    last_discard_round: int = 0  # раунд, когда игрок последний раз использовал сброс
    # Gojo's state for "Purple"
    used_blue: bool = False
    used_red: bool = False
    # Mahito's state for "True Body"
    successful_black_flash: bool = False
    ignore_block_attacks_count: int = 0
    # For chant effect
    chant_active_for_turn: bool = False
    # Gojo's state for cost reduction
    cost_modifier: float = 0.9  # Initial 10% discount
    is_blindfolded: bool = True
    # Mahito's resources
    distorted_souls: int = 0

class Lobby(BaseModel):
    id: str
    host_id: str
    players: List[Player] = []
    is_training: bool = False
    
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
    is_training: bool = False
