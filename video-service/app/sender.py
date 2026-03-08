import cv2
import asyncio
import zmq
import zmq.asyncio
import argparse
import platform
import subprocess
import numpy as np
from utils import get_ip_adress
# On récupère les arguments 

parser = argparse.ArgumentParser()

parser.add_argument('--stream_loop', action='store_true')
parser.add_argument("-f", "--input_file", type=str, default="/workspace/data/test_gouget_cut.mp4")
parser.add_argument("--device", type=int, default=-1)
parser.add_argument("--port", type=int, default=8080)
parser.add_argument("--fps", type=int, default=30)
parser.add_argument("--width", type=int, default=640, help="Output frame width in pixels")
parser.add_argument("--height", type=int, default=480, help="Output frame height in pixels")
args = parser.parse_args()


ip_adress = get_ip_adress()
print(f"IP adress detected : {ip_adress}")
# On charge les variables

stream_loop = args.stream_loop
video_path = args.input_file 
port = args.port
uri = f"tcp://{ip_adress}:{port}"
device = args.device # 0si on veut récupérer la webcam de l'app areil 

if device == -1 : 
    input_video = video_path
else :
    input_video = device

FPS = args.fps
WIDTH = args.width
HEIGHT = args.height

context = zmq.asyncio.Context()

async def sender():
    socket = context.socket(zmq.PUB)
    socket.setsockopt(zmq.SNDHWM, 1)
    socket.bind(uri)
    await asyncio.sleep(0.5)
    print(f"On envoie la vidéo à l'adresse : {uri}")

    
    while True : 
        cap = cv2.VideoCapture(input_video)
        try : 
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Fin de la vidéo")
                    break
                # Resize frames to the configured output dimensions
                frame = cv2.resize(frame, (WIDTH, HEIGHT))
                frame = np.flip(frame, axis=1)

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
