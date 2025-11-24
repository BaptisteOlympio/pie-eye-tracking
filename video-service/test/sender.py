import asyncio
import websockets

async def send_message():
    uri = "ws://192.168.178.46:8080"
    async with websockets.connect(uri) as websocket:
        msg = "Hello from Docker!"
        print(f"Sending: {msg}")
        await websocket.send(msg)
        reply = await websocket.recv()
        print(f"Received: {reply}")

if __name__ == "__main__":
    asyncio.run(send_message())
