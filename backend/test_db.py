from app.database.connection import engine
from sqlalchemy import text

print("Engine URL:", engine.url)

try:
    with engine.connect() as conn:
        result = conn.execute(
            text("SELECT current_database(), current_user;")
        )

        print("[OK] Connected Successfully!")
        print(result.fetchone())

except Exception as e:
    import traceback

    print("[ERROR] Connection Failed")
    traceback.print_exc()