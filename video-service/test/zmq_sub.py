import sys
import zmq
import asyncio
import zmq.asyncio
import numpy as np

port = "8080"

context = zmq.asyncio.Context()
socket = context.socket(zmq.SUB)
socket.connect(f"tcp://172.26.128.1:{port}")

socket.setsockopt(zmq.SUBSCRIBE, b"")

async def recv_msg():
    while True:
        dtype_b, shape_b, data_b = await socket.recv_multipart()
        dtype = np.dtype(dtype_b.decode())
        shape = tuple(map(int, shape_b.decode().strip("()").split(",")))
        
        arr = np.frombuffer(data_b, dtype=dtype).reshape(shape)
        print("Received:", arr.shape)

asyncio.run(recv_msg())

# Process 5 updates
# total_value = 0
# for update_nbr in range (5):
#     string = socket.recv_string()
#     topic, messagedata = string.split()
#     total_value += int(messagedata)
#     print (topic, messagedata)

# print ("Average messagedata value for topic '%s' was %dF" % (topicfilter, total_value / update_nbr))