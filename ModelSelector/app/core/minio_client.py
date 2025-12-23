"""
Client MinIO pour télécharger les datasets depuis le stockage object
"""
from minio import Minio
from minio.error import S3Error
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


def download_file_from_minio(path: str, bucket: Optional[str] = None) -> str:
    """
    Télécharger un fichier depuis MinIO
    
    Args:
        path: Chemin du fichier dans MinIO
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
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise Exception(f"Erreur lors du téléchargement depuis MinIO: {e}")

