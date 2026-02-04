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
        gaze = process_frame.process_frame.latest_gaze
        # latest_update = process_frame.process_frame.latest_update
        
        # if latest_update == previous_update : 
        #     print(latest_update, previous_update)
        #     continue
        # previous_update = latest_update
        
        try : 
            frame_landmark = frame.copy()
            # Dessiner les landmarks en rouge
            for face_keypoint in landmark : 
                frame_landmark = cv2.circle(frame_landmark, 
                                            face_keypoint, 
                                            radius=3, 
                                            color=(0,0,255), 
                                            thickness=-1)
            # Dessiner le point de gaze
            if gaze and len(gaze) >= 2:
                height, width = frame_landmark.shape[:2]
                gaze_x = float(gaze[0])
                gaze_y = float(gaze[1])
                # gaze_x = max(-1.0, min(1.0, gaze_x))
                # gaze_y = max(-1.0, min(1.0, gaze_y))
                px = int((gaze_x + 1) * 0.5 * (width - 1))
                py = int((gaze_y + 1) * 0.5 * (height - 1))
                frame_landmark = cv2.circle(frame_landmark,
                                            (px, py),
                                            radius=6,
                                            color=(0, 255, 0),
                                            thickness=-1)
            _, jpeg = cv2.imencode(".jpg", 
                                   frame_landmark, 
                                   [cv2.IMWRITE_JPEG_QUALITY, 80])
            await manager.broadcast(jpeg.tobytes(), "video")
            
            
            # Sending gaze data
            if gaze and len(gaze) >= 2:
                # json format to be able to send them via websocket
                gaze_data = {
                    "gaze_x": float(gaze[0]),
                    "gaze_y": float(gaze[1])
                }
                await manager.broadcast(gaze_data, "gaze")
            
            # TODO ici pas mettre de sleep mais plutôt mettre une condition pour savoir si la valeur à changé. 
            await asyncio.sleep(1/30)
            
        except Exception as e :
            # print(e)
            await asyncio.sleep(1)
            continue