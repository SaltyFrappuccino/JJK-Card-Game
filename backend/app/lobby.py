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

        # Создаем копию персонажа, чтобы не изменять глобальный объект
        player.character = character_template.copy(deep=True)
        
        # Применяем настройки игры
        modified_max_hp = int(character_template.max_hp * lobby.game_settings.hp_percentage / 100)
        modified_max_energy = int(character_template.max_energy * lobby.game_settings.max_energy_percentage / 100)
        starting_energy = int(modified_max_energy * lobby.game_settings.starting_energy_percentage / 100)
        
        player.hp = modified_max_hp
        player.max_hp = modified_max_hp
        player.energy = starting_energy
        
        # Обновляем характеристики персонажа с учетом настроек
        player.character.max_hp = modified_max_hp
        player.character.max_energy = modified_max_energy
        
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
            
        game = game_manager.start_game(lobby)
        
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

    async def update_game_settings(self, lobby_id: str, player_id: str, hp_percentage: int, max_energy_percentage: int, starting_energy_percentage: int) -> Lobby:
        lobby = self.get_lobby(lobby_id)
        if not lobby:
            raise LobbyNotFound(f"Lobby with id {lobby_id} not found.")
        
        if lobby.host_id != player_id:
            raise LobbyException("Только хост может изменять настройки игры.")

        # Validate percentages
        if not (1 <= hp_percentage <= 300):
            raise LobbyException("HP percentage must be between 1% and 300%.")
        if not (1 <= max_energy_percentage <= 300):
            raise LobbyException("Max energy percentage must be between 1% and 300%.")
        if not (0 <= starting_energy_percentage <= 100):
            raise LobbyException("Starting energy percentage must be between 0% and 100%.")
        
        lobby.game_settings.hp_percentage = hp_percentage
        lobby.game_settings.max_energy_percentage = max_energy_percentage
        lobby.game_settings.starting_energy_percentage = starting_energy_percentage
        
        # Пересчитываем характеристики всех игроков с уже выбранными персонажами
        for p in lobby.players:
            if p.character:
                # Находим оригинальный шаблон персонажа
                original_character = next((c for c in characters if c.id == p.character.id), None)
                if original_character:
                    # Пересчитываем характеристики с новыми настройками
                    modified_max_hp = int(original_character.max_hp * hp_percentage / 100)
                    modified_max_energy = int(original_character.max_energy * max_energy_percentage / 100)
                    starting_energy = int(modified_max_energy * starting_energy_percentage / 100)
                    
                    p.hp = modified_max_hp
                    p.max_hp = modified_max_hp
                    p.energy = starting_energy
                    p.character.max_hp = modified_max_hp
                    p.character.max_energy = modified_max_energy
        
        await broadcast(lobby_id, {"type": "lobby_update", "payload": lobby.dict()})
        
        return lobby

lobby_manager = LobbyManager()
