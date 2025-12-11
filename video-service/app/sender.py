import cv2
import asyncio
import struct
import zmq
import zmq.asyncio
import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--stream_loop', action='store_true')
parser.add_argument("-f", "--input_file", type=str, default="/workspace/data/test_gouget_cut.mp4")

parser.add_argument("--port", type=int, default=8080)
parser.add_argument("--fps", type=int, default=30)

args = parser.parse_args()

stream_loop = args.stream_loop
video_path = args.input_file 
port = args.port
uri = f"tcp://*:{port}"

FPS = args.fps
HEIGHT = 640
WIDTH = 480

context = zmq.asyncio.Context()

async def sender():
    socket = context.socket(zmq.PUB)
    socket.bind(uri)
    await asyncio.sleep(0.5)
    print(f"Start sending the video : {uri}")

    
    while True : 
        cap = cv2.VideoCapture(video_path)
        try : 
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
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
        
        if not(stream_loop) : 
            break

asyncio.run(sender())
