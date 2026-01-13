# pie-eye-tracking
# About the project.
This project started in September 2024 at the university of ISAE-Supaero. This project aims to implement and develop an open-source and low-cost end-to-end eye-tracking application for people with Charcot disease to control their home with home automation.

This project integrates an eye-tracking model (OpenFace) in an end-to-end application. The focus is to create a frontend interface and add some backend logic to adapt the eye-tracking model to the need. Another focus is on the open-source part; we try to enhance the quality of collaboration for this project by writing clean code and using standard technologies (such as Devcontainer) so anyone can participate in the development quickly and easily!

# Overview
The core of the application is the eye-tracker model; it takes an image of a face, and it calculates the eye’s direction. The OpenFace project was chosen as the model. Then we build an end-to-end application: 
- We build a frontend for the interface.
- We build pipelines of data and API for moving video frames and gazes’ data.
- We build backend logic for taking decisions of which action to take according to the gaze’s behavior.

# Project Organisation
The project is organized into services. Each service has its own container. We focused on a modular approach where it easy to change technologies or language as required. 
<img width="1156" height="394" alt="architecture-Simple Architecture drawio" src="https://github.com/user-attachments/assets/546958ff-9aa0-4272-973e-3e52edd6a142" />

# Quickstart (Working on WSL)
It's possible to launch the application without installation thanks to Docker.

## Clone the project
We need the docker-compose.yaml file to start the application; we clone the project to get it: 
```bash
git clone https://github.com/BaptisteOlympio/pie-eye-tracking.git
```

### Note 
pie-eye-tracking is in fact two project, with OpenFace. To clone the entire project : 
```bash 
git clone --recurse-submodules https://github.com/BaptisteOlympio/pie-eye-tracking.git
```
But we don't need it for the quickstart.

## decision and openface service
In the project root : 
```bash
docker compose up
```
This command starts two services, decision-service and openface-service. We can access the UI with this link: http://localhost:8083/interface/perf (or replace localhost with the IP of the host machine). 

These two services need to connect to a third one, video service.

## video-service
The purpose of the project is to use the webcam as the video source. I am using WSL so I can't use the webcam in WSL directly. I am running the script on my Windows host.
Copy the script `video-service/app/sender.py` in your Windows and start :
```bash
python sender.py --device 0
```
An IP address should be printed, and you can enter the IP and the port in http://localhost:8083/interface/perf and then `Send IP`. The video should appear! 


<!-- # Install the project.

## Clone
Clone the project with all submodules :
```
git clone --recurse-submodules https://github.com/BaptisteOlympio/pie-eye-tracking.git
```

## Windows + WSL.
The project is based on Docker container. You will need to build the container yourself. The build of OpenFace depends on the CPU architecture; it might not work for arm64 (Mac or Raspberry Pi).

## Building image
### OpenFace
build openface images. This is the base image for openface-service : 
```bash
docker build -t openface:latest ./openface-service/OpenFace
```

### openface-service and decision-service
```bash
docker build -t openface-service:latest ./openface-service
docker build -t decision-service:latest ./decision-service
```

### video-service
Video-service is the service sending the frame to the application. I can't use the webcam in WSL for some reason, so I run the video-service not in the docker compose but on my windows. You can install all the requirements. 
```bash
pip install -r ./video-service/requirements.txt
```

# Start the project
## Start openface-service and decision-service
```bash
docker compose up
```
The only available page is http://localhost:8083/interface/perf. 

## Lauch video service
To launch video-service with the webcam of windows : 
```bash
python video-service/app/sender.py --device 0
```
It will print on Windows the adress.

Enter the ip and port in the page ``perf`` and send ip. The video with the landmark should appear.  



 -->
