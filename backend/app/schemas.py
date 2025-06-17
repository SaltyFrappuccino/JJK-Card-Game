from pydantic import BaseModel
from typing import List, Optional

from .models import Card, Character

# --- Schemas for Player and Lobby Management ---

class PlayerCreate(BaseModel):
    nickname: str

class PlayerInfo(BaseModel):
    id: str
    nickname: str
    character: Optional[Character] = None

    class Config:
        orm_mode = True

class LobbyInfo(BaseModel):
    id: str
    host_id: str
    players: List[PlayerInfo]

    class Config:
        orm_mode = True

class LobbyJoinResponse(BaseModel):
    lobby_info: LobbyInfo
    player_id: str

class CharacterSelectRequest(BaseModel):
    player_id: str
    character_id: str

class KickPlayerRequest(BaseModel):
    host_id: str
    player_to_kick_id: str

# --- Schemas for Game State ---

class GameStateInfo(BaseModel):
    game_id: str
    players: List[PlayerInfo]
    current_turn_player_index: int
    round_number: int
    active_domain: Optional[Card] = None
    game_state: str
    game_log: List[str]

    class Config:
        orm_mode = True
