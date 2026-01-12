from concurrent import futures

import grpc
import numpy_pb2
import numpy_pb2_grpc

import numpy as np
import json

class NumpyServer(numpy_pb2_grpc.Numpy) :
    def ProcessArray(self, request, context) :
        dtype = np.dtype(request.dtype.decode())
        shape = tuple(map(int, request.shape.decode().strip("()").split(",")))
        array = np.frombuffer(buffer=request.image, dtype=dtype).reshape(shape)
        response = {"dtype" : str(dtype), "shape" : str(shape)}
        response_b = json.dumps(response).encode('utf-8')
        return numpy_pb2.MessageResponse(message=response_b)

def serve() :
    port = "50051"
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    numpy_pb2_grpc.add_NumpyServicer_to_server(NumpyServer(), server)
    server.add_insecure_port("[::]:" + port)
    server.start()
    print("server listening on " + port)
    server.wait_for_termination()

if __name__ == "__main__" : 
    serve()

