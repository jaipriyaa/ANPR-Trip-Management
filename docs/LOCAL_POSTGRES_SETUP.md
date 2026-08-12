# Local Native PostgreSQL Setup Guide

This guide details how to configure and run the **ANPR & Vehicle Trip Management Platform** using a **Local Native PostgreSQL Installation** (without Docker).

---

## 1. Prerequisites & Installation

### Windows Installation
1. Download PostgreSQL 16 installer from [postgresql.org](https://www.postgresql.org/download/windows/).
2. Run the installer and set superuser password (`1234` or custom password).
3. Ensure PostgreSQL Service (`postgresql-x64-16`) is running in `services.msc`.

### Linux / Ubuntu Installation
```bash
sudo apt update
sudo apt install -y postgresql postgresql-contrib
sudo systemctl enable --now postgresql
```

---

## 2. Database Creation & User Setup

Run `psql` shell to create the database:

```sql
-- Connect via psql
psql -U postgres -h localhost

-- Create database
CREATE DATABASE anpr_db;

-- Grant permissions (if using custom user)
GRANT ALL PRIVILEGES ON DATABASE anpr_db TO postgres;
```

---

## 3. Environment Configuration (`.env`)

Configure your `.env` file in the project root:

```env
DATABASE_URL=postgresql://postgres:1234@localhost:5432/anpr_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=1234
POSTGRES_DB=anpr_db
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

---

## 4. Run Backend Database Migrations & Table Creation

```bash
# From project root
backend\venv\Scripts\python.exe -c "from app.database.connection import engine, Base; Base.metadata.create_all(bind=engine)"
```

---

## 5. Verify Local Database Connection

Run the regression test suite against local PostgreSQL:

```bash
backend\venv\Scripts\python.exe -m pytest
```
