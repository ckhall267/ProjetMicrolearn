FROM python:3.11-slim

RUN pip install --upgrade pip
RUN pip install mlflow==2.9.2 boto3 psycopg2-binary

WORKDIR /mlflow
CMD ["mlflow", "server", "--backend-store-uri", "sqlite:////mlflow/mlflow.db", "--default-artifact-root", "s3://mlflow/", "--host", "0.0.0.0"]
