import openfaceservice_pb2_grpc
import openfaceservice_pb2
from concurrent import futures

import grpc
import numpy as np
import json
import pyopenface

# Init pyopenface detector
detector = pyopenface.Detector("/usr/local/etc/OpenFace/model/main_ceclm_general.txt", 
                               "/usr/local/etc/OpenFace/classifiers/haarcascade_frontalface_alt2.xml",
                               "/usr/local/etc/OpenFace/model/mtcnn_detector/MTCNN_detector.txt")


class OpenFaceService(openfaceservice_pb2_grpc.OpenFaceService) :
    def GetLandmark(self, request, context) :
        # Extraction of the numpy array from the request
        dtype = np.dtype(request.dtype.decode())
        shape = tuple(map(int, request.shape.decode().strip("()").split(",")))
        array = np.frombuffer(buffer=request.frame, dtype=dtype).reshape(shape)
        # print(array.shape, array.dtype, array[0,0,0])
        # !! Calculation of landmark !! Important, if you want to change model do it here. 
        landmark_output = detector.landmarkinvideo(array)
        
        face_keypoints = [(int(kp[0]), int(kp[1])) for kp in zip(landmark_output[0], landmark_output[1])]
        
        # Create a Landmark message, we add the point after
        landmark = openfaceservice_pb2.Landmark()
    
        for face_keypoint_x, face_keypoint_y in face_keypoints :
            landmark.landmark.add(x=face_keypoint_x, y=face_keypoint_y)
        
        return landmark

def serve() :
    port = "8081"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    openfaceservice_pb2_grpc.add_OpenFaceServiceServicer_to_server(OpenFaceService(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("server listening on " + port)
    server.wait_for_termination()

if __name__ == "__main__" :
    serve()
        
        
        
        