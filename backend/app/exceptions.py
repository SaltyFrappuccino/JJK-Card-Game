class LobbyException(Exception):
    """Base exception for lobby-related errors."""
    pass

class LobbyNotFound(LobbyException):
    """Raised when a lobby is not found."""
    pass

class CharacterAlreadyTaken(LobbyException):
    """Raised when a character is already taken by another player in the lobby."""
    pass

class PlayerNotFound(LobbyException):
    """Raised when a player is not found in the lobby."""
    pass

class CharacterNotFound(LobbyException):
    """Raised when a character template is not found."""
    pass

class GameException(Exception):
    """Base exception for game-related errors."""
    pass
