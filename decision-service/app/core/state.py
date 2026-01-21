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

class VideoStatus(str, Enum) : 
    RUNNING = "running"
    NOT_RUNNING = "not running"

video_status = VideoStatus.NOT_RUNNING
video_lock = asyncio.Lock()

class VideoServiceConnection(str, Enum) :
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"

video_service_connection_status = VideoServiceConnection.DISCONNECTED
video_service_connection_lock = asyncio.Lock()