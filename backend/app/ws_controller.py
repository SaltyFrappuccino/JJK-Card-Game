from .socket_manager import sio
from .lobby import lobby_manager
from .game import game_manager, GameException

# This is a simple in-memory mapping.
# For a real application, a more robust solution like Redis would be better.
sid_to_player_map: dict[str, str] = {}


def setup_socketio_events():
    @sio.event
    async def connect(sid, environ):
        print(f"Socket.IO connected: {sid}")

    @sio.event
    async def disconnect(sid):
        # TODO: Handle player disconnect during a game, e.g. make them lose.
        player_id = sid_to_player_map.get(sid)
        print(f"Socket.IO disconnected: {sid}, player: {player_id}")
        if player_id:
            # Here you could search for the game the player is in and handle their disconnection.
            del sid_to_player_map[sid]

    @sio.on('join_lobby')
    async def join_lobby(sid, data):
        lobby_id = data.get('lobby_id')
        player_id = data.get('player_id')
        if not lobby_id or not player_id:
            return
        
        sid_to_player_map[sid] = player_id
        sio.enter_room(sid, lobby_id)
        print(f"Player {player_id} ({sid}) joined lobby room {lobby_id}")
        
        lobby = lobby_manager.get_lobby(lobby_id)
        if lobby:
            await sio.emit('lobby_update', lobby.dict(), room=sid)

    @sio.on('play_card')
    async def play_card(sid, data):
        game_id = data.get('game_id')
        player_id = sid_to_player_map.get(sid)
        card_name = data.get('card_name')
        target_id = data.get('target_id')
        targets_ids = data.get('targets_ids')

        if not all([game_id, player_id, card_name]):
            await sio.emit('error', {'message': 'Missing required data.'}, room=sid)
            return
        
        try:
            game = game_manager.play_card(game_id, player_id, card_name, target_id, targets_ids)
            await sio.emit('game_state_update', game.dict(), room=game_id)
        except GameException as e:
            await sio.emit('error', {'message': str(e)}, room=sid)

    @sio.on('end_turn')
    async def end_turn(sid, data):
        game_id = data.get('game_id')
        player_id = sid_to_player_map.get(sid)

        if not game_id or not player_id:
            await sio.emit('error', {'message': 'Missing required data.'}, room=sid)
            return
            
        try:
            game = game_manager.end_turn(game_id, player_id)
            await sio.emit('game_state_update', game.dict(), room=game_id)
        except GameException as e:
            await sio.emit('error', {'message': str(e)}, room=sid)

    @sio.on('*')
    async def catch_all(event, sid, data):
        print(f"Received event '{event}' from {sid} with data: {data}") 