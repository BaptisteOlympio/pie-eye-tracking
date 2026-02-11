import json
import os

class DecisionWheel:
    def __init__(self, seuil_validation=4, buffer_limit=2):
        self.seuil = seuil_validation      # Ex: 4 ticks pour 100%
        self.buffer_limit = buffer_limit   # Ex: 2 ticks de tolérance
        
        self.compteur = 0
        self.buffer_compteur = 0
        self.direction_en_cours = "CENTER"
        self.decision_validee = None

    def update(self, raw_input_direction):
        """
        Logique de Résilience Totale :
        Si on a commencé quelque chose, on ne l'annule JAMAIS tout de suite.
        On utilise toujours le buffer.
        """
        
        # 1. EST-CE QU'ON CONTINUE DANS LA MÊME DIRECTION ?
        if raw_input_direction == self.direction_en_cours:
            # Oui -> Tout va bien, on reset le stress (buffer)
            self.buffer_compteur = 0
            
            # On continue de remplir (si ce n'est pas le centre)
            if self.direction_en_cours != "CENTER":
                if self.compteur < self.seuil:
                    self.compteur += 1
                
                # Validation ?
                if self.compteur >= self.seuil:
                    self.decision_validee = self.direction_en_cours

        # 2. NON, LE REGARD A CHANGÉ (Centre, autre direction, erreur...)
        else:
            # Est-ce qu'on avait du progrès à protéger ?
            if self.compteur > 0:
                # OUI -> ON ACTIVE LE BUFFER (PROTECTION)
                self.buffer_compteur += 1
                
                # Tant qu'on est dans la tolérance, ON NE BOUGE PAS.
                # On ignore le nouvel input, on garde l'ancienne direction figée.
                if self.buffer_compteur <= self.buffer_limit:
                    pass # On est en PAUSE
                
                # Si on a dépassé la tolérance, c'est perdu.
                else:
                    self._switch_direction(raw_input_direction)
            
            # Non, on était déjà à 0 (Centre)
            else:
                # Alors on peut changer tout de suite (c'est un nouveau démarrage)
                self._switch_direction(raw_input_direction)

        # Calcul du pourcentage pour l'affichage
        percent = 0
        if self.seuil > 0:
            percent = (self.compteur / self.seuil) * 100

        # On retourne l'état
        return {
            "direction": self.direction_en_cours, # On renvoie ce qu'on a en mémoire (pas forcément l'input)
            "percent": percent,
            "validated": self.decision_validee,
            # Info utile : Est-ce qu'on est en train d'utiliser le buffer ?
            "status": "PAUSE" if (self.buffer_compteur > 0 and self.compteur > 0) else "RUNNING"
        }

    def get_current_direction(self):
        return self.direction_en_cours

    def reset(self):
        """Réinitialise complètement la roue après une validation"""
        self.compteur = 0
        self.buffer_compteur = 0
        self.direction_en_cours = "CENTER"
        self.decision_validee = None

    def _switch_direction(self, new_dir):
        """Réinitialisation propre"""
        self.direction_en_cours = new_dir
        self.buffer_compteur = 0
        self.decision_validee = None
        
        # Si on regarde ailleurs que le centre, on commence direct à 1 (25%)
        # Sinon on se met à 0
        if new_dir != "CENTER":
            self.compteur = 1
        else:
            self.compteur = 0

