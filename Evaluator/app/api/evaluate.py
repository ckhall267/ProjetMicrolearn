import os
import io
import joblib
import pandas as pd
import json
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from minio import Minio
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, confusion_matrix, mean_squared_error, r2_score
from sqlalchemy import create_engine, Column, String, Float, JSON, DateTime, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

router = APIRouter()

# --- Configuration MinIO ---
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "microlearn-data")

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

# --- Configuration PostgreSQL ---
POSTGRES_USER = os.getenv("POSTGRES_USER", "mluser")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "mlpass")
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
POSTGRES_DB = os.getenv("POSTGRES_DB", "microlearn")
DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class EvaluationLog(Base):
    __tablename__ = "evaluation_logs"
    id = Column(Integer, primary_key=True, index=True)
    model_path = Column(String, index=True)
    dataset_path = Column(String)
    metrics = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

# Création de la table si elle n'existe pas
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning: Could not connect to DB to create tables: {e}")

class EvaluationRequest(BaseModel):
    model_path: str 
    dataset_path: str 
    target_column: str
    task_type: str = "classification" 

@router.post("/evaluate")
async def evaluate_model(request: EvaluationRequest):
    try:
        # ... (Chargement MinIO identique) ...
        try:
            model_response = minio_client.get_object(MINIO_BUCKET, request.model_path)
            model_buffer = io.BytesIO(model_response.read())
            model = joblib.load(model_buffer)
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Failed to load model: {str(e)}")

        try:
            data_response = minio_client.get_object(MINIO_BUCKET, request.dataset_path)
            df = pd.read_csv(io.BytesIO(data_response.read()))
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"Failed to load dataset: {str(e)}")

        if request.target_column not in df.columns:
            raise HTTPException(status_code=400, detail=f"Target column '{request.target_column}' not found")

        X = df.drop(columns=[request.target_column])
        y = df[request.target_column]
        X = pd.get_dummies(X) 
        
        # Prédiction
        y_pred = model.predict(X)

        # Calcul Métriques
        metrics = {}
        if request.task_type == "classification":
            metrics["accuracy"] = float(accuracy_score(y, y_pred))
            try:
                metrics["f1"] = float(f1_score(y, y_pred, average='weighted'))
                metrics["precision"] = float(precision_score(y, y_pred, average='weighted'))
            except:
                metrics["f1"] = 0.0 # Fallback
            
            metrics["confusion_matrix"] = confusion_matrix(y, y_pred).tolist()
            
        elif request.task_type == "regression":
            metrics["mse"] = float(mean_squared_error(y, y_pred))
            metrics["r2"] = float(r2_score(y, y_pred))

        # --- Persistance PostgreSQL ---
        try:
            db = SessionLocal()
            log_entry = EvaluationLog(
                model_path=request.model_path,
                dataset_path=request.dataset_path,
                metrics=metrics
            )
            db.add(log_entry)
            db.commit()
            db.close()
        except Exception as e:
            print(f"Database error: {e}")

        return {
            "model_path": request.model_path,
            "metrics": metrics,
            "status": "saved_to_db"
        }

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
