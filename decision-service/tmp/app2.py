import asyncio
import json
from contextlib import asynccontextmanager
from typing import Dict
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import zmq
import zmq.asyncio
from time import time
import numpy as np

ip_openface_service = "172.26.128.105"
port_openface_service = "8081"
uri_openface_service = f"tcp://{ip_openface_service}:{port_openface_service}"

last_data = None

calibration_data = {
    "data": {
        "gax_max": 0.0728,
        "gax_min": -0.195,
        "gay_max": 0.177,
        "gay_min": -0.150,
    }
}  

context = zmq.asyncio.Context()


# -------------------------------
# Gaze Visualisation
# -------------------------------
async def process_gaze_visualisation() :
    global calibration_data
    
    gax_max = calibration_data["data"]["gax_max"]
    gax_min = calibration_data["data"]["gax_min"]
    gay_max = calibration_data["data"]["gay_max"]
    gay_min = calibration_data["data"]["gay_min"]

    
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, b"")
    socket.setsockopt(zmq.RCVHWM, 1)
    socket.setsockopt(zmq.LINGER, 0)
    socket.connect(uri_openface_service)
    
    print(f"On écoute l'openface service sur : {uri_openface_service} pour la visualisation du gaze")
    await asyncio.sleep(0.5) # on attend un peu
    
    while True : 
        data = await socket.recv_json()
        x = min(max((data["gaze_angle_x"] - gax_min)/(gax_max - gax_min), 0), 1)
        y = min(max((data["gaze_angle_y"] - gay_min)/(gay_max - gay_min), 0), 1)
        gaze = {
            "x" : x,
            "y" : y
        }
        await manager.broadcast(message=gaze, client_type="visualisation")
        await asyncio.sleep(0.02)


# -------------------------------
# Calibration
# -------------------------------
async def process_calibration() :
    global calibration_data
    
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, b"")
    socket.setsockopt(zmq.RCVHWM, 1)
    socket.setsockopt(zmq.LINGER, 0)
    socket.connect(uri_openface_service)
    
    print(f"On écoute l'openface service sur : {uri_openface_service} pour la calibration")
    
    gaze_angle_x_list = []
    gaze_angle_y_list = []
    await asyncio.sleep(1) # on attend une seconde le temps que le websocket soit créé
    
    message = {"data" : {"value" : "Début de la calibration"}}
    await manager.broadcast(message=message, client_type="calibration")
    await asyncio.sleep(1)
    
    message = {"data" : {"value" : "Regardez à droite à fond"}}
    await manager.broadcast(message=message, client_type="calibration")
    
    start_time = time()
    while time() - start_time < 30 :
        data = await socket.recv_json()
        gaze_angle_x_list.append(data["gaze_angle_x"])
        gaze_angle_y_list.append(data["gaze_angle_y"])
    
    # message = {"data" : {"value" : "Regardez à gauche à fond"}}
    # await manager.broadcast(message=message, client_type="calibration")
    
    # start_time = time()
    # while time() - start_time < 5 :
    #     data = await socket.recv_json()
    #     gaze_angle_x_list.append(data["gaze_angle_x"])
    #     gaze_angle_y_list.append(data["gaze_angle_y"])
    
    # message = {"data" : {"value" : "Regardez en haut à fond"}}
    # await manager.broadcast(message=message, client_type="calibration")
    
    # start_time = time()
    # while time() - start_time < 5 :
    #     data = await socket.recv_json()
    #     gaze_angle_x_list.append(data["gaze_angle_x"])
    #     gaze_angle_y_list.append(data["gaze_angle_y"])
    
    # message = {"data" : {"value" : "Regardez en bas à fond"}}
    # await manager.broadcast(message=message, client_type="calibration")
    
    # start_time = time()
    # while time() - start_time < 5 :
    #     data = await socket.recv_json()
    #     gaze_angle_x_list.append(data["gaze_angle_x"])
    #     gaze_angle_y_list.append(data["gaze_angle_y"])
    
    gaze_angle_x_np = np.stack(gaze_angle_x_list)
    gaze_angle_x_np = gaze_angle_x_np[~np.isnan(gaze_angle_x_np)]
    gaze_angle_y_np = np.stack(gaze_angle_y_list)
    gaze_angle_y_np = gaze_angle_y_np[~np.isnan(gaze_angle_y_np)]
    
    gax_max = gaze_angle_x_np.max()
    gax_min = gaze_angle_x_np.min()
    gay_max = gaze_angle_y_np.max()
    gay_min = gaze_angle_y_np.min()
    
    message = {"data" : 
        {"value" : f"Fin calibration, nb frame {gaze_angle_x_np.shape}"}
        }
    await manager.broadcast(message=message, client_type="calibration")

    calibration_data = {
        "data": {
            "gax_max": float(gax_max),
            "gax_min": float(gax_min),
            "gay_max": float(gay_max),
            "gay_min": float(gay_min),
        }
    }
    
    socket.close()  

    

# -------------------------------
# WebSocket manager
# -------------------------------
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

# -------------------------------
# FastAPI app
# -------------------------------
app = FastAPI()

# Serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/gaze_visualisation")
async def get_index():
    asyncio.create_task(process_gaze_visualisation())
    with open("static/gaze_visualisation/index.html") as f:
        return HTMLResponse(content=f.read())

@app.get("/calibration")
async def get_calibration() :
    asyncio.create_task(process_calibration())
    with open("static/calibration/calibration.html") as f :
        return HTMLResponse(content=f.read())

@app.get("/interface")
async def get_interface() :
    with open("static/interface.html") as f :
        return HTMLResponse(content=f.read())
    
    
# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    client_type = websocket.query_params.get("type")
    print("type de client pour la connection", client_type)
    await manager.connect(websocket, client_type=client_type)
    try:
        while True:
            await asyncio.sleep(0.03)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("WebSocket disconnected")