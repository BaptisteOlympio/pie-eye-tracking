from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers.interface import interface_router
from app.routers.ws import ws_router

app = FastAPI()
app.mount("/templates", StaticFiles(directory="app/templates"), name="templates")
app.include_router(ws_router)
app.include_router(interface_router)
