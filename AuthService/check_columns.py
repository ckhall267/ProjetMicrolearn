from sqlalchemy import create_engine, inspect
import os

# Configuration de la base de données (déjà corrigée)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Chaimaakhalil%40123@localhost:5432/microlearn"
)

def list_columns():
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        
        if inspector.has_table("utilisateurs"):
            print("--- Colonnes de la table 'utilisateurs' ---")
            columns = inspector.get_columns("utilisateurs")
            for col in columns:
                print(f"Nom: {col['name']}, Type: {col['type']}")
        else:
            print("La table 'utilisateurs' n'existe pas.")
            
    except Exception as e:
        print(f"Erreur lors de l'inspection : {e}")

if __name__ == "__main__":
    list_columns()
