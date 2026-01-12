import zmq
import zmq.asyncio
import asyncio
from app.services.connection_manager import manager 
import numpy as np
from app.core import state
import cv2
from app.services import process_frame



async def video_task() :
    print("------------LAUCH STREAM TASK--------------")
    async with state.video_lock : 
        state.video_status = state.VideoStatus.RUNNING
    
    try :
        await stream_video()
    finally : 
        async with state.gaze_visualisation_lock : 
            state.gaze_visualisation_status = state.GazeVisualisationStatus.NOT_RUNNING

async def stream_video() :
    print("------------LAUCH STREAM VIDEO--------------")
    # previous_update = -1
    while True :
        frame = process_frame.process_frame.latest_frame
        landmark = process_frame.process_frame.latest_landmark
        # latest_update = process_frame.process_frame.latest_update
        
        # if latest_update == previous_update : 
        #     print(latest_update, previous_update)
        #     continue
        # previous_update = latest_update
        
        try : 
            frame_landmark = frame.copy()
            for face_keypoint in landmark : 
                frame_landmark = cv2.circle(frame_landmark, 
                                            face_keypoint, 
                                            radius=3, 
                                            color=(0,0,255), 
                                            thickness=-1)
            _, jpeg = cv2.imencode(".jpg", 
                                   frame_landmark, 
                                   [cv2.IMWRITE_JPEG_QUALITY, 80])
            # print("ok")
            await manager.broadcast(jpeg.tobytes(), "video")
            # TODO ici pas mettre de sleep mais plutôt mettre une condition pour savoir si la valeur à changé. 
            await asyncio.sleep(1/30)
            
        except Exception as e :
            print(e)
            await asyncio.sleep(1)
            continue