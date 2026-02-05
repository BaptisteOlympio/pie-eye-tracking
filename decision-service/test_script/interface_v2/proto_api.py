import asyncio
import json
import os
import sys
from pathlib import Path
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

# Ajouter le répertoire parent (decision-service) au PYTHONPATH
decision_service_path = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(decision_service_path))

# ### Importation DES MODULES ###
# 1. DecisionWheel : ce qui gère l'état des roues incrémentales et donc la gestion de l'état des devices
# 2. FakeListDriver : Les "Yeux Virtuels" qui lisent le scénario de test.
# 3. SmartHomeSystem : La "Mémoire de la Maison" qui stocke l'état réel (Lumière ON/OFF, etc.).
from logic_wheel import DecisionWheel
from fake_decision import FakeListDriver
from smart_home import SmartHomeSystem

from app.services import process_frame

app = FastAPI()

# ==============================================================================
# GESTIONNAIRE D'INTERFACE (LE CERVEAU CONTEXTUEL)
# ==============================================================================
# Cette classe est responsable de savoir "Où on est" et "Ce qu'on affiche".
# Elle ne gère pas le regard, elle gère la logique de navigation.

class InterfaceManager:
    def __init__(self):
        # ### ÉTAT INITIAL ###
        # On commence toujours sur le MENU PRINCIPAL (Choix de la pièce)
        self.mode = "MENU_PRINCIPAL" 
        self.current_room = None        # Aucune pièce sélectionnée au début
        self.selected_device_index = 0  # Si on entre dans une pièce, on commence par le 1er objet
        self.home_system = SmartHomeSystem()  # Instance privée de la Smart Home
        
    # ### FONCTION VITALE : PRÉPARATION DE L'AFFICHAGE ###
    # Cette fonction est appelée à CHAQUE image (4 fois par seconde).
    # Son rôle : Regarder l'état de la maison et dire au HTML quoi écrire dans les cercles.
    def get_ui_context(self):
        # On prépare des variables vides par défaut
        labels = {"UP": "", "DOWN": "", "LEFT": "", "RIGHT": "", "CENTER": ""}
        room_name = "ACCUEIL"
        queue_data = [] 
        center_theme = "neutral" # Par défaut, le cercle central est gris
        
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
            # On demanself.de à la "Smart Home" la liste des objets de cette pièce
            devices = home_system.get_room_devices(self.current_room)
            
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

# On crée une instance unique du gestionnaire pour toute l'app
ui_manager = InterfaceManager()
manager = None 

# ==============================================================================
# BOUCLE PRINCIPALE (LE COEUR DU PROGRAMME)
# ==============================================================================

FREQUENCE_LECTURE = 1.0 # Vitesse de la boucle (Hz)

async def run_app_logic():
    print(f">>> Démarrage Domotique V5 (Design) - {FREQUENCE_LECTURE} Hz")
    
    # 1. Initialisation des composants
    driver = FakeListDriver() # Les Yeux (Simulation)
    wheel = DecisionWheel(seuil_validation=4, buffer_limit=2) # Le Filtre (Ergonomie)
    sleep_time = 1.0 / FREQUENCE_LECTURE
    
    try:
        while True:
            # --- ÉTAPE A : INPUT ---
            # On demande aux yeux : "Où regarde l'utilisateur ?" (ex: "UP")
            current_direction = driver.get_next_direction()
            
            # --- ÉTAPE B : FILTRAGE & LOGIQUE ---
            # On demande à la roue : "Est-ce une validation ou juste un coup d'œil ?"
            # La roue gère le buffer et le % de progression.
            wheel_result = wheel.update(current_direction)
            
            # --- ÉTAPE C : CONTEXTE VISUEL (AVANT ACTION) ---
            # C'est l'astuce pour le problème d'affichage ! 
            # On prend une "photo" de l'interface MAINTENANT, avant de changer l'état.
            # Cela permet d'afficher "OK" sur le bouton "ALLUMER" juste avant qu'il disparaisse.
            context_data = ui_manager.get_ui_context()
            
            # --- ÉTAPE D : VALIDATION & ACTION ---
            # Si la roue dit "C'est validé (100%) !"
            if wheel_result["validated"]:
                # On exécute l'action (Changer lumière, entrer salon...)
                ui_manager.process_validation(wheel_result["validated"])
                
                # On remet la roue à zéro pour éviter de re-cliquer tout de suite
                wheel.compteur = 0 
                wheel.direction_en_cours = "CENTER"

            # --- ÉTAPE E : ENVOI AU HTML ---
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
            
            # On envoie via WebSocket à la page web
            await manager.broadcast(json.dumps(data_to_send))
            
            # --- ÉTAPE F : ATTENTE ---
            # On dort un peu pour respecter la fréquence (0.25s)
            await asyncio.sleep(sleep_time)
            
    except Exception as e:
        print(f"Erreur App: {e}")

# ==============================================================================
# INFRASTRUCTURE SERVEUR (STANDARD FASTAPI)
# ==============================================================================
# Cette partie gère juste la "tuyauterie" technique du Web.

class ConnectionManager:
    """Gère la liste des navigateurs connectés"""
    def __init__(self): self.active_connections = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket): self.active_connections.remove(websocket)
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try: await connection.send_text(message)
            except: pass

manager = ConnectionManager()

# Au démarrage du serveur, on lance notre boucle logique (run_app_logic) en tâche de fond
@app.on_event("startup")
async def startup_event(): asyncio.create_task(run_app_logic())

# Sert la page HTML
@app.get("/")
async def get():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, "templates", "index.html")
    with open(html_path, "r", encoding="utf-8") as f: return HTMLResponse(content=f.read())

# Gère la connexion WebSocket temps réel
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True: await websocket.receive_text() # On écoute (même si on reçoit rien)
    except WebSocketDisconnect: manager.disconnect(websocket)