class SmartHomeSystem:
    def __init__(self):
        # État initial de la maison

        # lecture des fichier pour configurer la maison (pièces, objets, etc.)
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "smart_home_config.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                print("load a partir du json")
                self.house_data = json.load(f)
        else:
            print("hardcoder la config de la maison (pas de json trouvé)")
            self.house_data = {
                "SALON": {
                    "devices": [
                        {"id": "light_main", "name": "Lumière Plafonded", "type": "binary", "state": False}, # False = Éteint
                    {"id": "shutters",   "name": "Volets",          "type": "analog", "state": 0},     # 0% = Fermé
                    {"id": "speaker",    "name": "Enceinte",        "type": "analog", "state": 30}     # Volume 30%
                ]
            },
            "AZY FRERE": { "devices": [] },
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
        
        # Logique pour un device binaire (On/Off)
        if device["type"] == "binary":
            if action == "UP": device["state"] = True
            if action == "DOWN": device["state"] = False
            
        # Logique pour device incrélmental de 0 à 100% par tranche de 10
        elif device["type"] == "analog":
            if action == "UP": 
                device["state"] = min(100, device["state"] + 10)
            if action == "DOWN": 
                device["state"] = max(0, device["state"] - 10)
        
        return device["state"]

# Instance unique
# home_system = SmartHomeSystem()

class InterfaceManager:
    def __init__(self):
        # ### ÉTAT INITIAL ###
        # On commence toujours sur le MENU PRINCIPAL (Choix de la pièce)
        self.mode = "MENU_PRINCIPAL" 
        self.current_room = None        # Aucune pièce sélectionnée au début
        self.selected_device_index = 0  # Si on entre dans une pièce, on commence par le 1er objet
        self.home_system = SmartHomeSystem() # Notre système domotique
        
        # Chargement de la configuration de l'interface
        config_path = os.path.join(os.path.dirname(__file__), "..", "config", "interface_config.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                self.interface_config = json.load(f)
        else:
            print("ERREUR: Fichier interface_config.json introuvable, utilisation configuration par défaut")
            self.interface_config = {
                "menu_principal": {
                    "room_name": "MENU PRINCIPAL",
                    "center_label": "MAISON",
                    "directions": {"UP": "SALON", "LEFT": "AZY FRERE", "RIGHT": "CHAMBRE", "DOWN": "SDB"}
                },
                "room_control": {
                    "navigation": {"previous": "PREC.", "next": "SUIV."},
                    "actions": {
                        "binary": {"on": {"up": "ALLUMER", "down": ""}, "off": {"up": "", "down": "ÉTEINDRE"}},
                        "analog": {"up": "+", "down": "-"}
                    },
                    "themes": {"light_on": "light-on", "light_off": "light-off", "neutral": "neutral"}
                },
                "default_labels": {"UP": "", "DOWN": "", "LEFT": "", "RIGHT": "", "CENTER": ""}
            }
        
    
    def get_ui_context(self):
        """
        Fonction de préparation de l'affichage
        Cette fonction est appelée à CHAQUE image (4 fois par seconde).
        Son rôle : Regarder l'état de la maison et dire au HTML quoi écrire dans les cercles.
        
        :param self: 
        """
        # On prépare des variables vides par défaut (depuis la config)
        labels = self.interface_config["default_labels"].copy()
        room_name = "ACCUEIL"
        queue_data = [] 
        center_theme = self.interface_config["room_control"]["themes"]["neutral"]
        
        # --- CAS 1 : ON EST DANS LE MENU PRINCIPAL ---
        # Ici, les boutons servent à choisir la pièce.
        if self.mode == "MENU_PRINCIPAL":
            menu_config = self.interface_config["menu_principal"]
            labels.update(menu_config["directions"])
            labels["CENTER"] = menu_config["center_label"]
            room_name = menu_config["room_name"]
            # (Pas de liste d'objets à droite dans le menu)

        # --- CAS 2 : ON EST DANS UNE PIÈCE (MODE CONTRÔLE) ---
        # Ici, on contrôle les objets (Lumière, Volets, etc.)
        elif self.mode == "ROOM_CONTROL":
            room_name = self.current_room
            # On demande à la "Smart Home" la liste des objets de cette pièce
            devices = self.home_system.get_room_devices(self.current_room)
            
            # Affichage de la liste de tous les devices et leurs états
            for i, dev in enumerate(devices):
                # Formatage du texte selon le type d'objet
                if dev["type"] == "binary":
                    state_str = "ON" if dev["state"] else "OFF"
                elif dev["type"] == "analog":
                    state_str = f"{dev['state']}%"
                else:
                    state_str = ""

                state_str = dev.get("state_str", "") + " " + state_str
                
                # On ajoute l'objet à la liste à envoyer au HTML
                queue_data.append({
                    "name": dev["name"],
                    "state": state_str,
                    "active": (i == self.selected_device_index) # Vrai si c'est l'objet qu'on regarde actuellement
                })

            # On récupère l'objet ACTUEL (celui sélectionné)
            current_device = devices[self.selected_device_index]
            
            # 2. Gestion des Couleurs (Feedback Visuel)
            themes = self.interface_config["room_control"]["themes"]
            # Si c'est une lumière allumée -> Jaune
            if current_device["type"] == "binary":
                if current_device["state"] is True:
                    center_theme = themes["light_on"]
                elif current_device["state"] is False:
                    center_theme = themes["light_off"]
            else:
                center_theme = themes["neutral"]

            # 3. Remplissage des Textes des Boutons
            # CENTRE : Nom de l'objet + son état
            current_state_str = queue_data[self.selected_device_index]["state"]
            labels["CENTER"] = f"{current_device['name']}\n{current_state_str}"
            
            # GAUCHE / DROITE : Navigation (Carrousel)
            nav_config = self.interface_config["room_control"]["navigation"]
            labels["LEFT"] = nav_config["previous"]
            labels["RIGHT"] = nav_config["next"]
            
            # HAUT / BAS : Actions Contextuelles (Intelligence)
            actions_config = self.interface_config["room_control"]["actions"]
            
            # Si c'est un device de navigation (retour menu)
            if current_device["type"] == "navigation":
                labels["UP"] = "VALIDER"
                labels["DOWN"] = ""
            # Si c'est un interrupteur (ON/OFF)
            elif current_device["type"] == "binary":
                if current_device["state"] is False:
                    # Si éteint -> On propose ALLUMER en haut
                    labels["UP"] = actions_config["binary"]["off"]["up"]
                    labels["DOWN"] = actions_config["binary"]["off"]["down"]
                else:
                    # Si allumé -> On propose ÉTEINDRE en bas
                    labels["UP"] = actions_config["binary"]["on"]["up"]
                    labels["DOWN"] = actions_config["binary"]["on"]["down"]
            # Si c'est un variateur (Volet/Son)
            elif current_device["type"] == "analog":
                labels["UP"] = actions_config["analog"]["up"]
                labels["DOWN"] = actions_config["analog"]["down"]

        # On retourne le "paquet" complet pour le HTML
        return {
            "labels": labels,
            "room_name": room_name,
            "queue": queue_data,
            "center_theme": center_theme 
        }

    # ### FONCTION D'ACTION : EXÉCUTION ###
    # Cette fonction est appelée UNIQUEMENT quand la roue atteint 100% (Validation).
    def process_validation(self, direction):
        if direction == "CENTER": return # Le centre ne déclenche jamais d'action

        # Si on valide dans le MENU -> On change de mode (On entre dans une pièce)
        if self.mode == "MENU_PRINCIPAL":
            # Lecture du mapping direction -> pièce depuis le JSON
            room_mapping = self.interface_config["menu_principal"]["directions"]
            if direction in room_mapping:
                self.mode = "ROOM_CONTROL"
                self.current_room = room_mapping[direction]
                self.selected_device_index = 0

        # Si on valide dans une PIÈCE -> On agit sur la maison
        elif self.mode == "ROOM_CONTROL":
            devices = self.home_system.get_room_devices(self.current_room)
            current_device = devices[self.selected_device_index]
            
            # Navigation (Droite/Gauche) : On change l'index de sélection
            if direction == "RIGHT":
                self.selected_device_index = (self.selected_device_index + 1) % len(devices)
            elif direction == "LEFT":
                self.selected_device_index = (self.selected_device_index - 1) % len(devices)
            # Action (Haut/Bas) : On vérifie si c'est un device de navigation
            elif direction in ["UP", "DOWN"]:
                # Si c'est le device de retour au menu
                if current_device["type"] == "navigation" and direction == "UP":
                    self.mode = "MENU_PRINCIPAL"
                    self.current_room = None
                    self.selected_device_index = 0
                else:
                    # Sinon on appelle la SmartHome pour modifier l'objet
                    self.home_system.update_device(self.current_room, self.selected_device_index, direction)
