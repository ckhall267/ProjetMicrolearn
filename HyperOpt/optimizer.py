import optuna
import uuid
import time
import requests
import os
import redis
import json
from typing import Dict, Any

# Connection Redis pour stocker l'état des jobs (indépendant d'Optuna)
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
# Note: On utilise le host 'redis' qui est le nom du service docker
try:
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
except:
    print("Warning: Redis not connected")

# Configuration des URLs des autres services
TRAINER_API_URL = os.getenv("TRAINER_API_URL", "http://localhost:8002/api/v1") 

def create_study_job(request) -> str:
    job_id = str(uuid.uuid4())
    job_data = {
        "request": request.dict(),
        "status": "pending",
        "best_params": None,
        "best_value": None,
        "trials_completed": 0,
        "created_at": time.time()
    }
    # Sauvegarde dans Redis (TTL 24h)
    redis_client.setex(f"job:{job_id}", 86400, json.dumps(job_data))
    return job_id

def get_study_result(job_id: str) -> Dict[str, Any]:
    data = redis_client.get(f"job:{job_id}")
    if data:
        return json.loads(data)
    return None

def update_job_status(job_id, updates):
    """Helper pour mettre à jour partiellement le statut dans Redis"""
    data = get_study_result(job_id)
    if data:
        data.update(updates)
        redis_client.setex(f"job:{job_id}", 86400, json.dumps(data))

def objective(trial, request):
    """
    Fonction objective qui orchestre l'entraînement réel.
    """
    # 1. Définition de l'espace de recherche
    hyperparameters = {}
    
    if request.model_type == "random_forest_clf":
        hyperparameters["n_estimators"] = trial.suggest_int("n_estimators", 10, 200)
        hyperparameters["max_depth"] = trial.suggest_int("max_depth", 2, 32)
    elif request.model_type == "xgboost":
         hyperparameters["n_estimators"] = trial.suggest_int("n_estimators", 50, 300)
         hyperparameters["learning_rate"] = trial.suggest_float("learning_rate", 0.01, 0.3)
    elif request.model_type == "logistic_regression":
        hyperparameters["C"] = trial.suggest_float("C", 0.001, 10.0, log=True)
    elif request.model_type == "neural_network":
        hyperparameters["epochs"] = trial.suggest_int("epochs", 5, 20)
        hyperparameters["lr"] = trial.suggest_float("lr", 1e-4, 1e-1, log=True)
    
    # 2. Appel au Trainer Service
    trainer_payload = {
        "model_name": request.model_type,
        "dataset_path": request.dataset_path,
        "target_column": request.target_column,
        "hyperparameters": hyperparameters,
        "job_id": f"trial_{trial.number}_{uuid.uuid4().hex[:8]}" 
    }
    
    try:
         # On utilise le nom de service 'trainer' dans docker interne
        internal_url = TRAINER_API_URL.replace("localhost", "trainer")
        response = requests.post(f"{internal_url}/train", json=trainer_payload)
        response.raise_for_status()
        train_job_id = response.json().get("job_id")
    except Exception as e:
        print(f"Failed to submit training job: {e}")
        # En fallback si on teste hors docker...
        try:
             response = requests.post(f"{TRAINER_API_URL}/train", json=trainer_payload)
             train_job_id = response.json().get("job_id")
        except:
             raise optuna.exceptions.TrialPruned()

    # 3. Polling
    max_retries = 60 
    for _ in range(max_retries):
        try:
            status_res = requests.get(f"{internal_url}/train/{train_job_id}")
            status_data = status_res.json()
            status = status_data.get("status")
            
            if status == "completed":
                return status_data.get("score")
            elif status == "failed":
                raise optuna.exceptions.TrialPruned()
            
            time.sleep(2) 
        except Exception:
            time.sleep(2)
            
    raise optuna.exceptions.TrialPruned("Timeout")

def run_optimization(job_id: str, request):
    print(f"Starting optimization for job {job_id}")
    update_job_status(job_id, {"status": "running"})
    
    try:
        # Stockage Optuna dans Redis pour la persistance des Essais
        study_name = f"study_{job_id}"
        
        study = optuna.create_study(
            study_name=study_name,
            storage=REDIS_URL, # Persistance Redis !
            direction=request.direction,
            load_if_exists=True
        )
        
        study.optimize(lambda trial: objective(trial, request), n_trials=request.n_trials)
        
        update_job_status(job_id, {
            "status": "completed",
            "best_params": study.best_params,
            "best_value": study.best_value,
            "trials_completed": len(study.trials)
        })
        print(f"Job {job_id} completed.")
        
    except Exception as e:
        print(f"Job {job_id} failed: {e}")
        update_job_status(job_id, {
            "status": "failed",
            "error": str(e)
        })
