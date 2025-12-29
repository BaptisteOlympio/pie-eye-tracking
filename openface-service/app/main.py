import asyncio
import numpy as np
import zmq
import zmq.asyncio
import argparse
import pyopenface

parser = argparse.ArgumentParser()
parser.add_argument("--ip_vs", type=str)
parser.add_argument("--port_vs", type=str)
args = parser.parse_args()

ip_vs = args.ip_vs
port_vs = args.port_vs

context = zmq.asyncio.Context()

print("----------- DETECTOR INIT ------------")
detector = pyopenface.Detector("/usr/local/etc/OpenFace/model/main_ceclm_general.txt", 
                                "/usr/local/etc/OpenFace/classifiers/haarcascade_frontalface_alt2.xml",
                                "/usr/local/etc/OpenFace/model/mtcnn_detector/MTCNN_detector.txt")

async def _recv_multipart_async(socket):
    """Yield multipart messages from an async zmq socket."""
    while True:
        try:
            parts = await socket.recv_multipart()
        except Exception:
            # Socket closed or interrupted
            return
        yield parts

async def init_socket_sub() :
    socket_video_service = context.socket(zmq.SUB)
    socket_video_service.setsockopt(zmq.SUBSCRIBE, b"")
    socket_video_service.setsockopt(zmq.RCVHWM, 1)
    socket_video_service.setsockopt(zmq.LINGER, 0)
    uri = f"tcp://{ip_vs}:{port_vs}"
    print(f"starting to listen on : {uri}")
    socket_video_service.connect(uri)
    return socket_video_service

async def init_socket_pub() :
    port_gaze_data = "8081"
    socket_gaze_sender = context.socket(zmq.PUB)
    socket_gaze_sender.bind(f"tcp://*:{port_gaze_data}")
    await asyncio.sleep(0.5)  # let subscribers connect
    return socket_gaze_sender

async def main() :
    socket_video_service = await init_socket_sub()
    socket_gaze_sender = await init_socket_pub()
    
    async for parts in _recv_multipart_async(socket_video_service):
        # We check that we receive 3 part : datatype, data shape and data itself
        if not parts or len(parts) != 3:
            continue
        dtype_b, shape_b, data_b = parts
        dtype = np.dtype(dtype_b.decode())
        shape = tuple(map(int, shape_b.decode().strip("()").split(",")))
        
        try:
            frame = np.frombuffer(data_b, dtype=dtype).reshape(shape)
        except Exception:
            # corrupted frame
            continue
        
        if frame.size == 0:
            continue
        
        # It's important to call landmarkinvideo before getgaze, getgaze don't calculate the landmark. 
        result = detector.landmarkinvideo(frame)
        gaze = detector.getgaze(frame)
        
        await socket_gaze_sender.send_json(gaze)
        
        
    

if __name__ == "__main__" :
    asyncio.run(main=main())
    