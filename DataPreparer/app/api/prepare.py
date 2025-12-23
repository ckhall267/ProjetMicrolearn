from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List
from app.core.pipeline import apply_pipeline
from app.core.minio_client import download_file_from_minio, upload_file_to_minio
from app.core.database import save_dataframe_to_db, engine
import pandas as pd
import os
import json
from sqlalchemy import text
import chardet  # <-- ajouté pour détecter l'encodage

router = APIRouter()

class PipelineStep(BaseModel):
    name: str
    strategy: Optional[str] = None
    method: Optional[str] = None
    columns: Optional[List[str]] = None

class PipelineConfig(BaseModel):
    steps: List[PipelineStep]

class PrepareRequest(BaseModel):
    file_path: str
    pipeline: Dict
    dataset_id: Optional[str] = None

# ===== Fonctions pour lire les fichiers avec encodage automatique =====
def read_csv_with_encoding(file_path):
    rawdata = open(file_path, "rb").read()
    encoding = chardet.detect(rawdata)['encoding']
    return pd.read_csv(file_path, encoding=encoding)

def read_json_with_encoding(file_path):
    rawdata = open(file_path, "rb").read()
    encoding = chardet.detect(rawdata)['encoding']
    return pd.read_json(file_path, encoding=encoding)

@router.post("/prepare")
def prepare_dataset(request: PrepareRequest):
    """
    Endpoint pour préparer un dataset :
    1. Télécharger depuis MinIO
    2. Charger avec pandas
    3. Appliquer le pipeline de transformations
    4. Sauvegarder le dataset nettoyé dans MinIO et PostgreSQL
    """
    try:
        # 1. Télécharger le fichier depuis MinIO
        local_file = download_file_from_minio(request.file_path)

        # 2. Charger les données dans pandas avec détection automatique d'encodage
        if local_file.endswith('.csv'):
            df = read_csv_with_encoding(local_file)
        elif local_file.endswith('.json'):
            df = read_json_with_encoding(local_file)
        else:
            raise HTTPException(status_code=400, detail="Format de fichier non supporté. Utilisez CSV ou JSON.")

        # 3. Appliquer le pipeline
        df_cleaned = apply_pipeline(df, request.pipeline)

        # 4. Sauvegarder la version nettoyée dans MinIO
        cleaned_path = f"cleaned/{os.path.basename(request.file_path)}"
        upload_file_to_minio(cleaned_path, df_cleaned)

        # 5. Générer un ID de dataset unique
        dataset_id = request.dataset_id or f"dataset_{pd.Timestamp.now().value}"
        
        # 6. Sauvegarder le DataFrame nettoyé dans PostgreSQL
        table_name = f"dataset_{dataset_id}".replace("-", "_").replace(".", "_")
        save_dataframe_to_db(df_cleaned, table_name)

        # 7. Sauvegarder les métadonnées dans une table séparée
        metadata_df = pd.DataFrame([{
            "dataset_id": dataset_id,
            "table_name": table_name,
            "original_path": request.file_path,
            "cleaned_path": cleaned_path,
            "rows": len(df_cleaned),
            "columns": json.dumps(list(df_cleaned.columns)),
            "pipeline": json.dumps(request.pipeline)
        }])
        metadata_df.to_sql("dataset_metadata", engine, if_exists="append", index=False)

        # Nettoyer le fichier temporaire
        if os.path.exists(local_file):
            os.remove(local_file)

        return {
            "status": "success",
            "dataset_id": dataset_id,
            "cleaned_dataset_path": cleaned_path,
            "table_name": table_name,
            "metadata": {
                "rows": len(df_cleaned),
                "columns": list(df_cleaned.columns),
                "shape": df_cleaned.shape
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la préparation: {str(e)}")

@router.get("/prepare/{dataset_id}")
def get_prepared_dataset(dataset_id: str):
    """Récupérer les informations d'un dataset préparé"""
    try:
        query = text("SELECT * FROM dataset_metadata WHERE dataset_id = :dataset_id")
        result = pd.read_sql(query, engine, params={"dataset_id": dataset_id})
        
        if result.empty:
            raise HTTPException(status_code=404, detail="Dataset non trouvé")
        
        metadata = result.iloc[0].to_dict()
        
        if isinstance(metadata.get("columns"), str):
            metadata["columns"] = json.loads(metadata["columns"])
        
        if isinstance(metadata.get("pipeline"), str):
            metadata["pipeline"] = json.loads(metadata["pipeline"])
        
        table_name = metadata.get("table_name")
        if table_name:
            if all(c.isalnum() or c == '_' for c in table_name):
                sample_query = text(f'SELECT * FROM "{table_name}" LIMIT 10')
                sample_data = pd.read_sql(sample_query, engine)
                metadata["sample_data"] = sample_data.to_dict("records")
        
        return metadata
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")
