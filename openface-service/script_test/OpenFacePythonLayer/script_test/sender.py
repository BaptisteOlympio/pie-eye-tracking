import asyncio
import numpy as np
import subprocess
import pandas as pd
import zmq
import zmq.asyncio

# On fait quelque calcul sur le csv

df = pd.read_csv("/workspace/data/data_analyse/data.csv")
max_gax = df.max()["gaze_angle_x"]
max_gay = df.max()["gaze_angle_y"]
min_gax = df.min()["gaze_angle_x"]
min_gay = df.min()["gaze_angle_y"]

context = zmq.asyncio.Context()

async def gaze_sender():
    
    columns = ["frame", "face_id", "timestamp", "confidence", "success", "gaze_0_x",
               "gaze_0_y", "gaze_0_z", "gaze_1_x", "gaze_1_y", "gaze_1_z",
               "gaze_angle_x", "gaze_angle_y"]

    port_gaze_data = "8081"

    socket_gaze_sender = context.socket(zmq.PUB)
    socket_gaze_sender.bind(f"tcp://*:{port_gaze_data}")

    await asyncio.sleep(0.5)  # let subscribers connect

    while True:
        for i in range(len(df.index)) : 
            data = df[columns].loc[i].to_dict()
            data["gaze_angle_x"] = (data["gaze_angle_x"] - min_gax)/(max_gax - min_gax)
            data["gaze_angle_y"] = (data["gaze_angle_y"] - min_gay)/(max_gay - min_gay) 
            # print(data["gaze_angle_x"], data["gaze_angle_y"])
            await socket_gaze_sender.send_json(data)
            await asyncio.sleep(1/30)

async def main() :
    await asyncio.gather(
        gaze_sender()
    )

if __name__ == "__main__" :
    asyncio.run(main())
