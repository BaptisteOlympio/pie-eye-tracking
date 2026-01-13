import zmq
import zmq.asyncio
import asyncio
import numpy as np

import sys
sys.path.append("/workspace/app/services")
import grpc
import app.services.openfaceservice_pb2_grpc as openfaceservice_pb2_grpc
import app.services.openfaceservice_pb2 as openfaceservice_pb2
from app.core import state


class ProcessFrame() :
    def __init__(self):
        self.latest_frame = np.empty(shape=0)
        self.latest_landmark = []
        self.context = zmq.asyncio.Context()
    
    def initializeConnection(self, ip_vs, port_vs) -> bool :
        # Init de zmq
        
        self.ip_vs = ip_vs
        self.port_vs = port_vs
        
        self.socket_video_service = self.context.socket(zmq.SUB)
        self.socket_video_service.setsockopt(zmq.SUBSCRIBE, b"")
        self.socket_video_service.setsockopt(zmq.RCVHWM, 1)
        self.socket_video_service.setsockopt(zmq.LINGER, 0)
        uri = f"tcp://{ip_vs}:{port_vs}"
        
        self.socket_video_service.connect(uri)
        # TODO Here check if the connection exist, otherwise return false, so far return true as we assume the connection exist
        return True

    
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
        
        async with grpc.aio.insecure_channel("openface-service:8081") as channel :
            stub = openfaceservice_pb2_grpc.OpenFaceServiceStub(channel)
            
            async for parts in _recv_multipart_async(self.socket_video_service):
                if not parts or len(parts) != 3:
                    print("problem part not lenght equal 3")
                    continue
                dtype_b, shape_b, data_b = parts
                dtype = np.dtype(dtype_b.decode())
                shape = tuple(map(int, shape_b.decode().strip("()").split(",")))
                
                try:
                    frame = np.frombuffer(data_b, dtype=dtype).reshape(shape)
                except Exception:
                    print("frame canot be transform as numpy array")
                    continue
                
                if frame.size == 0:
                    print("frame size is null")
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
                
            print("loop finished")
            
process_frame = ProcessFrame()

async def process_frame_task(ip_vs, port_vs) :
    async with state.video_service_connection_lock :
        if process_frame.initializeConnection(ip_vs=ip_vs, port_vs=port_vs) :
            state.video_service_connection_status = state.VideoServiceConnection.CONNECTED
        else :
            # TODO Do something if the connection does not exist.
            print("URI does not exist")
            return
    
    try :
        await process_frame.process_frame()
    finally :
        async with state.video_service_connection_lock :
            state.video_service_connection_status = state.VideoServiceConnection.DISCONNECTED
