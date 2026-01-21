import numpy as np
import json

import grpc
import numpy_pb2
import numpy_pb2_grpc

def run() :
    rng = np.random.default_rng()
    array_random = rng.integers(256, size=(640, 480, 3), dtype=np.uint8)
    dtype_b = str(array_random.dtype).encode()
    shabe_b = str(array_random.shape).encode()
    array_b = array_random.tobytes()
    
    with grpc.insecure_channel("localhost:50051") as channel :
        stub = numpy_pb2_grpc.NumpyStub(channel)
        response = stub.ProcessArray(numpy_pb2.ArrayRequest(
            image=array_b,
            dtype=dtype_b,
            shape=shabe_b
        ))
        dico = json.loads(response.message)
        print(dico)
        
    pass 

if __name__ == "__main__" :
    run()