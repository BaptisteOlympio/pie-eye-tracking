import asyncio
import numpy as np
import subprocess
import pandas as pd
import zmq
import zmq.asyncio

context = zmq.asyncio.Context()


async def gaze_sender():
    columns = [
        "frame",
        "face_id",
        "timestamp",
        "confidence",
        "success",
        "gaze_0_x",
        "gaze_0_y",
        "gaze_0_z",
        "gaze_1_x",
        "gaze_1_y",
        "gaze_1_z",
        "gaze_angle_x",
        "gaze_angle_y",
    ]

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
        except (
            pd.errors.EmptyDataError,
            pd.errors.ParserError,
            FileNotFoundError,
            EOFError,
        ):
            return None

    while True:
        df = await load_csv()

        if df is not None and not df.empty:
            try:
                row = df.tail(1)[columns].to_dict("records")[0]
                await socket_gaze_sender.send_json(row)
            except Exception:
                # corrupted row or missing columns
                pass

        await asyncio.sleep(1 / 30)


async def main():
    await asyncio.gather(gaze_sender())


if __name__ == "__main__":
    asyncio.run(main())
