import zmq
import zmq.asyncio
import asyncio

# Du wiki de OpenFace : gaze_angle_x, gaze_angle_y sont les angles des deux yeux en moyenne.
# gaze_angle_x s'occupe de la direction gauche-droite
# gaze_angle_y s'occupe de la direction haut-bas



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
