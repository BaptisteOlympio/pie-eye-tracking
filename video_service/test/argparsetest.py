import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--stream_loop', action='store_true')
parser.add_argument("-f", "--input_file", type=str, default="/workspace/data/test_gouget_cut.mp4")
parser.add_argument("--port", type=int, default=8080)
parser.add_argument("--fps", type=int, default=30)

args = parser.parse_args()

print(args.stream_loop)
print(args.input_file)
print(args.port)
print(args.fps)