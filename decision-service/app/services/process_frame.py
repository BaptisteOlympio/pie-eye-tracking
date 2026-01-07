import zmq
import zmq.asyncio
import asyncio
import numpy as np

import sys
sys.path.append("/workspace/app/services")
import grpc
import openfaceservice_pb2_grpc
import openfaceservice_pb2


class ProcessFrame() :
    def __init__(self, ip_vs, port_vs):
        # Init de zmq
        self.context = zmq.asyncio.Context()
        self.ip_vs = ip_vs
        self.port_vs = port_vs
        
        self.socket_video_service = self.context.socket(zmq.SUB)
        self.socket_video_service.setsockopt(zmq.SUBSCRIBE, b"")
        self.socket_video_service.setsockopt(zmq.RCVHWM, 1)
        self.socket_video_service.setsockopt(zmq.LINGER, 0)
        uri = f"tcp://{ip_vs}:{port_vs}"
        
        self.socket_video_service.connect(uri)
    
        self.latest_frame = np.empty(shape=0)
        self.latest_landmark = []
        self.latest_update = 0
    
    async def process_frame(self) :
        async def _recv_multipart_async(socket):
            """Yield multipart messages from an async zmq socket."""
            while True:
                try:
                    parts = await socket.recv_multipart()
                except Exception:
                    # Socket closed or interrupted
                    return
                yield parts
        
        async with grpc.aio.insecure_channel("172.26.128.105:8081") as channel :
            stub = openfaceservice_pb2_grpc.OpenFaceServiceStub(channel)
            
            async for parts in _recv_multipart_async(self.socket_video_service):
                if not parts or len(parts) != 3:
                    continue
                dtype_b, shape_b, data_b = parts
                dtype = np.dtype(dtype_b.decode())
                shape = tuple(map(int, shape_b.decode().strip("()").split(",")))
                
                try:
                    frame = np.frombuffer(data_b, dtype=dtype).reshape(shape)
                except Exception:
                    continue
                
                if frame.size == 0:
                    continue
                
                response = await stub.GetLandmark(openfaceservice_pb2.Frame(
                    frame=data_b,
                    dtype=dtype_b,
                    shape=shape_b
                ))
                landmark = []
                for point in response.landmark :
                    landmark.append((int(point.x), int(point.y)))
                    
                # print(landmark[0])
                
                self.latest_frame = frame
                self.latest_landmark = landmark
                self.update = (self.update + 1) % 100
            
            

process_frame = ProcessFrame(ip_vs="172.26.128.105", port_vs = "8080")
    