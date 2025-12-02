from minio import Minio
import pandas as pd
import os

client = Minio(
    "localhost:9000",
    access_key="minio",
    secret_key="minio123",
    secure=False
)

def download_file_from_minio(path):
    bucket, file = path.replace("s3://", "").split("/", 1)
    local_path = file

    client.fget_object(bucket, file, local_path)
    return local_path

def upload_file_to_minio(path, df):
    bucket, file = path.split("/", 1)
    local_path = "temp_cleaned.csv"

    df.to_csv(local_path, index=False)
    client.fput_object(bucket, file, local_path)
