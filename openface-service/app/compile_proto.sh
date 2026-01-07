python3 -m grpc_tools.protoc -I . --python_out=. --pyi_out=. --grpc_python_out=. ./openfaceservice.proto
cp openfaceservice_pb2_grpc.py ../script_test/openservice_test/
cp openfaceservice_pb2.py ../script_test/openservice_test/
cp openfaceservice_pb2.pyi ../script_test/openservice_test/