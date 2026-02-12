import os 
import json
from app.config import load_calibration_data

async def get_direction_from_gaze(gaze) :

    # get current calibration values
    calibration_data = load_calibration_data.get_calibration_values()
    GAZE_MAX_X = calibration_data["GAZE_MAX_X"]
    GAZE_MIN_X = calibration_data["GAZE_MIN_X"]
    GAZE_MAX_Y = calibration_data["GAZE_MAX_Y"]
    GAZE_MIN_Y = calibration_data["GAZE_MIN_Y"]

    # current gaze data
    gaze_x = gaze[0]
    gaze_y = gaze[1]
    
    # Compute the center of the gaze range
    gaze_center_x = (GAZE_MAX_X + GAZE_MIN_X) / 2  
    gaze_center_y = (GAZE_MAX_Y + GAZE_MIN_Y) / 2  

   

    # Seuil adapté aux vraies plages (30% de la plage)
    threshold_x = (GAZE_MAX_X - GAZE_MIN_X) * 0.3  # ~0.012
    threshold_y = (GAZE_MAX_Y - GAZE_MIN_Y) * 0.3  # ~0.039

    # Si on est au centre sur les deux axes
    if abs(gaze_x - gaze_center_x) < threshold_x and abs(gaze_y - gaze_center_y) < threshold_y:
        return "CENTER"
    
    # Déterminer la direction dominante (normalisée)
    x_distance = abs(gaze_x - gaze_center_x) / ((GAZE_MAX_X - GAZE_MIN_X) / 2)
    y_distance = abs(gaze_y - gaze_center_y) / ((GAZE_MAX_Y - GAZE_MIN_Y) / 2)
    
    if x_distance >= y_distance:
        # Direction horizontale dominante
        if gaze_x - gaze_center_x > 0:
            return "RIGHT"  # Vers x positif (+1)
        else:
            return "LEFT"   # Vers x négatif (-1)
    else:
        # Direction verticale dominante
        if gaze_y - gaze_center_y > 0:
            return "DOWN"   # Vers y positif (+1)
        else:
            return "UP"     # Vers y négatif (-1)