import argparse

# On récupère les arguments 

parser = argparse.ArgumentParser()

parser.add_argument('--stream_loop', action='store_true')
parser.add_argument("-f", "--input_file", type=str, default="/workspace/data/test_gouget_cut.mp4")
parser.add_argument("--device", type=int, default=-1)
parser.add_argument("--port", type=int, default=8080)
parser.add_argument("--fps", type=int, default=30)
args = parser.parse_args()

stream_loop = args.stream_loop
input_file = args.input_file
device = args.device
port = args.port
fps = args.fps

print("stream loop :", stream_loop)
print("input_file :", input_file)
print("device :", device)
print("port :", port)
print("fps :", fps)
