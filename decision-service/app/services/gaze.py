import zmq
import zmq.asyncio
import asyncio
from app.services.connection_manager import manager 
from time import time
import numpy as np
from app.core import state

context = zmq.asyncio.Context()

calibration_data = {
    "data": {
        "gax_max": 0.0728,
        "gax_min": -0.195,
        "gay_max": 0.177,
        "gay_min": -0.150,
    }
} 


ip_openface_service = "172.26.128.105"
port_openface_service = "8081"
uri_openface_service = f"tcp://{ip_openface_service}:{port_openface_service}"

# -------------------------------
# Gaze Visualisation
# -------------------------------
async def gaze_visualisation() :
    async with state.gaze_visualisation_lock: 
        state.gaze_visualisation_status = state.GazeVisualisationStatus.RUNNING
    
    try :
        await process_gaze_visualisation()
    finally : 
        async with state.gaze_visualisation_lock : 
            state.gaze_visualisation_status = state.GazeVisualisationStatus.NOT_RUNNING

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
    socket.setsockopt(zmq.RCVTIMEO, 5000)
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
async def calibration_task() :
    async with state.calibration_lock : 
        state.calibration_status = state.CalibrationStatus.RUNNING
    
    try :
        await process_calibration()
    finally : 
        async with state.calibration_lock : 
            state.calibration_status = state.CalibrationStatus.IDLE

async def process_calibration() :
    global calibration_data
    
    socket = context.socket(zmq.SUB)
    socket.setsockopt(zmq.SUBSCRIBE, b"")
    socket.setsockopt(zmq.RCVHWM, 1)
    socket.setsockopt(zmq.LINGER, 0)
    socket.setsockopt(zmq.RCVTIMEO, 5000)
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
    while time() - start_time < 20 :
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
    
    



