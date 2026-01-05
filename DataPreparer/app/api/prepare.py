from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, Dict, List
from app.core.pipeline import apply_pipeline
from app.core.minio_client import download_file_from_minio, upload_file_to_minio, upload_raw_file_to_minio
from app.core.database import save_dataframe_to_db, engine
import pandas as pd
import os
import json
from sqlalchemy import text
import chardet  # <-- ajouté pour détecter l'encodage


router = APIRouter()

@router.get("/datasets")
def list_datasets():
    """Lister tous les datasets disponibles"""
    try:
        # Vérifier si la table existe d'abord (pour éviter crash au tout début)
        # Mais on suppose que 'dataset_metadata' est créé au premier upload.
        # On va tenter le select.
        query = text("SELECT dataset_id, original_path, created_at FROM dataset_metadata ORDER BY created_at DESC")
        # Note: created_at n'est peut-être pas dans le schéma actuel, on va vérifier le save.
        # Le save fait: metadata_df.to_sql("dataset_metadata", ...). Pandas crée la table.
        # Pandas n'ajoute pas created_at automatiquement sauf si dans le DF.
        # Dans prepare_dataset:
        # metadata_df = pd.DataFrame([{ "dataset_id": ..., ... }])
        # Donc pas de timestamp pour l'instant. On va juste select tout.
        
        query = text("SELECT dataset_id, original_path, table_name, rows, columns FROM dataset_metadata")
        result = pd.read_sql(query, engine)
        
        datasets = result.to_dict("records")
        # Parser les colonnes si c'est des strings JSON
        for d in datasets:
            if isinstance(d.get("columns"), str):
                d["columns"] = json.loads(d["columns"])
                
        return {"datasets": datasets}
    except Exception as e:
        # Si la table n'existe pas encore (aucun upload), on retourne vide
        if "relation \"dataset_metadata\" does not exist" in str(e):
             return {"datasets": []}
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des datasets: {str(e)}")


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
@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Endpoint pour uploader un dataset brut vers MinIO
    """
    try:
        # Lire le fichier en mémoire (attention aux gros fichiers, mais ok pour démo)
        contents = await file.read()
        file_size = len(contents)
        
        # Reset curseur pour upload
        await file.seek(0)
        
        # Nom du fichier dans MinIO (on garde le nom d'origine pour simplifier)
        filename = file.filename
        
        # Upload
        minio_path = upload_raw_file_to_minio(file.file, filename, file_size)
        
        # Enregistrer les métadonnées pour qu'il apparaisse dans la liste
        dataset_id = f"dataset_{pd.Timestamp.now().value}"
        
        # On ne connaît pas encore les colonnes/lignes car c'est brut,
        # mais on crée l'entrée pour qu'elle soit listable.
        metadata_df = pd.DataFrame([{
            "dataset_id": dataset_id,
            "table_name": None, # Pas encore de table SQL
            "original_path": minio_path,
            "cleaned_path": None,
            "rows": 0,
            "columns": json.dumps([]),
            "pipeline": json.dumps({})
        }])
        
        # Sauvegarde en bdd
        metadata_df.to_sql("dataset_metadata", engine, if_exists="append", index=False)

        return {
            "status": "success",
            "message": f"Fichier {filename} uploadé avec succès",
            "minio_path": minio_path,
            "filename": filename,
            "dataset_id": dataset_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'upload: {str(e)}")

