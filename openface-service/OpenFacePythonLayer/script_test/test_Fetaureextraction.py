import subprocess as sp
import sys
import cv2
import zmq
import asyncio
import zmq.asyncio
import numpy as np
import pandas as pd
import time

port = "8080"
ip = "video-servicee" #jsute en phase de test
time_list = []
context = zmq.asyncio.Context()
socket = context.socket(zmq.SUB)
socket.setsockopt(zmq.SUBSCRIBE, b"") 
socket.connect(f"tcp://{ip}:{port}")

print(f"Connected to server at {ip}:{port}")


async def recv_msg():
    i=0
    while True:
        if i>20:
            print("Average processing time:", sum(time_list)/len(time_list))
            sys.exit()
        dtype_b, shape_b, data_b = await socket.recv_multipart()
        dtype = np.dtype(dtype_b.decode())
        shape = tuple(map(int, shape_b.decode().strip("()").split(",")))
        
        arr = np.frombuffer(data_b, dtype=dtype).reshape(shape)
        cv2.imwrite("./current_img.png", arr)
        # print(arr)
        t0 = time.time()
        OpenFace = sp.run(['FeatureExtraction', '-f', './current_img.png', '-of', 'OF_img.csv'])
        t1 = time.time()
        time_list.append(t1 - t0)
        current_data = pd.read_csv("./processed/OF_img.csv")
        gaze_data = current_data[["gaze_angle_x","gaze_angle_y"]]

        print(gaze_data)
        
        await asyncio.sleep(0.5)
        i += 1


asyncio.run(recv_msg())

# Process 5 updates
# total_value = 0
# for update_nbr in range (5):
#     string = socket.recv_string()
#     topic, messagedata = string.split()
#     total_value += int(messagedata)
#     print (topic, messagedata)

# print ("Average messagedata value for topic '%s' was %dF" % (topicfilter, total_value / update_nbr))