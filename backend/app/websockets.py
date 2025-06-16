from fastapi import WebSocket
from typing import Dict, Set
from starlette.websockets import WebSocketState

# player_id -> websocket
connections: Dict[str, WebSocket] = {}
# lobby_id -> set(player_id)
lobby_rooms: Dict[str, Set[str]] = {}

async def register(lobby_id: str, player_id: str, ws: WebSocket):
    connections[player_id] = ws
    lobby_rooms.setdefault(lobby_id, set()).add(player_id)

async def unregister(lobby_id: str, player_id: str):
    lobby_rooms.get(lobby_id, set()).discard(player_id)
    connections.pop(player_id, None)

async def broadcast(lobby_id: str, message: dict):
    for pid in list(lobby_rooms.get(lobby_id, set())):
        ws = connections.get(pid)
        if ws and ws.application_state == WebSocketState.CONNECTED:
            try:
                await ws.send_json(message)
            except Exception:
                pass 