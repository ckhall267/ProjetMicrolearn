from fastapi import FastAPI
from .pipeline import apply_pipeline
from .minio_client import download_file_from_minio, upload_file_to_minio  # <-- corrigé
import pandas as pd
import yaml
import json

app = FastAPI()

@app.post("/prepare")
def prepare_dataset(file_path: str, pipeline: dict):
    """
    Endpoint pour préparer un dataset :
    1. Télécharger depuis MinIO
    2. Charger avec pandas
    3. Appliquer le pipeline de transformations
    4. Sauvegarder le dataset nettoyé dans MinIO
    """
    # 1. Télécharger le fichier depuis MinIO
    local_file = download_file_from_minio(file_path)

    # 2. Charger les données dans pandas
    df = pd.read_csv(local_file)

    # 3. Appliquer le pipeline
    df = apply_pipeline(df, pipeline)

    # 4. Sauvegarder la version nettoyée dans MinIO
    cleaned_path = "cleaned/" + local_file
    upload_file_to_minio(cleaned_path, df)

    return {
        "status": "success",
        "cleaned_dataset_path": cleaned_path
    }
