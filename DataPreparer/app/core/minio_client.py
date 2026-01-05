from minio import Minio
from minio.error import S3Error
import pandas as pd
import os
import tempfile
from typing import Optional

# Configuration depuis les variables d'environnement ou valeurs par défaut
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minio")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minio123")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "microlearn-data")

client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

def ensure_bucket(bucket_name: str = MINIO_BUCKET):
    """Créer le bucket s'il n'existe pas"""
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
    except S3Error as e:
        print(f"Erreur lors de la création du bucket: {e}")

# S'assurer que le bucket existe au démarrage
# ensure_bucket()  <-- Commented out to prevent blocking on startup if MinIO is not available

def download_file_from_minio(path: str, bucket: Optional[str] = None) -> str:
    """
    Télécharger un fichier depuis MinIO
    
    Args:
        path: Chemin du fichier (peut être s3://bucket/file ou bucket/file ou juste file)
        bucket: Nom du bucket (optionnel, utilise MINIO_BUCKET par défaut)
    
    Returns:
        Chemin local du fichier téléchargé
    """
    bucket_name = bucket or MINIO_BUCKET
    
    # Nettoyer le path
    path = path.replace("s3://", "")
    if "/" in path:
        if path.startswith(bucket_name + "/"):
            file_path = path[len(bucket_name) + 1:]
        else:
            bucket_name, file_path = path.split("/", 1)
    else:
        file_path = path
    
    # Créer un fichier temporaire
    _, ext = os.path.splitext(file_path)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    temp_path = temp_file.name
    temp_file.close()
    
    try:
        client.fget_object(bucket_name, file_path, temp_path)
        return temp_path
    except S3Error as e:
        os.remove(temp_path)
        raise Exception(f"Erreur lors du téléchargement depuis MinIO: {e}")

def upload_file_to_minio(path: str, df: pd.DataFrame, bucket: Optional[str] = None) -> str:
    """
    Upload un DataFrame vers MinIO
    
    Args:
        path: Chemin de destination dans MinIO
        df: DataFrame pandas à uploader
        bucket: Nom du bucket (optionnel)
    
    Returns:
        Chemin complet dans MinIO
    """
    bucket_name = bucket or MINIO_BUCKET
    ensure_bucket(bucket_name)
    
    # Nettoyer le path
    path = path.replace("s3://", "")
    if "/" in path and not path.startswith(bucket_name + "/"):
        if path.startswith(bucket_name + "/"):
            file_path = path[len(bucket_name) + 1:]
        else:
            bucket_name, file_path = path.split("/", 1)
    else:
        file_path = path
    
    # Déterminer l'extension
    _, ext = os.path.splitext(file_path)
    if not ext:
        ext = ".csv"
        file_path += ext
    
    # Créer un fichier temporaire
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
    temp_path = temp_file.name
    temp_file.close()
    
    try:
        # Sauvegarder le DataFrame
        if ext == ".csv":
            df.to_csv(temp_path, index=False)
        elif ext == ".json":
            df.to_json(temp_path, orient="records", indent=2)
        else:
            df.to_csv(temp_path, index=False)  # Par défaut CSV
        
        # Upload vers MinIO
        client.fput_object(bucket_name, file_path, temp_path)
        
        return f"{bucket_name}/{file_path}"
    finally:
        # Nettoyer le fichier temporaire
        if os.path.exists(temp_path):
            os.remove(temp_path)

def upload_raw_file_to_minio(file_data, file_name: str, length: int, bucket: Optional[str] = None) -> str:
    """
    Upload un fichier brut (file-like object) vers MinIO
    """
    bucket_name = bucket or MINIO_BUCKET
    ensure_bucket(bucket_name)

    try:
        client.put_object(
            bucket_name,
            file_name,
            file_data,
            length=length,
            content_type="application/octet-stream"
        )
        return f"{bucket_name}/{file_name}"
    except S3Error as e:
        raise Exception(f"Erreur lors de l'upload vers MinIO: {e}")

