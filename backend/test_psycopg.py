import psycopg2

try:
    conn = psycopg2.connect(
        host="localhost",
        port=5432,
        user="postgres",
        password="1234",   # replace if your password is different
        database="postgres"   # <-- connect to the default database first
    )

    print("✅ Connected to PostgreSQL!")

    cur = conn.cursor()
    cur.execute("SELECT datname FROM pg_database;")

    print("\nDatabases:")
    for row in cur.fetchall():
        print(row[0])

    conn.close()

except Exception as e:
    print("❌ Error:")
    print(e)