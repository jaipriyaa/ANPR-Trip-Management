import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="1234",      # Replace if your password is different
        database="anpr_db"
    )

    print("✅ Connected directly to anpr_db")

    conn.close()

except Exception as e:
    print("❌ Error")
    print(e)