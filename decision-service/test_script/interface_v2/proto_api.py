import asyncio
import json
import os
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse

# Import de ta logique métier (indépendant de la source)
from logic_wheel import DecisionWheel

app = FastAPI()

# ==============================================================================
# 1. COUCHE D'ABSTRACTION (INPUT)
# ==============================================================================

class GazeDriver:
    """Classe parent générique. Toute nouvelle source de données devra hériter de ça."""
    def get_gaze_data(self):
        """Doit retourner un dict: {'direction': str, 'face_id': int, ...}"""
        raise NotImplementedError("Chaque pilote doit implémenter cette méthode")

# ==============================================================================
# 2. PILOTE A : SIMULATEUR CLAVIER (Ce qu'on utilise aujourd'hui)
# ==============================================================================

class KeyboardDriver(GazeDriver):
    def __init__(self):
        self.current_direction = "CENTER"
        print(">>> PILOTE ACTIVÉ : CLAVIER (Simulation Web)")

    def set_direction(self, direction: str):
        """Méthode spécifique pour recevoir l'ordre du Web"""
        self.current_direction = direction

    def get_gaze_data(self):
        # On formate comme si ça venait du vrai tracker
        return {
            "direction": self.current_direction,
            "face_id": 0, 
            "timestamp": time.time()
        }

# ==============================================================================
# 3. PILOTE B : VRAI TRACKER (Ce que tu utiliseras demain)
# ==============================================================================

class ZMQInputDriver(GazeDriver):
    def __init__(self):
        # Ici tu mettras ton code de connexion (ex: zmq.Context(), socket...)
        print(">>> PILOTE ACTIVÉ : VRAI TRACKER (ZMQ)")
        pass

    def get_gaze_data(self):
        # Ici tu mettras : return socket.recv_json()
        return {"direction": "CENTER"} # Placeholder

# ==============================================================================
# 4. CONFIGURATION DU PILOTE ACTIF
# ==============================================================================

# C'est LA SEULE LIGNE à changer pour passer du clavier à la réalité !
active_driver = KeyboardDriver()
# active_driver = ZMQInputDriver() 

# ==============================================================================
# 5. BOUCLE PRINCIPALE (CERVEAU)
# ==============================================================================

async def run_decision_logic():
    print(">>> Démarrage de la Logique Métier")
    
    # Paramétrage de la roue (Logique pure)
    wheel = DecisionWheel(seuil_validation=20)
    
    try:
        while True:
            # A. ACQUISITION : On demande au pilote actif (peu importe qui c'est)
            raw_data = active_driver.get_gaze_data()
            
            # B. TRAITEMENT : On donne la direction brute à la roue
            # La roue gère le comptage, le seuil, la validation...
            wheel_result = wheel.update(raw_data['direction'])
            
            # C. DIFFUSION : On envoie le résultat visuel au HTML
            await manager.broadcast(json.dumps(wheel_result))
            
            # Cadence (20Hz)
            await asyncio.sleep(0.05)
            
    except Exception as e:
        print(f"Erreur critique dans la boucle logique: {e}")

# ==============================================================================
# 6. INFRASTRUCTURE WEB (AFFICHAGE & ROUTING)
# ==============================================================================

class ConnectionManager:
    def __init__(self):
        self.active_connections = []
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try: await connection.send_text(message)
            except: pass

manager = ConnectionManager()

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(run_decision_logic())

@app.get("/")
async def get():
    # Sert le fichier HTML (Vue)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, "templates", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Réception des messages venant du HTML
            data = await websocket.receive_text()
            
            # Si on est en mode Clavier, on met à jour le pilote
            if isinstance(active_driver, KeyboardDriver):
                cmd = json.loads(data)
                if "set_direction" in cmd:
                    active_driver.set_direction(cmd["set_direction"])
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket)