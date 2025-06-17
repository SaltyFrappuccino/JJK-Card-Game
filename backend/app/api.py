from fastapi import APIRouter, Depends, HTTPException, Body
import uuid
from typing import Annotated

from .lobby import lobby_manager, LobbyManager
from .schemas import PlayerCreate, LobbyInfo, LobbyJoinResponse, CharacterSelectRequest, GameStateInfo, PlayerInfo, KickPlayerRequest
from .exceptions import LobbyException, LobbyNotFound, CharacterAlreadyTaken, PlayerNotFound, CharacterNotFound

router = APIRouter()

def get_lobby_manager():
    return lobby_manager

@router.post("/lobby/create", response_model=LobbyJoinResponse)
async def create_lobby(player: PlayerCreate, lm: LobbyManager = Depends(get_lobby_manager)):
    host_id = str(uuid.uuid4())
    lobby = await lm.create_lobby(host_id, player.nickname)
    lobby_info = LobbyInfo(
        id=lobby.id, 
        host_id=lobby.host_id, 
        players=[PlayerInfo(**p.dict()) for p in lobby.players]
    )
    return LobbyJoinResponse(lobby_info=lobby_info, player_id=host_id)

@router.post("/lobby/training", response_model=LobbyJoinResponse)
async def create_training_lobby(player: PlayerCreate, lm: LobbyManager = Depends(get_lobby_manager)):
    host_id = str(uuid.uuid4())
    lobby = await lm.create_lobby(host_id, player.nickname, is_training=True)
    lobby_info = LobbyInfo(
        id=lobby.id,
        host_id=lobby.host_id,
        players=[PlayerInfo(**p.dict()) for p in lobby.players]
    )
    return LobbyJoinResponse(lobby_info=lobby_info, player_id=host_id)

@router.get("/lobby/{lobby_id}", response_model=LobbyInfo)
async def get_lobby(lobby_id: str, lm: LobbyManager = Depends(get_lobby_manager)):
    lobby = lm.get_lobby(lobby_id)
    if not lobby:
        raise HTTPException(status_code=404, detail="Lobby not found")
    return lobby

@router.post("/lobby/{lobby_id}/join", response_model=LobbyJoinResponse)
async def join_lobby(lobby_id: str, player: PlayerCreate, lm: LobbyManager = Depends(get_lobby_manager)):
    try:
        player_id = str(uuid.uuid4())
        lobby = await lm.join_lobby(lobby_id, player_id, player.nickname)
        lobby_info = LobbyInfo(
            id=lobby.id,
            host_id=lobby.host_id,
            players=[PlayerInfo(**p.dict()) for p in lobby.players]
        )
        return LobbyJoinResponse(lobby_info=lobby_info, player_id=player_id)
    except LobbyNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/lobby/{lobby_id}/character", response_model=LobbyInfo)
async def select_character(lobby_id: str, selection: CharacterSelectRequest, lm: LobbyManager = Depends(get_lobby_manager)):
    try:
        lobby = await lm.select_character(lobby_id, selection.player_id, selection.character_id)
        return lobby
    except (LobbyNotFound, PlayerNotFound, CharacterNotFound) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CharacterAlreadyTaken as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/lobby/{lobby_id}/start", response_model=GameStateInfo)
async def start_game(lobby_id: str, player_id_body: Annotated[dict, Body()], lm: LobbyManager = Depends(get_lobby_manager)):
    player_id = player_id_body.get("player_id")
    if not player_id:
        raise HTTPException(status_code=400, detail="player_id is required.")
    
    try:
        game = await lm.start_game(lobby_id, player_id)
        return game
    except (LobbyNotFound, PlayerNotFound) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LobbyException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/lobby/{lobby_id}/kick", response_model=LobbyInfo)
async def kick_player(lobby_id: str, request: KickPlayerRequest, lm: LobbyManager = Depends(get_lobby_manager)):
    try:
        lobby = await lm.kick_player(lobby_id, request.host_id, request.player_to_kick_id)
        return lobby
    except (LobbyNotFound, PlayerNotFound) as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LobbyException as e:
        raise HTTPException(status_code=403, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
