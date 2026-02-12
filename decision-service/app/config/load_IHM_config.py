import json
import os

config_path = os.path.join(os.path.dirname(__file__), "IHM_config.json")
if os.path.exists(config_path):
    with open(config_path, "r") as f:
        IHM_CONFIG = json.load(f)
else:
    print("ERREUR: Fichier IHM_config.json introuvable, utilisation configuration par défaut")


