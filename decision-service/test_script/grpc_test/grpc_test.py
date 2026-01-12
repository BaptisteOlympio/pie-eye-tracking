import grpc
import openfaceservice_pb2_grpc
import openfaceservice_pb2

import cv2
import numpy as np
from time import time

def run() :
    img = cv2.imread("/workspace/data_test/images/tesla.jpg")
    dtype_b = str(img.dtype).encode()
    shabe_b = str(img.shape).encode()
    array_b = img.tobytes()
    
    start = time()
    with grpc.insecure_channel("172.26.128.105:8081") as channel :
        stub = openfaceservice_pb2_grpc.OpenFaceServiceStub(channel)
        response = stub.GetLandmark(openfaceservice_pb2.Frame(
            frame=array_b,
            dtype=dtype_b,
            shape=shabe_b
        ))
        landmark = []
        for point in response.landmark :
            landmark.append((int(point.x), int(point.y)))
            
        print(landmark)
    print("time taken : ", time() - start)
    
    img_landmark = img.copy()
    print("---- print landmark -----")
    for face_keypoint in landmark : 
        img_landmark = cv2.circle(img_landmark, face_keypoint, radius=3, color=(0,0,255), thickness=-1)
    cv2.imwrite("./tesla_landmark.jpg", img_landmark)
        
if __name__ == "__main__" :
    run()