from sqlalchemy import create_engine
import pandas as pd
import os

DB_URL = os.getenv("POSTGRES_URL", "postgresql+psycopg2://postgres:postgres123@localhost:5432/microlearn")
engine = create_engine(DB_URL)

def save_dataframe_to_db(df, table_name):
    df.to_sql(table_name, engine, if_exists="replace", index=False)
