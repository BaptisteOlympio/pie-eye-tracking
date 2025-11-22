import cv2
import asyncio
import struct
import zmq
import zmq.asyncio


video_path = "/workspace/data/test_gouget_cut.mp4"
# uri = "ws://172.26.128.105:8081"
port = "8080"
uri = f"tcp://*:{port}"

FPS = 15
HEIGHT = 640
WIDTH = 480

context = zmq.asyncio.Context()
socket = context.socket(zmq.PUB)
socket.bind(uri)

async def sender():
    await asyncio.sleep(0.5)
    print(f"Start sending the video : {uri}")
    for _ in range(5) : 
        cap = cv2.VideoCapture(video_path)
        try : 
            while True:
                ret, frame = cap.read()
                if not ret:
                    raise KeyboardInterrupt
                # Downscale if needed
                frame = cv2.resize(frame, (HEIGHT, WIDTH))
                # print(frame.shape)
                await socket.send_multipart([
                    str(frame.dtype).encode(),
                    str(frame.shape).encode(),
                    frame.tobytes()
                ])
                await asyncio.sleep(1/FPS)  # target FPS
        except :
            cap.release()

asyncio.run(sender())
