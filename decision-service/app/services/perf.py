import zmq
import zmq.asyncio
import asyncio
from app.services.connection_manager import manager 
import numpy as np
from app.core import state

async def video_task() :
    async with state.video_lock : 
        state.video_status = state.VideoStatus.RUNNING
    
    try :
        await stream_video()
    finally : 
        async with state.gaze_visualisation_lock : 
            state.gaze_visualisation_status = state.GazeVisualisationStatus.NOT_RUNNING

async def stream_video() :
    context = zmq.asyncio.Context()
    ip_video_service = ""
    port_video_service = ""