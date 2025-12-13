# Ce module va recevoir les frame par websocket et les écrit dans /dev/video0 avec ffmpeg.

import asyncio
import numpy as np
import subprocess
import pandas as pd
import zmq
import zmq.asyncio
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--ip_vs", type=str)
parser.add_argument("--port_vs", type=str)
parser.add_argument('--from_file', action='store_true')
args = parser.parse_args()

ip_vs = args.ip_vs
port_vs = args.port_vs
from_file = args.from_file

context = zmq.asyncio.Context()

WIDTH = 640
HEIGHT = 480


async def _recv_multipart_async(socket):
    """Yield multipart messages from an async zmq socket."""
    while True:
        try:
            parts = await socket.recv_multipart()
        except Exception:
            # Socket closed or interrupted
            return
        yield parts


def _write_to_ffmpeg(pipe, data: bytes) -> bool:
    """Write bytes to ffmpeg stdin in a thread-safe manner.

    Returns True on success, False if the pipe is closed.
    """
    try:
        pipe.write(data)
        pipe.flush()
        return True
    except BrokenPipeError:
        return False
    except Exception:
        return False


async def write_frame():
    if from_file :
        return
    socket_video_service = context.socket(zmq.SUB)
    socket_video_service.setsockopt(zmq.SUBSCRIBE, b"")
    # Use RCVHWM=1 to keep only the last message in the queue instead of
    # using CONFLATE which can cause issues with multipart messages.
    socket_video_service.setsockopt(zmq.RCVHWM, 1)
    socket_video_service.setsockopt(zmq.LINGER, 0)
    socket_video_service.connect(f"tcp://{ip_vs}:{port_vs}")
    
    
    print("[video-svc] launching ffmpeg to /dev/video0")
    ffmpeg = subprocess.Popen([
        "ffmpeg", "-y",
        "-f", "rawvideo", "-pix_fmt", "bgr24",
        "-s", f"{WIDTH}x{HEIGHT}", "-r", "15",
        "-i", "-", "-f", "v4l2", "/dev/video0"
    ], stdin=subprocess.PIPE, bufsize=0)
    
    print(f"[video-svc] Connected to tcp://{ip_vs}:{port_vs}")
    async for parts in _recv_multipart_async(socket_video_service):
        if not parts or len(parts) != 3:
            # malformed message, skip
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

        if frame.shape != (HEIGHT, WIDTH, 3):
            # try to reshape sensibly or skip
            try:
                frame = frame.reshape((HEIGHT, WIDTH, 3))
            except Exception:
                continue

        data_bytes = frame.tobytes()
        loop = asyncio.get_running_loop()
        ok = await loop.run_in_executor(None, _write_to_ffmpeg, ffmpeg.stdin, data_bytes)
        if not ok:
            print("[video-svc] ffmpeg pipe closed; stopping writer")
            break

async def gaze_sender():
    columns = ["frame", "face_id", "timestamp", "confidence", "success", "gaze_0_x",
               "gaze_0_y", "gaze_0_z", "gaze_1_x", "gaze_1_y", "gaze_1_z",
               "gaze_angle_x", "gaze_angle_y"]

    port_gaze_data = "8081"

    socket_gaze_sender = context.socket(zmq.PUB)
    socket_gaze_sender.bind(f"tcp://*:{port_gaze_data}")

    await asyncio.sleep(0.5)  # let subscribers connect

    loop = asyncio.get_running_loop()

    async def load_csv():
        """Read CSV in a background thread safely."""
        try:
            return await loop.run_in_executor(
                None, pd.read_csv, "/workspace/data/data.csv"
            )
        except (pd.errors.EmptyDataError,
                pd.errors.ParserError,
                FileNotFoundError,
                EOFError):
            return None

    i = 0
    while True:
        df = await load_csv()

        if df is not None and not df.empty:
            try:
                if from_file :
                    i = i % len(df.index)
                    row = df[columns].loc[i].to_dict()
                    i += 1
                else : 
                    row = df.tail(1)[columns].to_dict("records")[0]
                await socket_gaze_sender.send_json(row)
                
            except Exception:
                # corrupted row or missing columns
                pass

        await asyncio.sleep(1/30)

async def main() :
    await asyncio.gather(
        write_frame(),
        gaze_sender()
    )

if __name__ == "__main__" :
    asyncio.run(main())
