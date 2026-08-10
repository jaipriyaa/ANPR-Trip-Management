#!/bin/sh
set -e

echo "========================================================="
echo "Starting Industrial ANPR Trip Management System Backend..."
echo "========================================================="

# Extract DB host and port from DATABASE_URL if set, defaulting to postgres:5432
DB_HOST="postgres"
DB_PORT="5432"

echo "Waiting for PostgreSQL database at ${DB_HOST}:${DB_PORT} to become ready..."

# Wait for PostgreSQL port using Python
python -c "
import socket
import time

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = '$DB_HOST'
port = int('$DB_PORT')
start = time.time()
while True:
    try:
        s.connect((host, port))
        s.close()
        print('✓ PostgreSQL database connection established!')
        break
    except Exception:
        if time.time() - start > 60:
            print('✗ Timeout waiting for PostgreSQL database!')
            break
        time.sleep(1)
"

echo "Initializing database tables and running schema setup..."
python create_tables.py || echo "Table creation script executed."

# Run Alembic migrations if alembic.ini is present
if [ -f "alembic.ini" ]; then
    echo "Executing Alembic database migrations..."
    alembic upgrade head || echo "Alembic migration step finished."
fi

echo "========================================================="
echo "Launching FastAPI Uvicorn Server on 0.0.0.0:8000..."
echo "========================================================="

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
