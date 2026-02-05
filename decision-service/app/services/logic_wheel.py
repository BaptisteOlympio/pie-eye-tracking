# Code contenant la logique de la roue de décision (résilience totale, buffer, etc.)
# et aussi  Smart home system et Interface Manager (préparation du contexte d'affichage et exécution des actions)

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
        # TODO: faire l'init avec la lecture d'un json pour pouvoir faire évoluer facilement
        # TODO: la config de la maison (ex: ajouter une cuisine, etc.)
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
# home_system = SmartHomeSystem()

class InterfaceManager:
    def __init__(self):
        # ### ÉTAT INITIAL ###
        # On commence toujours sur le MENU PRINCIPAL (Choix de la pièce)
        self.mode = "MENU_PRINCIPAL" 
        self.current_room = None        # Aucune pièce sélectionnée au début
        self.selected_device_index = 0  # Si on entre dans une pièce, on commence par le 1er objet
        self.home_system = SmartHomeSystem() # Notre système domotique
        
    
    def get_ui_context(self):
        """
        Fonction de préparation de l'affichage
        Cette fonction est appelée à CHAQUE image (4 fois par seconde).
        Son rôle : Regarder l'état de la maison et dire au HTML quoi écrire dans les cercles.
        
        :param self: 
        """
        # On prépare des variables vides par défaut
        labels = {"UP": "", "DOWN": "", "LEFT": "", "RIGHT": "", "CENTER": ""}
        room_name = "ACCUEIL"
        queue_data = [] 
        center_theme = "neutral" # Par défaut, le cercle central est gris
        
        # TODO: ne pas hardcoder Menu principal etc mais faire lire un ficheir json de config pour
        # TODO: pouvoir faire évoluer l'interface facilement (ex: ajouter une cuisine, etc.)
        # --- CAS 1 : ON EST DANS LE MENU PRINCIPAL ---
        # Ici, les boutons servent à choisir la pièce.
        if self.mode == "MENU_PRINCIPAL":
            labels["UP"] = "SALON"
            labels["LEFT"] = "CUISINE"
            labels["RIGHT"] = "CHAMBRE"
            labels["DOWN"] = "SDB"
            labels["CENTER"] = "MAISON"
            room_name = "MENU PRINCIPAL"
            # (Pas de liste d'objets à droite dans le menu)

        # --- CAS 2 : ON EST DANS UNE PIÈCE (MODE CONTRÔLE) ---
        # Ici, on contrôle les objets (Lumière, Volets, etc.)
        elif self.mode == "ROOM_CONTROL":
            room_name = self.current_room
            # On demande à la "Smart Home" la liste des objets de cette pièce
            devices = self.home_system.get_room_devices(self.current_room)
            
            # 1. Construction de la "File d'attente" (Liste à droite de l'écran)
            # On boucle sur tous les objets pour préparer leur affichage
            for i, dev in enumerate(devices):
                # Formatage du texte selon le type d'objet
                if dev["type"] == "binary":
                    # Pour une lumière : ON ou OFF
                    state_str = "ON" if dev["state"] else "OFF"
                elif dev["id"] == "shutters":
                    # Pour les volets : Texte explicite
                    state_str = f"OUVERT {dev['state']}%"
                else:
                    # Pour le reste (Son) : Juste le %
                    state_str = f"{dev['state']}%"
                
                # On ajoute l'objet à la liste à envoyer au HTML
                queue_data.append({
                    "name": dev["name"],
                    "state": state_str,
                    "active": (i == self.selected_device_index) # Vrai si c'est l'objet qu'on regarde actuellement
                })

            # On récupère l'objet ACTUEL (celui sélectionné)
            current_device = devices[self.selected_device_index]
            
            # 2. Gestion des Couleurs (Feedback Visuel)
            # Si c'est une lumière allumée -> Jaune
            if current_device["type"] == "binary" and current_device["state"] is True:
                center_theme = "light-on"
            # Si c'est une lumière éteinte -> Gris Sombre
            elif current_device["type"] == "binary" and current_device["state"] is False:
                center_theme = "light-off"
            else:
                center_theme = "neutral"

            # 3. Remplissage des Textes des Boutons
            # CENTRE : Nom de l'objet + son état
            current_state_str = queue_data[self.selected_device_index]["state"]
            labels["CENTER"] = f"{current_device['name']}\n{current_state_str}"
            
            # GAUCHE / DROITE : Navigation (Carrousel)
            labels["LEFT"] = "PREC."
            labels["RIGHT"] = "SUIV."
            
            # HAUT / BAS : Actions Contextuelles (Intelligence)
            # Si c'est un interrupteur (ON/OFF)
            if current_device["type"] == "binary":
                if current_device["state"] is False:
                    # Si éteint -> On propose ALLUMER en haut
                    labels["UP"] = "ALLUMER"
                    labels["DOWN"] = "" # Bas ne sert à rien
                else:
                    # Si allumé -> On propose ÉTEINDRE en bas
                    labels["UP"] = ""   # Haut ne sert à rien
                    labels["DOWN"] = "ÉTEINDRE"
            # Si c'est un variateur (Volet/Son)
            elif current_device["type"] == "analog":
                labels["UP"] = "+"
                labels["DOWN"] = "-"

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

        # Si on valide dans le MENU -> On change de mode (On entre dans le salon)
        if self.mode == "MENU_PRINCIPAL":
            if direction == "UP": 
                self.mode = "ROOM_CONTROL"
                self.current_room = "SALON"
                self.selected_device_index = 0

        # Si on valide dans une PIÈCE -> On agit sur la maison
        elif self.mode == "ROOM_CONTROL":
            devices = self.home_system.get_room_devices(self.current_room)
            
            # Navigation (Droite/Gauche) : On change l'index de sélection
            if direction == "RIGHT":
                self.selected_device_index = (self.selected_device_index + 1) % len(devices)
            elif direction == "LEFT":
                self.selected_device_index = (self.selected_device_index - 1) % len(devices)
            # Action (Haut/Bas) : On appelle la SmartHome pour modifier l'objet
            elif direction in ["UP", "DOWN"]:
                self.home_system.update_device(self.current_room, self.selected_device_index, direction)
