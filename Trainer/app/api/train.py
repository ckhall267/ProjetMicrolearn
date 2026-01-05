import os
import io
import uuid
import joblib
import pandas as pd
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import mlflow
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, Dict, Any
from minio import Minio
from sklearn.model_selection import train_test_split
# ... (imports sklearn standard existants) ...
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

router = APIRouter()

# --- Config infra ---
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "microlearn-data")
MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")

minio_client = Minio(MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY, secure=False)
mlflow.set_tracking_uri(MLFLOW_URI)
try:
    mlflow.set_experiment("MicroLearn_Experiments")
except:
    pass

# --- PyTorch Simple Model ---
class SimpleNN(nn.Module):
    def __init__(self, input_dim, output_dim, task="classification"):
        super(SimpleNN, self).__init__()
        self.layer1 = nn.Linear(input_dim, 64)
        self.relu = nn.ReLU()
        self.layer2 = nn.Linear(64, 32)
        self.output = nn.Linear(32, output_dim)
        self.task = task
        
    def forward(self, x):
        x = self.relu(self.layer1(x))
        x = self.relu(self.layer2(x))
        x = self.output(x)
        if self.task == "classification" and self.output.out_features == 1:
             return torch.sigmoid(x)
        return x

class TrainRequest(BaseModel):
    model_name: str
    dataset_path: str 
    target_column: str
    hyperparameters: Optional[Dict[str, Any]] = {}
    job_id: Optional[str] = None 

training_jobs = {}

def train_model_task(job_id: str, request: TrainRequest):
    try:
        training_jobs[job_id]["status"] = "running"
        
        # 1. Load Data
        response = minio_client.get_object(MINIO_BUCKET, request.dataset_path)
        df = pd.read_csv(io.BytesIO(response.read()))
        
        X = df.drop(columns=[request.target_column])
        y = df[request.target_column]
        X = pd.get_dummies(X)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
        
        # MLflow Run
        with mlflow.start_run(run_name=f"{request.model_name}_{job_id}"):
            mlflow.log_params(request.hyperparameters)
            mlflow.log_param("dataset", request.dataset_path)
            
            score = 0
            model_to_save = None
            
            # --- BRANCHE PYTORCH ---
            if request.model_name == "neural_network":
                # Convertir en Tensors
                X_train_t = torch.FloatTensor(X_train.values)
                y_train_t = torch.FloatTensor(y_train.values).unsqueeze(1) # Binary classification assumption
                
                input_dim = X_train.shape[1]
                model = SimpleNN(input_dim, 1)
                criterion = nn.BCELoss()
                optimizer = optim.Adam(model.parameters(), lr=request.hyperparameters.get("lr", 0.001))
                
                epochs = request.hyperparameters.get("epochs", 10)
                for epoch in range(epochs):
                    optimizer.zero_grad()
                    outputs = model(X_train_t)
                    loss = criterion(outputs, y_train_t)
                    loss.backward()
                    optimizer.step()
                    mlflow.log_metric("loss", loss.item(), step=epoch)
                
                # Eval simple
                with torch.no_grad():
                     X_test_t = torch.FloatTensor(X_test.values)
                     preds = model(X_test_t)
                     preds_cls = (preds > 0.5).float()
                     acc = (preds_cls.eq(torch.FloatTensor(y_test.values).unsqueeze(1))).sum() / len(y_test)
                     score = acc.item()
                     
                model_to_save = model # Should convert to script or save state_dict
                mlflow.pytorch.log_model(model, "model")
                
            # --- BRANCHE SCIKIT-LEARN ---
            else:
                # Fallback to sklearn logic (RandomForest, etc.)
                if request.model_name == "random_forest_clf":
                    model = RandomForestClassifier(**request.hyperparameters)
                else: 
                    model = LogisticRegression() # Default
                    
                model.fit(X_train, y_train)
                score = model.score(X_test, y_test)
                mlflow.sklearn.log_model(model, "model")
                model_to_save = model

            mlflow.log_metric("accuracy", score)
            training_jobs[job_id]["score"] = score
            
            # Save to MinIO (Binary for internal usage)
            buffer = io.BytesIO()
            joblib.dump(model_to_save, buffer) # Note: Joblib works for Torch models usually but save/load state_dict is better best practice. Keeping joblib for homogeneity here.
            buffer.seek(0)
            minio_client.put_object(MINIO_BUCKET, f"models/{job_id}.joblib", buffer, buffer.getbuffer().nbytes)
            
            training_jobs[job_id]["model_path"] = f"models/{job_id}.joblib"
            training_jobs[job_id]["status"] = "completed"
            
    except Exception as e:
        training_jobs[job_id]["status"] = "failed"
        training_jobs[job_id]["error"] = str(e)
        print(f"Error: {e}")

@router.post("/train")
async def start_training(request: TrainRequest, background_tasks: BackgroundTasks):
    job_id = request.job_id if request.job_id else str(uuid.uuid4())
    training_jobs[job_id] = {"status": "pending"}
    background_tasks.add_task(train_model_task, job_id, request)
    return {"job_id": job_id, "status": "submitted"}

@router.get("/train/{job_id}")
async def get_training_status(job_id: str):
    return training_jobs.get(job_id, {"status": "not_found"})
