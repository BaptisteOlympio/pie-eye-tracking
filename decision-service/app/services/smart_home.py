# Simulation d'une base de données domotique
class SmartHomeSystem:
    def __init__(self):
        # État initial de la maison
        self.house_data = {
            "SALON": {
                "devices": [
                    {"id": "light_main", "name": "Lumière Plafond", "type": "binary", "state": False}, # False = Éteint
                    {"id": "shutters",   "name": "Volets",          "type": "analog", "state": 0},     # 0% = Fermé
                    {"id": "speaker",    "name": "Enceinte",        "type": "analog", "state": 30}     # Volume 30%
                ]
            },
            "CUISINE": { "devices": [] }, # Vide pour l'instant
            "CHAMBRE": { "devices": [] },
            "SDB":     { "devices": [] }
        }

    def get_room_devices(self, room_name):
        return self.house_data.get(room_name, {}).get("devices", [])

    def update_device(self, room, device_index, action):
        """
        Modifie l'état (ex: Allumer lumière, Monter volume)
        action: "UP" ou "DOWN"
        """
        device = self.house_data[room]["devices"][device_index]
        
        # Logique pour LUMIÈRE (On/Off)
        if device["type"] == "binary":
            if action == "UP": device["state"] = True
            if action == "DOWN": device["state"] = False
            
        # Logique pour VOLETS et SON (0 à 100%)
        elif device["type"] == "analog":
            if action == "UP": 
                device["state"] = min(100, device["state"] + 10)
            if action == "DOWN": 
                device["state"] = max(0, device["state"] - 10)
        
        return device["state"]

# Instance unique
home_system = SmartHomeSystem()