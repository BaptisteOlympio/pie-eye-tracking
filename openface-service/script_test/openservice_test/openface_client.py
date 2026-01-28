import grpc
import openfaceservice_pb2_grpc
import openfaceservice_pb2

import asyncio
import cv2
import numpy as np
from time import time

async def run() :
    img = cv2.imread("../../data_test/tesla.jpg")
    dtype_b = str(img.dtype).encode()
    shape_b = str(img.shape).encode()
    array_b = img.tobytes()
    
    start = time()
    async with grpc.aio.insecure_channel("localhost:8081") as channel :
        stub = openfaceservice_pb2_grpc.OpenFaceServiceStub(channel)
        response = await stub.GetLandmarkAndGaze(openfaceservice_pb2.Frame(
            frame=array_b,
            dtype=dtype_b,
            shape=shape_b
        ))
        landmark = []
        for point in response.landmark.landmark :
            landmark.append((int(point.x), int(point.y)))
        gaze_angle_x = response.gaze.gaze_angle_x
        gaze_angle_y = response.gaze.gaze_angle_y
        
        print(landmark[0], landmark[1])
        print("Gaze angle x:", gaze_angle_x)
        print("Gaze angle y:", gaze_angle_y)
    print("time taken : ", time() - start)
    
    # img_landmark = img.copy()
    # print("---- print landmark -----")
    # for face_keypoint in landmark : 
    #     img_landmark = cv2.circle(img_landmark, face_keypoint, radius=3, color=(0,0,255), thickness=-1)
    # cv2.imwrite("./tesla_landmark.jpg", img_landmark)
        
if __name__ == "__main__" :
    asyncio.run(run())