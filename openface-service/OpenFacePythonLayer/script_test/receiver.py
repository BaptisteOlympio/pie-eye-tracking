import zmq

context = zmq.Context()
socket = context.socket(zmq.SUB)
socket.connect("tcp://172.26.128.105:8081")
socket.setsockopt(zmq.SUBSCRIBE, b"")

# while True:
data = socket.recv_json()
print("Data received:", data)
