#!/bin/bash
set -e

echo "Waiting for PostgreSQL to be ready..."
until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
  echo "PostgreSQL is unavailable - sleeping..."
  sleep 1
done

echo "PostgreSQL is ready!"
echo "Running Alembic migrations..."
poetry run alembic upgrade head

echo "Starting Uvicorn server..."
exec poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
