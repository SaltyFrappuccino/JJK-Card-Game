import string, random
from typing import Dict

from .models import Lobby, Player, Game
from .exceptions import LobbyNotFound, CharacterAlreadyTaken, PlayerNotFound, CharacterNotFound, LobbyException
from .content import characters
from .game import game_manager
from .websockets import broadcast

# In-memory storage for lobbies
lobbies: Dict[str, Lobby] = {}

def _generate_lobby_id():
    """Generates a unique 6-digit alphanumeric lobby code."""
    while True:
        lobby_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if lobby_id not in lobbies:
            return lobby_id

class LobbyManager:
    async def create_lobby(self, host_id: str, nickname: str, is_training: bool = False) -> Lobby:
        lobby_id = _generate_lobby_id()
        host = Player(id=host_id, nickname=nickname)
        lobby = Lobby(id=lobby_id, host_id=host_id, players=[host], is_training=is_training)
        lobbies[lobby_id] = lobby
        return lobby

    def get_lobby(self, lobby_id: str) -> Lobby | None:
        return lobbies.get(lobby_id)

    async def join_lobby(self, lobby_id: str, player_id: str, nickname: str) -> Lobby:
        lobby = self.get_lobby(lobby_id)
        if not lobby:
            raise LobbyNotFound(f"Lobby with id {lobby_id} not found.")
        
        if len(lobby.players) >= 8:
            raise LobbyException("Lobby is full.")

        new_player = Player(id=player_id, nickname=nickname)
        lobby.players.append(new_player)
        
        await broadcast(lobby_id, {"type": "lobby_update", "payload": lobby.dict()})
        return lobby

    async def select_character(self, lobby_id: str, player_id: str, character_id: str) -> Lobby:
        lobby = self.get_lobby(lobby_id)
        if not lobby:
            raise LobbyNotFound(f"Lobby with id {lobby_id} not found.")

        # Check if character is already taken
        for p in lobby.players:
            if p.character and p.character.id == character_id:
                raise CharacterAlreadyTaken(f"Character {character_id} is already taken.")

        player = next((p for p in lobby.players if p.id == player_id), None)
        if not player:
            raise PlayerNotFound(f"Player with id {player_id} not found in lobby {lobby_id}.")

        character_template = next((c for c in characters if c.id == character_id), None)
        if not character_template:
            raise CharacterNotFound(f"Character with id {character_id} not found.")

        player.character = character_template
        player.hp = character_template.max_hp
        player.max_hp = character_template.max_hp
        player.energy = character_template.max_energy
        
        await broadcast(lobby_id, {"type": "lobby_update", "payload": lobby.dict()})
        return lobby
        
    async def start_game(self, lobby_id: str, player_id: str) -> Game:
        lobby = self.get_lobby(lobby_id)
        if not lobby:
            raise LobbyNotFound("Lobby not found.")
        if lobby.host_id != player_id:
            raise LobbyException("Только хост может начать игру.")
        
        if not lobby.is_training:
            if len(lobby.players) < 2:
                raise LobbyException("Для начала игры нужно минимум 2 игрока.")
            if any(p.character is None for p in lobby.players):
                raise LobbyException("Не все игроки выбрали персонажа.")
            
        game = await game_manager.start_game_and_watcher(lobby)
        
        # Notify all players in the lobby that the game is starting
        await broadcast(lobby_id, {"type": "game_state", "payload": game.dict()})
        
        # Clean up lobby
        del lobbies[lobby_id]
        
        return game

    async def kick_player(self, lobby_id: str, host_id: str, player_to_kick_id: str) -> Lobby:
        lobby = self.get_lobby(lobby_id)
        if not lobby:
            raise LobbyNotFound(f"Lobby with id {lobby_id} not found.")
        
        if lobby.host_id != host_id:
            raise LobbyException("Только хост может кикать игроков.")

        if host_id == player_to_kick_id:
            raise LobbyException("Хост не может кикнуть сам себя.")

        player_to_kick = next((p for p in lobby.players if p.id == player_to_kick_id), None)
        if not player_to_kick:
            raise PlayerNotFound(f"Игрок с id {player_to_kick_id} не найден в лобби.")
        
        lobby.players.remove(player_to_kick)
        
        await broadcast(lobby_id, {"type": "lobby_update", "payload": lobby.dict()})
        await broadcast(lobby_id, {"type": "player_kicked", "payload": {"kicked_player_id": player_to_kick_id, "kicked_player_nickname": player_to_kick.nickname}})
        
        return lobby

lobby_manager = LobbyManager()
