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
<img width="1098" height="202" alt="architecture-Simple Architecture drawio" src="https://github.com/user-attachments/assets/ddc9232f-e792-4966-9ab2-8c6c66a3a957" />

# Clone le projet
Dans ce projet il y a en réalité deux projets github. Le projet principale pie-eye-tracking et une copie du projet original d'OpenFace. Pour cloner l'ensemble des deux projets : 
```
git clone --recurse-submodules https://github.com/BaptisteOlympio/pie-eye-tracking.git
```


