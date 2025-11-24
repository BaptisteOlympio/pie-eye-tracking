import asyncio
import websockets
from websockets.exceptions import InvalidHandshake

async def echo(websocket):
    async for message in websocket:
        print("Received and echoing message: " + message, flush=True)
        await websocket.send(message)

async def handle_http(reader, writer):
    """Handle plain HTTP requests for health checks."""
    request_line = await reader.readline()
    if not request_line:
        writer.close()
        await writer.wait_closed()
        return

    request = request_line.decode().strip()
    if request.startswith("GET /health") or request.startswith("GET / "):
        response_body = b"OK\n"
        response = (
            b"HTTP/1.1 200 OK\r\n"
            b"Content-Type: text/plain\r\n"
            b"Content-Length: " + str(len(response_body)).encode() + b"\r\n"
            b"\r\n" + response_body
        )
    else:
        response_body = b"Not Found\n"
        response = (
            b"HTTP/1.1 404 Not Found\r\n"
            b"Content-Type: text/plain\r\n"
            b"Content-Length: " + str(len(response_body)).encode() + b"\r\n"
            b"\r\n" + response_body
        )

    writer.write(response)
    await writer.drain()
    writer.close()
    await writer.wait_closed()

async def main():
    # Start WebSocket server
    port_websocket = 8080
    ws_server = await websockets.serve(echo, "0.0.0.0", port_websocket)
    print(f"✅ WebSocket echo server started on ws://0.0.0.0:{port_websocket}", flush=True)

    # Start HTTP health-check server (on same port)
    port_http = 8081
    http_server = await asyncio.start_server(handle_http, "0.0.0.0", port_http)
    print(f"✅ HTTP health endpoint ready at http://localhost:{port_http}/health", flush=True)

    async with ws_server,http_server: #  
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
