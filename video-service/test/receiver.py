import asyncio
import websockets
import subprocess
import numpy as np
import cv2

WIDTH, HEIGHT = 640, 480
# ffmpeg = subprocess.Popen([
#     "ffmpeg", "-y",
#     "-f", "rawvideo", "-pix_fmt", "bgr24",
#     "-s", f"{WIDTH}x{HEIGHT}", "-r", "30",
#     "-i", "-", "-f", "v4l2", "/dev/video2"
# ], stdin=subprocess.PIPE)

WIDTH = 640    # replace with your frame width
HEIGHT = 480   # replace with your frame height
FPS = 30 # frames per second

# Create a VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # for mp4
out = cv2.VideoWriter('./data/output.mp4', fourcc, FPS, (WIDTH, HEIGHT))

async def handler(ws):
    async for message in ws:
        frame = np.frombuffer(message, dtype=np.uint8)
        if frame.size == WIDTH * HEIGHT * 3:
            frame = frame.reshape((HEIGHT, WIDTH, 3))  # OpenCV uses (height, width)
            out.write(frame)  # write frame to video
            # print(f"Frame written. Center pixel R value: {frame[HEIGHT//2, WIDTH//2, 0]}")

async def main():
    async with websockets.serve(handler, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever

try:
    asyncio.run(main())
finally:
    out.release()
    print("Video saved as output.mp4")