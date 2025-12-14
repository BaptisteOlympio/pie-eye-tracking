from enum import Enum
import asyncio

class CalibrationStatus(str, Enum) :
    IDLE = "idle"
    RUNNING = "running"

calibration_status = CalibrationStatus.IDLE
calibration_lock = asyncio.Lock()

class GazeVisualisationStatus(str, Enum) : 
    RUNNING = "running"
    NOT_RUNNING = "not running"

gaze_visualisation_status = GazeVisualisationStatus.NOT_RUNNING
gaze_visualisation_lock = asyncio.Lock()