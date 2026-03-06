import asyncio
import json
from app.services.connection_manager import manager 
from app.services import process_frame
from app.services.logic_wheel import DecisionWheel, InterfaceManager
from app.services.perf import get_direction_from_gaze
from app.services.interpretation import get_direction_from_gaze
from app.core import state
from app.config.load_IHM_config import IHM_CONFIG


async def IHM_task() :
    print("------------LAUCH IHM TASK--------------")
    async with state.IHM_lock : 
        state.IHM_status = state.IHMStatus.RUNNING
    
    try :
        await run_app_logic()
    finally : 
        async with state.IHM_lock : 
            state.IHM_status = state.IHMStatus.NOT_RUNNING


ui_manager = InterfaceManager()

async def run_app_logic():
    """
    function that runs the main logic of the application:
        - Read gaze data
        - Update decision wheel
        - Get UI context
        - Send everything to the frontend via WebSocket
    """
    # Chargement des paramètres depuis la config
    FREQUENCE_LECTURE = IHM_CONFIG["performance"]["frequence_lecture"]
    VALIDATION_THRESHOLD = IHM_CONFIG["wheel"]["seuil_validation"]
    BUFFER_LIMIT = IHM_CONFIG["wheel"]["buffer_limit"]
    
    print(f">>> Démarrage Domotique V5 (Design) - {FREQUENCE_LECTURE} Hz")
    print(f">>> Seuil validation: {VALIDATION_THRESHOLD}, Buffer: {BUFFER_LIMIT}")
    
    # Initialisation des composants
    wheel = DecisionWheel(seuil_validation=VALIDATION_THRESHOLD, buffer_limit=BUFFER_LIMIT) # Le Filtre (Ergonomie)
    
    try:
        while True:
            frame = process_frame.process_frame.latest_frame
            landmark = process_frame.process_frame.latest_landmark
            gaze = process_frame.process_frame.latest_gaze
            
            # La direction du regard (UP, DOWN, LEFT, RIGHT, CENTER) calculée à partir des coordonnées de gaze
            current_direction = await get_direction_from_gaze(gaze)  

            # Mise à jour de la roue de décision avec la nouvelle direction
            wheel_result = wheel.update(current_direction)
            
            # --- CONTEXTE VISUEL (AVANT ACTION) ---
            # C'est l'astuce pour le problème d'affichage ! 
            # On prend une "photo" de l'interface MAINTENANT, avant de changer l'état.
            # Cela permet d'afficher "OK" sur le bouton "ALLUMER" juste avant qu'il disparaisse.
            context_data = ui_manager.get_ui_context()
            
            # --- VALIDATION & ACTION ---
            # Si la roue dit "C'est validé (100%) !"
            if wheel_result["validated"]:
                # On exécute l'action (Changer lumière, entrer salon...)
                ui_manager.process_validation(wheel_result["validated"])
                
                # On remet la roue à zéro pour éviter de re-cliquer tout de suite
                wheel.reset()

            # --- ENVOI AU HTML ---
            # On regroupe tout (Input + Roue + Contexte UI) dans un gros paquet JSON
            data_to_send = {
                "direction": wheel_result["direction"], # ex: "UP"
                "percent": wheel_result["percent"],     # ex: 75
                "validated": wheel_result["validated"], # ex: "UP" ou null
                "debug_info": f"In: {current_direction}",
                
                # Les infos calculées par l'InterfaceManager
                "labels": context_data["labels"],
                "room_name": context_data["room_name"],
                "queue": context_data["queue"],
                "center_theme": context_data["center_theme"] 
            }
            
            # On envoie les données ecrites précédemment via WebSocket à la page web
            await manager.broadcast(json.dumps(data_to_send), "IHM")
            
            
            await asyncio.sleep(1.0 / FREQUENCE_LECTURE)
            
    except Exception as e:
        print(f"Erreur App: {e}")