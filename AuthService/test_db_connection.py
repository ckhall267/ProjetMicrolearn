from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import sys

# Configuration par défaut
DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/microlearn"

def test_connection():
    try:
        engine = create_engine(DATABASE_URL)
        connection = engine.connect()
        print("Successfully connected to the database!")
        connection.close()
        return True
    except OperationalError as e:
        print(f"Connection failed: {e}")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False

if __name__ == "__main__":
    if test_connection():
        sys.exit(0)
    else:
        sys.exit(1)
