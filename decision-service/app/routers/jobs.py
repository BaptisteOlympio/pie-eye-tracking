from fastapi import APIRouter
from pydantic import BaseModel


class Job(BaseModel):
    id: int
    name: str
    status: str 

running_jobs=[]

jobs_router = APIRouter()

@jobs_router.get("/jobs/get_jobs")
async def get_jobs():
    
    return {"message": running_jobs}

@jobs_router.post("/jobs/start_jobs")
async def start_jobs(job : Job):
    if job.status != "on":
        return {"message": "job status is off"}
    running_jobs.append(job)
    # curl --json '{"id": 1,"name": "first job", "status" : "on"}' localhost:8083/jobs/start_jobs
    return {"message": f"added job {job.id}"}