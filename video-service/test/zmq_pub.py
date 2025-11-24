import zmq
import asyncio
import zmq.asyncio
import random
import sys
import time
import numpy as np
import pickle

port = "5556"

context = zmq.asyncio.Context()
socket = context.socket(zmq.PUB)
socket.bind(f"tcp://*:{port}")

async def send_msg():
    await asyncio.sleep(0.5)  # 🔥 allow subscribers to connect
    i = 0
    while True:
        data = np.array([[i]], dtype=np.int32)
        i += 1
        print("Sending:", data)

        # Send array as 3-part multipart message:
        # [dtype, shape, raw_bytes]
        socket.send_multipart([
            str(data.dtype).encode(),
            str(data.shape).encode(),
            data.tobytes()
        ])
        await asyncio.sleep(1)

asyncio.run(send_msg())

# video_path = "/workspace/data/test_gouget_cut.mp4"
# uri = "ws://172.26.128.105:8081"
# # uri = "ws://0.0.0.0:8080"
# FPS = 30

# async def sender():
#     cap = cv2.VideoCapture(video_path)
#     async with websockets.connect(uri=uri) as ws:
#         while True:
#             ret, frame = cap.read()
#             if not ret:
                
#                 raise KeyboardInterrupt
#             # Downscale if needed
#             frame = cv2.resize(frame, (640, 480))
#             await ws.send(frame.tobytes())
#             await asyncio.sleep(1/FPS)  # target FPS
#     cap.release()

# asyncio.run(sender())
