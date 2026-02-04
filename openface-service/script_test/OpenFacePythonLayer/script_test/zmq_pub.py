import zmq
import random
import sys
import time
import zmq.asyncio
import asyncio
import websockets
import numpy as np
import cv2
import subprocess
import json
import pandas as pd

# port = "5556"
# if len(sys.argv) > 1:
#     port =  sys.argv[1]
#     int(port)

# context = zmq.Context()
# socket = context.socket(zmq.PUB)
# socket.bind(f"tcp://*:{port}" )

# while True:
#     topic = random.randrange(9999,10005)
#     messagedata = random.randrange(1,215) - 80
#     print((topic, messagedata))
#     socket.send_string(f"{topic}, {messagedata}")
#     time.sleep(1)