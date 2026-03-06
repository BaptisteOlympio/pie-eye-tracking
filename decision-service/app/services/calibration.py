import asyncio
import json
import os

from time import time
import numpy as np
from app.core import state
from app.services import process_frame
from app.services.connection_manager import manager 
from app.config import load_calibration_data


# -------------------------------
# Calibration
# -------------------------------
async def calibration_task() :
    async with state.calibration_lock : 
        state.calibration_status = state.CalibrationStatus.RUNNING
    
    try :
        await process_calibration()
    finally : 
        async with state.calibration_lock : 
            state.calibration_status = state.CalibrationStatus.IDLE
    


async def process_calibration():
    global calibration_data
    
    # Points de calibration relatifs (x, y) de 0 à 1
    # Disposition à 9 points couvrant tout l'écran
    rel_points = [
        (0.5, 0.5),   # 1. Centre
        (0.05, 0.05), (0.5, 0.05), (0.95, 0.05), # 2, 3, 4. Ligne du haut
        (0.05, 0.5),               (0.95, 0.5),  # 5, 6. Milieux latéraux
        (0.05, 0.95), (0.5, 0.95), (0.95, 0.95)  # 7, 8, 9. Ligne du bas
    ]
    
    all_gaze_x = []
    all_gaze_y = []
    
    await asyncio.sleep(1)
    await manager.broadcast({"data": {"type": "instruction", "value": "Début de la calibration. Fixez les points rouges."}}, "calibration")
    await asyncio.sleep(2)

    for i, (px, py) in enumerate(rel_points):
        # Envoyer les coordonnées du point au front-end
        await manager.broadcast({"data": {"type": "target", "x": px, "y": py}}, "calibration")
        
        # Attendre la stabilisation (700ms)
        # TODO ca se justifie dans la doc
        await asyncio.sleep(0.7)
        
        # Collecter les données pendant 1.3s (Total 2s par point)
        start_point_time = time()
        while time() - start_point_time < 1.3:
            try:
                # Utiliser les données du process_frame au lieu du socket ZMQ
                landmark = process_frame.process_frame.latest_landmark
                gaze = process_frame.process_frame.latest_gaze
                if gaze is not None and len(gaze) >= 2:
                    all_gaze_x.append(gaze[0])
                    all_gaze_y.append(gaze[1])
                # TODO remplace pâr 1/FPS
                await asyncio.sleep(0.03)  # ~30 Hz
            except Exception as e:
                print(f"Erreur calibration: {e}")
                continue

    # Calcul des bornes après filtrage des NaNs
    gaze_x_np = np.array(all_gaze_x)
    gaze_y_np = np.array(all_gaze_y)
    gaze_x_np = gaze_x_np[~np.isnan(gaze_x_np)]
    gaze_y_np = gaze_y_np[~np.isnan(gaze_y_np)]

    if len(gaze_x_np) > 0:
        # On définit les extremums pour le mapping futur
        calibration_data = {
            "gaze_x_max": float(np.percentile(gaze_x_np, 95)), # Utilisation de percentiles pour éviter les outliers
            "gaze_x_min": float(np.percentile(gaze_x_np, 5)),
            "gaze_y_max": float(np.percentile(gaze_y_np, 95)),
            "gaze_y_min": float(np.percentile(gaze_y_np, 5)),
        }
        
        # Save calibration data to JSON file and reload it in the gaze service
        try:
            # Save calibration data to JSON file
            calibration_config_path = os.path.join(os.path.dirname(__file__), "..", "config", "calibration_data.json")
            with open(calibration_config_path, "w") as f:
                json.dump(calibration_data, f, indent=4)
            print(f"Données de calibration sauvegardées dans {calibration_config_path}")
            
            # Run load_calibration.py to update the calibration data used by the gaze service
            load_calibration_data.load_calibration()
            print("Données de calibration rechargées dans le service de gaze.")
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la calibration ou du rechargement: {e}")


    await manager.broadcast({"data": {"type": "instruction", "value": "Calibration terminée !"}}, "calibration")