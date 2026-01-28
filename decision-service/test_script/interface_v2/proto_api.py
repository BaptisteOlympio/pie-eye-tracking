import asyncio
import json
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse


from logic_wheel import DecisionWheel
#pour simuler une séquence d'envoie (plus de clavier, fake_decision.py envoie une direction de regard à l'app)
from fake_decision import FakeListDriver

app = FastAPI()

# ==============================================================================
# PARAMÈTRES DE L'APPLICATION
# ==============================================================================

# fréq de lecture du système : 4.0 Hz = 4 lectures par seconde (donc 1 incrément toutes les 0.25s)
FREQUENCE_LECTURE = 1 

# ==============================================================================
# BOUCLE PRINCIPALE
# ==============================================================================

async def run_app_logic():
    print(f">>> Démarrage de l'App (Fréquence: {FREQUENCE_LECTURE} Hz)")
    
    # Initialisation des composants
    driver = FakeListDriver()             
    wheel = DecisionWheel(seuil_validation=4, buffer_limit=3) 
    # Calcul du temps de pause (ex: 1/4 = 0.25 sec)
    sleep_time = 1.0 / FREQUENCE_LECTURE
    
    try:
        while True:
            # -------------------------------------------------------
            # ÉTAPE 1 : INPUT (On récupère juste UNE direction donc soit haut, soit gauche, soit bas, soit droite)
            # -------------------------------------------------------
            current_direction = driver.get_next_direction()
            
            # -------------------------------------------------------
            # ÉTAPE 2 : LOGIQUE (On met à jour la roue)
            # -------------------------------------------------------
            wheel_result = wheel.update(current_direction)
            
            # -------------------------------------------------------
            # ÉTAPE 3 : OUTPUT (On envoie à l'écran)
            # -------------------------------------------------------
            # On ajoute l'info debug pour voir ce qui entre
            wheel_result["debug_info"] = f"Input reçu: {current_direction}"
            
            await manager.broadcast(json.dumps(wheel_result))
            
            # -------------------------------------------------------
            # ÉTAPE 4 : FRÉQUENCE (On attend le prochain cycle)
            # -------------------------------------------------------
            await asyncio.sleep(sleep_time)
            
    except Exception as e:
        print(f"Erreur App: {e}")

# ==============================================================================
# INFRASTRUCTURE WEB 
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
    asyncio.create_task(run_app_logic())

@app.get("/")
async def get():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(base_dir, "templates", "index.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text() # On écoute mais on fait rien
    except WebSocketDisconnect:
        manager.disconnect(websocket)