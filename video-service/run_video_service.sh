#!/bin/bash

docker rm -f video-service 2>/dev/null

docker run -it --rm\
  --name video-service \
  --network zmq_net \
  video-service-image bash