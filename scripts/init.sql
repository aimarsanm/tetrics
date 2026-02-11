-- Initialize databases for Tetrics project
-- This script runs only on first container initialization

-- Create lks_database if it doesn't exist
SELECT 'CREATE DATABASE lks_database'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'lks_database')\gexec

-- Create sonarqube database if it doesn't exist
SELECT 'CREATE DATABASE sonarqube'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'sonarqube')\gexec

-- Create keycloak user if it doesn't exist
DO
$$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'keycloak') THEN
    CREATE ROLE keycloak WITH LOGIN PASSWORD 'keycloak';
  END IF;
END
$$;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE lks_database TO keycloak;
GRANT ALL PRIVILEGES ON DATABASE sonarqube TO keycloak;
