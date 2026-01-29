import openfaceservice_pb2_grpc
import openfaceservice_pb2
from concurrent import futures

import grpc
import numpy as np
import json
import pyopenface
import asyncio

# Init pyopenface detector
detector = pyopenface.Detector("/usr/local/etc/OpenFace/model/main_ceclm_general.txt", 
                               "/usr/local/etc/OpenFace/classifiers/haarcascade_frontalface_alt2.xml",
                               "/usr/local/etc/OpenFace/model/mtcnn_detector/MTCNN_detector.txt")


class OpenFaceService(openfaceservice_pb2_grpc.OpenFaceService) :
    async def GetLandmarkAndGaze(self, request, context) :
        # Extraction of the numpy array from the request
        dtype = np.dtype(request.dtype.decode())
        shape = tuple(map(int, request.shape.decode().strip("()").split(",")))
        array = np.frombuffer(buffer=request.frame, dtype=dtype).reshape(shape)
        # print(array.shape, array.dtype, array[0,0,0])
        # !! Calculation of landmark !! Important, if you want to change model do it here.
        try :  
            landmark_output = detector.landmarkinvideo(array)
            
            
            face_keypoints = [(int(kp[0]), int(kp[1])) for kp in zip(landmark_output[0], landmark_output[1])]
            
            # Create a Landmark message, we add the point after
            landmark = openfaceservice_pb2.Landmark()

            for face_keypoint_x, face_keypoint_y in face_keypoints :
                landmark.landmark.add(x=face_keypoint_x, y=face_keypoint_y)


            gaze_output = detector.getgaze(array)

            gaze_angle_x = float(gaze_output["gaze_angle_x"])
            gaze_angle_y = float(gaze_output["gaze_angle_y"])
            gaze_angles = openfaceservice_pb2.Gaze(gaze_angle_x=gaze_angle_x, gaze_angle_y=gaze_angle_y)        # dépend du .proto
            

            landmark_and_gaze = openfaceservice_pb2.LandmarkAndGaze(landmark=landmark, gaze=gaze_angles)
        except Exception as e :
            # print(e)
            return openfaceservice_pb2.LandmarkAndGaze()
        
        return landmark_and_gaze

async def serve() :
    port = "8081"
    server = grpc.aio.server()
    openfaceservice_pb2_grpc.add_OpenFaceServiceServicer_to_server(OpenFaceService(), server)
    server.add_insecure_port("*:" + port)
    await server.start()
    print("server listening on " + port)
    await server.wait_for_termination()

if __name__ == "__main__" :
    asyncio.run(serve())
        
        
        
        