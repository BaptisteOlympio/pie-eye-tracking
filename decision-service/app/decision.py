import zmq
import zmq.asyncio
import asyncio

async def sub():
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.SUB)

    socket.connect("tcp://172.26.128.105:8081")
    socket.setsockopt(zmq.SUBSCRIBE, b"")
    print("Listening on : tcp://172.26.128.105:8081...")

    while True:
        data = await socket.recv_json()
        print(f"frame : {data["frame"]}, x : {data["gaze_angle_x"]}, y : {data["gaze_angle_y"]}")

asyncio.run(sub())
