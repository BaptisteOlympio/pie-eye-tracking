import asyncio
import numpy as np
import cv2
import zmq
import zmq.asyncio
import argparse
import sys

# On récupère les arguments 

parser = argparse.ArgumentParser()
parser.add_argument("--ip", type=str)
parser.add_argument("--port", type=str)
args = parser.parse_args()

ip = args.ip
port = args.port
uri = f"tcp://{ip}:{port}"

latest_frame = None

context = zmq.asyncio.Context()
socket = context.socket(zmq.SUB)
socket.connect(uri)

socket.setsockopt(zmq.SUBSCRIBE, b"")

async def recv_msg():
    global latest_frame
    while True : 
        dtype_b, shape_b, data_b = await socket.recv_multipart()
        dtype = np.dtype(dtype_b.decode())
        shape = tuple(map(int, shape_b.decode().strip("()").split(",")))
        
        arr = np.frombuffer(data_b, dtype=dtype).reshape(shape)
        # print("Received:", arr.shape)
        latest_frame = arr

async def display_loop():
    global latest_frame
    while True:
        if latest_frame is not None:
            cv2.imshow("test", latest_frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            sys.exit(0)
            break
        
        await asyncio.sleep(0.01)  # yield to the event loop

async def main():
    # Run both tasks concurrently
    await asyncio.gather(
        recv_msg(),
        display_loop(),
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    finally:
        cv2.destroyAllWindows()