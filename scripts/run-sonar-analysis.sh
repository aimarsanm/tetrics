#!/bin/bash

# SonarQube Analysis Script for Tetrics
# Usage: ./scripts/run-sonar-analysis.sh [TOKEN]

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Tetrics SonarQube Analysis ===${NC}\n"

# Check if SonarQube is running
if ! docker ps | grep -q lks-sonarqube; then
    echo -e "${YELLOW}SonarQube container is not running. Starting it...${NC}"
    docker-compose up -d sonarqube
    echo -e "${YELLOW}Waiting for SonarQube to be ready (this may take 1-2 minutes)...${NC}"
    sleep 60
fi

# Check if token is provided
if [ -z "$1" ]; then
    echo -e "${YELLOW}Warning: No SonarQube token provided.${NC}"
    echo -e "${YELLOW}Usage: $0 <YOUR_SONAR_TOKEN>${NC}"
    echo -e "${YELLOW}You can generate a token at: http://localhost:9000/account/security${NC}\n"
    echo -e "${YELLOW}Attempting analysis without authentication (may fail)...${NC}\n"
    SONAR_TOKEN=""
else
    SONAR_TOKEN="$1"
    echo -e "${GREEN}Using provided token for authentication${NC}\n"
fi

# Run the analysis using Docker
echo -e "${GREEN}Running SonarQube analysis...${NC}\n"

if [ -z "$SONAR_TOKEN" ]; then
    docker run --rm \
      --network lks-network \
      -e SONAR_HOST_URL="http://sonarqube:9000" \
      -v "$(pwd):/usr/src" \
      sonarsource/sonar-scanner-cli
else
    docker run --rm \
      --network lks-network \
      -e SONAR_HOST_URL="http://sonarqube:9000" \
      -e SONAR_TOKEN="$SONAR_TOKEN" \
      -v "$(pwd):/usr/src" \
      sonarsource/sonar-scanner-cli
fi

echo -e "\n${GREEN}=== Analysis Complete ===${NC}"
echo -e "${GREEN}View results at: http://localhost:9000/dashboard?id=tetrics${NC}"
