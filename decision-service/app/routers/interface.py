from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse
from app.services import gaze
from app.services import calibration
from app.services import perf 
from app.services import process_frame
from app.services import IHM
from app.core import state


interface_router = APIRouter()

@interface_router.get("/interface/")
async def get_home() :
    with open("app/templates/home/index.html") as file : 
        return HTMLResponse(content=file.read())

# TODO a enlever
@interface_router.get("/interface/gaze_visualisation")
async def get_gaze_visualisation(background_tasks : BackgroundTasks) :
    background_tasks.add_task(gaze.gaze_visualisation)
    with open("app/templates/gaze_visualisation/index.html") as file:
        return HTMLResponse(content=file.read())

@interface_router.get("/interface/calibration")
async def get_calibration(background_tasks : BackgroundTasks) :
    if state.calibration_status == state.CalibrationStatus.RUNNING :
        raise HTTPException(
            status_code=409,
            detail="La calibration tourne déjà"
        )
        
    background_tasks.add_task(calibration.calibration_task)
    
    with open("app/templates/calibration/index.html") as file:
        return HTMLResponse(content=file.read())

@interface_router.get("/interface/perf")
async def get_perf(background_tasks : BackgroundTasks) :
    background_tasks.add_task(perf.video_task)
    with open("app/templates/perf/index.html") as file : 
        return HTMLResponse(content=file.read())

@interface_router.get("/interface/IHM")
async def get_IHM(background_tasks : BackgroundTasks) :
    background_tasks.add_task(IHM.IHM_task)
    with open("app/templates/IHM/index.html") as file : 
        return HTMLResponse(content=file.read())