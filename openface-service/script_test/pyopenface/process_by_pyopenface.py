import cv2 as cv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import pyopenface

# On définie notre detector. On charge donc les modèles qui vont être utilisé dans le cadre de landmarkinvideo et gaze. 
detector = pyopenface.Detector("/usr/local/etc/OpenFace/model/main_ceclm_general.txt", 
                               "/usr/local/etc/OpenFace/classifiers/haarcascade_frontalface_alt2.xml",
                               "/usr/local/etc/OpenFace/model/mtcnn_detector/MTCNN_detector.txt")

# On charge un numpy array en couleur RGB (ici avec opencv)
img = cv.imread("./tesla.jpg")
# .landmarkinvideo sert à calculer les landmarks, on reçois une liste de points pour chaque landmark.
landmark = detector.landmarkinvideo(img)
# .getgaze permet d'avoir dans un dictionaire "get_angle_x" et "get_angle_y"
# ! Il est nécessaire de lancer .landmarkinvideo avant chaque utilisation de getgaze.
gaze = detector.getgaze(img)
