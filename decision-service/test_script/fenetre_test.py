import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import zmq
import zmq.asyncio

app = FastAPI()

html = """
<!DOCTYPE html>
<html>
<head>
    <title>Realtime Dot</title>
    <style>
        #canvas {
            border: 2px solid black;
        }
    </style>
</head>
<body>
    <h1>Realtime Dot Visualization</h1>
    <canvas id="canvas" width="400" height="400"></canvas>

    <script>
        const canvas = document.getElementById("canvas");
        const ctx = canvas.getContext("2d");
        const ws = new WebSocket("ws://localhost:8083/ws");

        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            const x = data.x * canvas.width;  // normalize from [-1,1] to [0,width]
            const y = data.y * canvas.height; // normalize from [-1,1] to [0,height]

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.beginPath();
            ctx.arc(x, y, 10, 0, 2 * Math.PI);
            ctx.fillStyle = "red";
            ctx.fill();
        };
    </script>
</body>
</html>
"""

@app.get("/")
async def get():
    return HTMLResponse(html)

# WebSocket manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await asyncio.sleep(1)  # keep connection alive
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ZMQ Subscriber
async def zmq_subscriber():
    context = zmq.asyncio.Context()
    socket = context.socket(zmq.SUB)
    socket.connect("tcp://172.26.128.105:8081")
    socket.setsockopt(zmq.SUBSCRIBE, b"")
    print("Listening on : tcp://172.26.128.105:8081...")

    while True:
        data = await socket.recv_json()
        x = 0.5*(data["gaze_angle_x"] + 0.195)/(0.056 + 0.195) 
        y = 0.5*(data["gaze_angle_y"] + 0.150)/(0.177 + 0.150) 
        message = json.dumps({"x": x, "y": y})
        await manager.broadcast(message)

# Run ZMQ subscriber in background
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(zmq_subscriber())
