# Keycloak Setup & Configuration

This project uses [Keycloak](https://www.keycloak.org/) for authentication and role-based access control.

## Quick Start

```bash
# Start all services (PostgreSQL, Keycloak, FastAPI)
docker-compose up -d

# Keycloak will be available at:
# http://localhost:8080
```

Keycloak starts with the `--import-realm` flag, which automatically imports the realm configuration from `keycloak-config/tetrics-realm.json`.

## Keycloak Admin Console

| Setting    | Value                  |
|------------|------------------------|
| URL        | http://localhost:8080  |
| Username   | `admin`                |
| Password   | `admin123` (from `KEYCLOAK_ADMIN_PASSWORD` in `.env`) |

## Realm Configuration

- **Realm:** `tetrics`
- **Client:** `fastapi-client` (OpenID Connect, confidential)
- **Client Secret:** `fastapi-client-secret-123`

### Roles

| Role    | Description                                    |
|---------|------------------------------------------------|
| `admin` | Full CRUD access to all resources              |
| `user`  | Read-only access + can create measurements     |

### Pre-configured Users

| Username   | Password   | Roles           |
|------------|------------|-----------------|
| `admin`    | `admin123` | `admin`, `user` |
| `testuser` | `test123`  | `user`          |

## Authorization Rules

| Endpoint                          | Admin | User |
|-----------------------------------|-------|------|
| `GET /api/v1/*`                   |       |      |
| `POST /api/v1/domain/measurements/` |       |      |
| `POST /api/v1/users/sync`         |       |      |
| All other `POST`/`PUT`/`DELETE`   |       | —    |

## Getting a Token

Use the included helper script:

```bash
python scripts/get_token.py
```

Or request a token manually via curl:

```bash
curl -X POST \
  http://localhost:8080/realms/tetrics/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=fastapi-client" \
  -d "client_secret=fastapi-client-secret-123" \
  -d "username=admin" \
  -d "password=admin123" \
  -d "grant_type=password"
```

The response includes an `access_token`:

```json
{
  "access_token": "eyJhbGciOi...",
  "expires_in": 300,
  "refresh_token": "eyJhbGciOi...",
  "token_type": "Bearer"
}
```

## Calling the API

Include the access token as a Bearer token in the Authorization header:

```bash
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/v1/domain/metrics/
```

### Example: admin creating a metric

```bash
# Get admin token
TOKEN=$(curl -s -X POST \
  http://localhost:8080/realms/tetrics/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=fastapi-client" \
  -d "client_secret=fastapi-client-secret-123" \
  -d "username=admin" \
  -d "password=admin123" \
  -d "grant_type=password" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Create a metric (admin only)
curl -X POST http://localhost:8000/api/v1/domain/metrics/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "accuracy", "description": "Model accuracy metric"}'
```

### Example: user adding a measurement

```bash
# Get testuser token
TOKEN=$(curl -s -X POST \
  http://localhost:8080/realms/tetrics/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "client_id=fastapi-client" \
  -d "client_secret=fastapi-client-secret-123" \
  -d "username=testuser" \
  -d "password=test123" \
  -d "grant_type=password" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Add a measurement (allowed for users)
curl -X POST http://localhost:8000/api/v1/domain/measurements/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"value": 0.95, "metric_id": "<metric-uuid>", "llm_tool_configuration_id": "<config-uuid>"}'

# Try to create a metric (forbidden for users)
curl -X POST http://localhost:8000/api/v1/domain/metrics/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "precision"}'
# Returns: 403 - Role 'admin' required
```

## Configuration Reference

### Environment Variables

| Variable                    | Default                    | Description                          |
|-----------------------------|----------------------------|--------------------------------------|
| `KEYCLOAK_SERVER_URL`       | `http://localhost:8080`    | Keycloak server URL                  |
| `KEYCLOAK_REALM`            | `tetrics`                  | Realm name                           |
| `KEYCLOAK_CLIENT_ID`        | `fastapi-client`           | OIDC client ID                       |
| `KEYCLOAK_CLIENT_SECRET`    | `fastapi-client-secret-123`| OIDC client secret                   |
| `KEYCLOAK_ADMIN_PASSWORD`   | `admin123`                 | Keycloak admin user password         |

### Relevant Files

| File                                      | Purpose                                  |
|-------------------------------------------|------------------------------------------|
| `docker-compose.yml`                      | Keycloak service definition              |
| `keycloak-config/tetrics-realm.json`      | Realm, client, user, and role definitions|
| `app/core/auth.py`                        | JWT validation and role dependencies    |
| `app/config/settings.py`                  | Keycloak connection settings            |
| `scripts/get_token.py`                    | Helper to get an access token           |

## How It Works

1. **Token Validation:** `app/core/auth.py` fetches the JWKS (JSON Web Key Set) from Keycloak's certs endpoint and caches it for 1 hour. Each request's Bearer token is validated using the matching public key.

2. **User Extraction:** The validated JWT payload yields a `UserContext` with `sub`, `username`, `email`, and `roles` (from `realm_access.roles`).

3. **Role Checking:** The `requires_role("admin")` dependency factory checks the user's realm roles. Endpoints that need admin access use this dependency.

4. **Open Endpoints:** Only `/`, `/health`, and `/health/readiness` are unauthenticated.

## Adding Users

Via the Keycloak admin console at `http://localhost:8080`:

1. Log in with admin credentials
2. Select the `tetrics` realm
3. Go to **Users** → **Add user**
4. Fill in the form and click **Create**
5. Go to the **Credentials** tab to set a password
6. Go to **Role Mapping** → **Assign role** to assign `user` or `admin`

Or update `keycloak-config/tetrics-realm.json` and restart Keycloak to re-import.
