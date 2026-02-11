# SonarQube Integration

This project includes SonarQube Community Edition for continuous code quality and security analysis.

## Quick Start

### 1. Start SonarQube
```bash
docker compose up -d sonarqube
```

Wait for startup (~1-2 minutes). Check logs:
```bash
docker compose logs -f sonarqube
# Wait for: "SonarQube is operational"
```

### 2. Initial Configuration

1. Open http://localhost:9000
2. Login with default credentials: `admin` / `admin`
3. Change password when prompted
4. Create project:
   - Click "Create Project" → "Manually"
   - Project key: `tetrics`
   - Display name: `Tetrics`
   - Click "Set Up" → "Locally"
5. Generate authentication token:
   - Name it `tetrics-analysis`
   - **Save this token securely!**

### 3. Connect VSCode SonarLint

1. Install the **SonarLint** extension in VSCode
2. Open Command Palette (Ctrl+Shift+P / Cmd+Shift+P)
3. Run: `SonarLint: Add SonarQube Connection`
   - Connection ID: `tetrics-local`
   - Server URL: `http://localhost:9000`
   - Token: [paste your token from step 2]
4. Run: `SonarLint: Update All Project Bindings`
   - Select connection `tetrics-local`
   - Select project `tetrics`

### 4. Run Analysis

Using the helper script:
```bash
./scripts/run-sonar-analysis.sh YOUR_TOKEN_HERE
```

Or manually with Docker:
```bash
docker run --rm \
  --network lks-network \
  -e SONAR_HOST_URL="http://sonarqube:9000" \
  -e SONAR_TOKEN="YOUR_TOKEN_HERE" \
  -v "$(pwd):/usr/src" \
  sonarsource/sonar-scanner-cli
```

View results at: http://localhost:9000/dashboard?id=tetrics

## Architecture

- **SonarQube Server**: http://localhost:9000
- **Database**: Separate PostgreSQL database (`sonarqube`) in shared postgres container
- **Network**: Connected to `lks-network`
- **Analyzed Code**: `app/` directory (Python files)
- **Exclusions**: migrations, `__pycache__`, node_modules, alembic, front-end

## Configuration Files

- **sonar-project.properties**: Project configuration and analysis scope
- **scripts/init.sql**: Database initialization
- **.vscode/settings.sonarqube.json**: Template for VSCode settings

## Benefits

### In VSCode (SonarLint)
- Real-time analysis as you type
- Inline issue highlighting
- Quick fixes for common problems
- Same rules as your CI/CD pipeline

### In SonarQube Dashboard
- Code quality metrics and trends
- Security vulnerabilities detection
- Code smells and technical debt tracking
- Duplicate code detection

## Customization

### Modify Analysis Scope
Edit `sonar-project.properties`:
```properties
# Add more source directories
sonar.sources=app,scripts

# Exclude specific patterns
sonar.exclusions=**/test_*.py,**/conftest.py
```

### Adjust Quality Rules
1. Go to SonarQube UI → "Rules" → "Python"
2. Activate/deactivate specific rules
3. Create custom quality profiles

### Set Quality Gates
1. Go to "Quality Gates" in SonarQube UI
2. Create custom gates with your thresholds
3. Apply to your project

## Troubleshooting

### Linux: SonarQube won't start
```bash
sudo sysctl -w vm.max_map_count=262144
# Make permanent:
echo 'vm.max_map_count=262144' | sudo tee -a /etc/sysctl.conf
```

### VSCode can't connect
- Verify SonarQube is running: `docker compose ps sonarqube`
- Test in browser: http://localhost:9000
- Check your token is correct
- Restart VSCode after configuration

### Database issues
The `sonarqube` database is created automatically via `scripts/init.sql` on first postgres startup. If you had postgres running before adding SonarQube, recreate the volume:
```bash
docker compose down
docker volume rm tetrics_postgres_data
docker compose up -d postgres sonarqube
```

### Reset SonarQube completely
```bash
docker compose down
docker volume rm tetrics_sonarqube_data tetrics_sonarqube_extensions tetrics_sonarqube_logs
docker compose up -d sonarqube
```

## Useful Commands

```bash
# View logs
docker compose logs -f sonarqube

# Restart SonarQube
docker compose restart sonarqube

# Stop/start
docker compose stop sonarqube
docker compose start sonarqube

# Check status
docker compose ps sonarqube
```

## Resources

- **SonarQube Docs**: https://docs.sonarqube.org/latest/
- **SonarLint Docs**: https://www.sonarsource.com/products/sonarlint/
- **Python Rules**: https://rules.sonarsource.com/python/

---

**Note**: Keep your authentication token secure. Don't commit it to version control. Each team member should generate their own token.
