from app.grpc_compiled import openfaceservice_pb2
from app.grpc_compiled import openfaceservice_pb2_grpc

import grpc
import numpy as np
import json
import pyopenface


class OpenFaceService(openfaceservice_pb2_grpc.OpenFaceService) :
    def GetLandmark(self, request, context) :
        dtype = np.dtype(request.dtype.decode())
        shape = tuple(map(int, request.shape.decode().strip("()").split(",")))
        array = np.frombuffer(buffer=request.image, dtype=dtype).reshape(shape)