from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Configuration de la base de données
# On utilise user=postgres car c'est ce que l'utilisateur a utilisé dans sa commande psql
# Le mot de passe contient un @, on le remplace par %40 pour qu'il soit valide dans l'URL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Chaimaakhalil%40123@localhost:5432/microlearn"
)

# Note: Si le mot de passe est différent, l'utilisateur devra le définir via la variable d'env

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
