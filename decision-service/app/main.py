from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from fastapi.staticfiles import StaticFiles
from app.routers.interface import interface_router
from app.routers.ws import ws_router
from app.routers.configuration import configuration_router
from app.routers.jobs import jobs_router
from app.services import process_frame

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # 🔥 START LONG-RUNNING TASKS
#     process_task = asyncio.create_task(                   definir la task comme une varaible
#         process_frame.process_frame.process_frame()
#     )

#     try:
#         yield
#     finally:
#         # 🛑 GRACEFUL SHUTDOWN
#         process_task.cancel()                 pour arreter les task

#         await asyncio.gather(
#             process_task,
#             return_exceptions=True,
        # )

app = FastAPI() # lifespan=lifespan


app.mount("/templates", StaticFiles(directory="app/templates"), name="templates")
app.include_router(ws_router)
app.include_router(interface_router)
app.include_router(configuration_router)
app.include_router(jobs_router)
