from sqlalchemy import inspect
from database import engine

def inspect_table():
    inspector = inspect(engine)
    if inspector.has_table("utilisateurs"):
        columns = inspector.get_columns("utilisateurs")
        print("Columns in 'utilisateurs':")
        for col in columns:
            print(f"- {col['name']} ({col['type']})")
    else:
        print("Table 'utilisateurs' does not exist.")

if __name__ == "__main__":
    inspect_table()
