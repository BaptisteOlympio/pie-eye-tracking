from fastapi import APIRouter
from pydantic import BaseModel
import asyncio

from app.core import state
from app.services import process_frame

class Adress(BaseModel):
    ip: str
    port: str

configuration_router = APIRouter()

tasks = dict()

@configuration_router.post("/connect_video_service")
async def connect_video_service(adress : Adress) :
    process_task = asyncio.create_task(                   #definir la task comme une varaible
        process_frame.process_frame.process_frame(ip_vs=adress.ip, port_vs=adress.port))
    state.process_frame_task = process_task
    tasks['process_frame_task'] = process_task

    # await process_frame.process_frame_task(ip_vs=adress.ip, port_vs=adress.port)
    return {"status" : "success"}