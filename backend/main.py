import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api import router as api_router
from app.websockets import register, unregister, broadcast
from app.game import game_manager, GameException
from app.lobby import lobby_manager

app = FastAPI(
    title="Jujutsu Kaisen: Cursed Clash API",
    description="API for the Jujutsu Kaisen: Cursed Clash card game.",
    version="1.0.0",
)

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include REST routers
app.include_router(api_router, prefix="/api")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Jujutsu Kaisen: Cursed Clash API!"}

@app.websocket("/ws/{lobby_id}/{player_id}")
async def websocket_endpoint(ws: WebSocket, lobby_id: str, player_id: str):
    await ws.accept()
    await register(lobby_id, player_id, ws)

    # отправляем актуальное состояние лобби новому подключившемуся
    lobby = lobby_manager.get_lobby(lobby_id)
    if lobby:
        await ws.send_json({"type": "lobby_update", "payload": lobby.dict()})
    try:
        while True:
            data = await ws.receive_json()
            msg_type = data.get("type")
            payload = data.get("payload", {})

            if msg_type == "play_card":
                try:
                    game = game_manager.play_card(
                        payload.get("game_id"),
                        player_id,
                        payload.get("card_id"),
                        payload.get("target_id"),
                        payload.get("targets_ids"),
                    )
                    await broadcast(lobby_id, {"type": "game_state", "payload": game.dict()})
                except GameException as e:
                    await ws.send_json({"type": "error", "payload": str(e)})

            elif msg_type == "end_turn":
                try:
                    game = game_manager.end_turn(payload.get("game_id"), player_id)
                    await broadcast(lobby_id, {"type": "game_state", "payload": game.dict()})
                except GameException as e:
                    await ws.send_json({"type": "error", "payload": str(e)})

            elif msg_type == "discard_cards":
                try:
                    game = game_manager.discard_cards(
                        payload.get("game_id"),
                        player_id,
                        payload.get("card_ids", []),
                    )
                    await broadcast(lobby_id, {"type": "game_state", "payload": game.dict()})
                except GameException as e:
                    await ws.send_json({"type": "error", "payload": str(e)})

            elif msg_type == "add_dummy":
                try:
                    game = game_manager.add_dummy(payload.get("game_id"))
                    await broadcast(lobby_id, {"type": "game_state", "payload": game.dict()})
                except GameException as e:
                    await ws.send_json({"type": "error", "payload": str(e)})
            
            elif msg_type == "remove_dummy":
                try:
                    game = game_manager.remove_dummy(payload.get("game_id"), payload.get("dummy_id"))
                    await broadcast(lobby_id, {"type": "game_state", "payload": game.dict()})
                except GameException as e:
                    await ws.send_json({"type": "error", "payload": str(e)})

            elif msg_type == "forfeit_game":
                try:
                    game = game_manager.forfeit_game(payload.get("game_id"), player_id)
                    await broadcast(lobby_id, {"type": "game_state", "payload": game.dict()})
                    # Send player back to lobby
                    lobby = lobby_manager.get_lobby(lobby_id)
                    if lobby:
                        await ws.send_json({"type": "lobby_update", "payload": lobby.dict()})
                except GameException as e:
                    await ws.send_json({"type": "error", "payload": str(e)})

    except WebSocketDisconnect:
        await unregister(lobby_id, player_id)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 