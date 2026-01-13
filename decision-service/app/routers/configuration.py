from fastapi import APIRouter
from pydantic import BaseModel
import asyncio

from app.core import state
from app.services import process_frame

class Adress(BaseModel):
    ip: str
    port: str

configuration_router = APIRouter()

@configuration_router.post("/connect_video_service")
async def connect_video_service(adress : Adress) :
    await process_frame.process_frame_task(ip_vs=adress.ip, port_vs=adress.port)
    return {"status" : "success"}