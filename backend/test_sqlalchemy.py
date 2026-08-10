from sqlalchemy import text
from app.database.connection import engine

try:
    with engine.connect() as conn:
        print("✅ Connected!")

        print("Current Database:")
        print(conn.execute(text("SELECT current_database();")).fetchone())

        print("\nDatabases:")
        print(conn.execute(text("SELECT datname FROM pg_database;")).fetchall())

except Exception as e:
    print("❌ Error:")
    print(e)