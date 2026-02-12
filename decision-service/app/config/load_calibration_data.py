import json 
import os


# Variables globales pour stocker les données de calibration
CALIBRATION_DATA = {}
GAZE_MAX_X = 0.1
GAZE_MIN_X = -0.1
GAZE_MAX_Y = 0.1
GAZE_MIN_Y = -0.1

# Charger les données au démarrage
calibration_config_path = os.path.join(os.path.dirname(__file__), "..", "config", "calibration_data.json")
if os.path.exists(calibration_config_path):
    with open(calibration_config_path, "r") as f:
        CALIBRATION_DATA = json.load(f)
        GAZE_MAX_X = CALIBRATION_DATA["gaze_x_max"]
        GAZE_MIN_X = CALIBRATION_DATA["gaze_x_min"]
        GAZE_MAX_Y = CALIBRATION_DATA["gaze_y_max"]
        GAZE_MIN_Y = CALIBRATION_DATA["gaze_y_min"]

        print(f"NEW gaze max x: {GAZE_MAX_X}")
else:
    print("ERREUR: Fichier calibration_data.json introuvable, utilisation des valeurs par défaut")
    CALIBRATION_DATA = {
        "gaze_x_max": GAZE_MAX_X,
        "gaze_x_min": GAZE_MIN_X,
        "gaze_y_max": GAZE_MAX_Y,
        "gaze_y_min": GAZE_MIN_Y,
    }

def load_calibration():
    """Recharge les données de calibration depuis le fichier JSON."""
    global CALIBRATION_DATA, GAZE_MAX_X, GAZE_MIN_X, GAZE_MAX_Y, GAZE_MIN_Y
    calibration_config_path = os.path.join(os.path.dirname(__file__), "..", "config", "calibration_data.json")
    if os.path.exists(calibration_config_path):
        with open(calibration_config_path, "r") as f:
            CALIBRATION_DATA = json.load(f)
            GAZE_MAX_X = CALIBRATION_DATA["gaze_x_max"]
            GAZE_MIN_X = CALIBRATION_DATA["gaze_x_min"]
            GAZE_MAX_Y = CALIBRATION_DATA["gaze_y_max"]
            GAZE_MIN_Y = CALIBRATION_DATA["gaze_y_min"]

            print(f"Calibration data loaded: {CALIBRATION_DATA}")
    else:
        print("ERREUR: Fichier calibration_data.json introuvable, utilisation des valeurs par défaut")
        GAZE_MAX_X = 0.1
        GAZE_MIN_X = -0.1
        GAZE_MAX_Y = 0.1
        GAZE_MIN_Y = -0.1
        CALIBRATION_DATA = {
            "gaze_x_max": GAZE_MAX_X,
            "gaze_x_min": GAZE_MIN_X,
            "gaze_y_max": GAZE_MAX_Y,
            "gaze_y_min": GAZE_MIN_Y,
        }


def get_calibration_values():
    """Retourne les valeurs de calibration actuelles."""
    return {
        "GAZE_MAX_X": GAZE_MAX_X,
        "GAZE_MIN_X": GAZE_MIN_X,
        "GAZE_MAX_Y": GAZE_MAX_Y,
        "GAZE_MIN_Y": GAZE_MIN_Y,
        "CALIBRATION_DATA": CALIBRATION_DATA
    }