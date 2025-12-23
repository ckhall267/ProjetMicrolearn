from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import optimizer

app = FastAPI(title="MicroLearn HyperOpt Service")

class OptimizationRequest(BaseModel):
    study_name: str
    model_type: str # e.g., "random_forest", "xgboost"
    n_trials: int = 20
    direction: str = "maximize" # "maximize" or "minimize"
    metric: str = "accuracy"

@app.get("/")
def read_root():
    return {"service": "HyperOpt", "status": "active"}

@app.post("/optimize")
async def start_optimization(request: OptimizationRequest, background_tasks: BackgroundTasks):
    """
    Lance une tâche d'optimisation en arrière-plan.
    """
    job_id = optimizer.create_study_job(request)
    background_tasks.add_task(optimizer.run_optimization, job_id, request)
    return {"job_id": job_id, "status": "started", "message": "Optimization started in background"}

@app.get("/optimize/{job_id}")
def get_optimization_status(job_id: str):
    """
    Récupère le statut et les meilleurs paramètres d'une optimisation.
    """
    result = optimizer.get_study_result(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")
    return result
