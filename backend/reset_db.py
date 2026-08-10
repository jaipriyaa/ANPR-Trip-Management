from app.database.connection import engine
from sqlalchemy import text

print("Resetting database schema...")
with engine.connect() as conn:
    conn.execute(text("DROP SCHEMA public CASCADE;"))
    conn.execute(text("CREATE SCHEMA public;"))
    conn.commit()

print("Schema reset successfully!")
