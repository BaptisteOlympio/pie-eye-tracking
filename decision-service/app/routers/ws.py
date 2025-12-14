from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.connection_manager import manager
import asyncio

ws_router = APIRouter()

@ws_router.websocket("/ws")
async def websocket_endpoint(websocket : WebSocket) :
    client_type = websocket.query_params.get("type")
    print("type de client pour la connection", client_type)
    await manager.connect(websocket, client_type=client_type)
    try:
        while True:
            await asyncio.sleep(0.03)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("WebSocket disconnected")