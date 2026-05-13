#!/bin/bash
# Create databases on first PostgreSQL initialization.
set -e

create_db_if_not_exists() {
  local db="$1"
  echo "Checking database '$db'..."
  if psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres -tc \
    "SELECT 1 FROM pg_database WHERE datname = '$db'" | grep -q 1; then
    echo "Database '$db' already exists."
  else
    echo "Creating database '$db'..."
    psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres -c \
      "CREATE DATABASE \"$db\""
  fi
}

create_db_if_not_exists "lks_database"
create_db_if_not_exists "keycloak_db"
create_db_if_not_exists "sonarqube"

echo "All databases ready."
