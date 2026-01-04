import zmq
import zmq.asyncio
import asyncio
from app.services.connection_manager import manager 
import numpy as np
from app.core import state
import cv2



async def video_task() :
    async with state.video_lock : 
        state.video_status = state.VideoStatus.RUNNING
    
    try :
        await stream_video()
    finally : 
        async with state.gaze_visualisation_lock : 
            state.gaze_visualisation_status = state.GazeVisualisationStatus.NOT_RUNNING

async def stream_video() :
    
    async def _recv_multipart_async(socket):
        """Yield multipart messages from an async zmq socket."""
        while True:
            try:
                parts = await socket.recv_multipart()
            except Exception:
                # Socket closed or interrupted
                return
            yield parts
    
    context = zmq.asyncio.Context()
    ip_vs = "172.26.128.105"
    port_vs = "8080"
    
    socket_video_service = context.socket(zmq.SUB)
    socket_video_service.setsockopt(zmq.SUBSCRIBE, b"")
    socket_video_service.setsockopt(zmq.RCVHWM, 1)
    socket_video_service.setsockopt(zmq.LINGER, 0)
    uri = f"tcp://{ip_vs}:{port_vs}"
    
    socket_video_service.connect(uri)
    
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
        
        _, jpeg = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        # print("send")
        await manager.broadcast(jpeg.tobytes(), "video")