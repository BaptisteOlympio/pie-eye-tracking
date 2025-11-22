# Ce module va recevoir les frame par websocket et les écrit dans /dev/video0 avec ffmpeg.

import asyncio
import numpy as np
import cv2
import subprocess
import json
import pandas as pd
import zmq
import zmq.asyncio

context = zmq.asyncio.Context()

WIDTH = 640
HEIGHT = 480


async def write_frame():
    port_video_service = "8080"
    socket_video_service = context.socket(zmq.SUB)
    socket_video_service.connect(f"tcp://172.26.128.105:{port_video_service}")
    socket_video_service.setsockopt(zmq.SUBSCRIBE, b"")
    
    ffmpeg = subprocess.Popen([
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "bgr24",
        "-s", f"{WIDTH}x{HEIGHT}", "-r", "30",
        "-i", "-", "-f", "v4l2", "/dev/video0"
    ], stdin=subprocess.PIPE)
    
    while True : 
        dtype_b, shape_b, data_b = await socket_video_service.recv_multipart()
        dtype = np.dtype(dtype_b.decode())
        shape = tuple(map(int, shape_b.decode().strip("()").split(",")))
        frame = np.frombuffer(data_b, dtype=dtype).reshape(shape)
        # print(frame.shape)
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, ffmpeg.stdin.write, frame.tobytes())

async def gaze_sender() :
    columns = ["frame", "face_id", "timestamp", "confidence", "success", "gaze_0_x",
               "gaze_0_y", "gaze_0_z", "gaze_1_x", "gaze_1_y", "gaze_1_z", 
               "gaze_angle_x", "gaze_angle_y"]

    
    port_gaze_data = "8081"
    
    socket_gaze_sender = context.socket(zmq.PUB)
    socket_gaze_sender.bind(f"tcp://*:{port_gaze_data}")
    
    await asyncio.sleep(0.5)
    
    while True :
        try : 
            df = pd.read_csv("/workspace/data/data.csv")
        except pd.errors.EmptyDataError :
            pass
        last_row = df.tail(1)
        selected_last_row = last_row[columns].to_dict("records")[0]
        # print(type(selected_last_row))
        await socket_gaze_sender.send_json(selected_last_row)
        await asyncio.sleep(1/30)
#     # uri_decision = "ws://172.26.128.105:8082"
#     # async with websockets.connect(uri=uri_decision) as ws:
#     while True:
#         # df = pd.read_csv("/workspace/data/data.csv")
#         # last_row = df.tail(1)
#         # print(last_row)
#         # print(type(last_row))
#         # data_string = json.dump()
#         # await ws.send(data_string)
#         await asyncio.sleep(1)  # target FPS
    


async def main() :
    await asyncio.gather(
        write_frame(),
        gaze_sender()
    )

if __name__ == "__main__" :
    asyncio.run(main())
    # asyncio.run(write_frame())