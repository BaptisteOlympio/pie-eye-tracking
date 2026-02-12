import asyncio
import json
import os
from app.services.connection_manager import manager 
from time import time
import numpy as np
from app.core import state
from app.services import process_frame


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
    
    while True : 

        frame = process_frame.process_frame.latest_frame
        landmark = process_frame.process_frame.latest_landmark
        gaze = process_frame.process_frame.latest_gaze

        # data = await socket.recv_json()
        # x = min(max((data["gaze_angle_x"] - gax_min)/(gax_max - gax_min), 0), 1)
        # y = min(max((data["gaze_angle_y"] - gay_min)/(gay_max - gay_min), 0), 1)``
        try:
            gaze = {
                "x" : float(gaze[0]),
                "y" : float(gaze[1])
            }
            await manager.broadcast(gaze, client_type="visualisation")
        except Exception as e:
            print(f"Erreur lors de l'envoi des données de gaze visualisation : {e}")
        await asyncio.sleep(1/30)
