from sqlalchemy import create_engine, inspect
import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Chaimaakhalil%40123@localhost:5432/microlearn"
)

def list_columns():
    try:
        engine = create_engine(DATABASE_URL)
        inspector = inspect(engine)
        columns = inspector.get_columns("utilisateurs")
        with open("cols.txt", "w") as f:
            for col in columns:
                f.write(f"{col['name']}\n")
    except Exception as e:
        with open("cols.txt", "w") as f:
            f.write(f"ERROR: {e}")

if __name__ == "__main__":
    list_columns()
