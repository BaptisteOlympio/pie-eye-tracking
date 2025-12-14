from typing import Dict
from fastapi import WebSocket, WebSocketDisconnect


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[Dict[str, WebSocket]] = []

    async def connect(self, websocket: WebSocket, client_type : str):
        await websocket.accept()
        print("création de la connection avec client type : ", client_type)
        self.active_connections.append({"client_type" : client_type, "websocket" : websocket})
        print("nombre de connection :", len(self.active_connections))

    def disconnect(self, websocket_or_conn):
        """Disconnect either by WebSocket object or by connection dict.
        This makes the API robust when callers pass either a dict or the websocket itself.
        """
        # If caller passed the connection dict directly, just remove it if present
        if isinstance(websocket_or_conn, dict):
            if websocket_or_conn in self.active_connections:
                self.active_connections.remove(websocket_or_conn)
            return

        # Otherwise, assume it's a WebSocket and find the matching connection dict
        for dict_websocket in list(self.active_connections):
            if websocket_or_conn == dict_websocket["websocket"]:
                self.active_connections.remove(dict_websocket)
                return


    async def broadcast(self, message: dict, client_type):
        disconnected = []
        # iterate over a copy of the list to avoid issues removing items while iterating
        for conn in list(self.active_connections):
            if conn["client_type"] == client_type : 
                try:
                    await conn["websocket"].send_json(message)
                except (WebSocketDisconnect, RuntimeError, ConnectionResetError):
                    # mark the websocket for removal; store the actual WebSocket object
                    disconnected.append(conn["websocket"])

        for ws in disconnected:
            self.disconnect(ws)

manager = ConnectionManager()