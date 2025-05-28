from sqlalchemy import text
from app.database import engine

def test_db_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("Connection successful! Result:", result.scalar())
    except Exception as e:
        print("Connection failed:", e)

if __name__ == "__main__":
    test_db_connection()
