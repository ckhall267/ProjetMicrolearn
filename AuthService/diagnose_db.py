from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import sys

COMMON_PASSWORDS = [
    "postgres",
    "admin",
    "root",
    "1234",
    "password",
    "microlearn",
    ""  # Empty password
]

DB_NAME = "microlearn"
USER = "postgres"
HOST = "localhost"
PORT = "5432"

def try_connect(password):
    if password:
        url = f"postgresql://{USER}:{password}@{HOST}:{PORT}/{DB_NAME}"
        masked_url = f"postgresql://{USER}:****@{HOST}:{PORT}/{DB_NAME}"
    else:
        url = f"postgresql://{USER}@{HOST}:{PORT}/{DB_NAME}"
        masked_url = f"postgresql://{USER}@(none)@{HOST}:{PORT}/{DB_NAME}"
    
    print(f"Testing connection with: {masked_url} ... ", end="")
    try:
        engine = create_engine(url)
        # Try to connect
        with engine.connect() as conn:
            pass
        print("SUCCESS!")
        return url
    except OperationalError:
        print("FAILED (Auth failed or invalid)")
    except Exception as e:
        print(f"FAILED (Error: {e})")
    return None

def diagnose():
    print("--- Starting PostgreSQL Connection Diagnosis ---")
    for pwd in COMMON_PASSWORDS:
        success_url = try_connect(pwd)
        if success_url:
            print(f"\nFOUND WORKING CONFIGURATION!")
            print(f"Please update database.py with this password: '{pwd}'")
            return
    
    print("\n--- Diagnosis Finished ---")
    print("Could not connect with common passwords.")
    print("Please manually edit 'database.py' with your correct PostgreSQL password.")

if __name__ == "__main__":
    diagnose()
