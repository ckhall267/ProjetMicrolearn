from sqlalchemy import create_engine
import pandas as pd
import os

# Configuration de la base de données
user = os.getenv("POSTGRES_USER", "mluser")
password = os.getenv("POSTGRES_PASSWORD", "mlpass")
server = os.getenv("POSTGRES_SERVER", "localhost")
db_name = os.getenv("POSTGRES_DB", "microlearn")

DB_URL = os.getenv(
    "POSTGRES_URL",
    f"postgresql+psycopg2://{user}:{password}@{server}:5432/{db_name}"
)

# Création du moteur SQLAlchemy
engine = create_engine(DB_URL)

def save_dataframe_to_db(df, table_name):
    # Enregistrer le DataFrame dans PostgreSQL
    df.to_sql(table_name, engine, if_exists="replace", index=False)

