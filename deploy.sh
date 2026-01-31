#!/bin/bash

set -e

echo "🚀 Deploying A4S with Personal Assistant Agent"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cd "$SCRIPT_DIR"

# Step 1: Build the personal-assistant agent image
echo -e "${BLUE}📦 Building personal-assistant agent image...${NC}"
docker build \
  -t a4s-personal-assistant:latest \
  -f agents/personal-assistant/Dockerfile \
  .

echo -e "${GREEN}✅ Personal assistant agent image built successfully${NC}"

# Step 2: Start services using docker compose
echo -e "${BLUE}🐳 Starting A4S services with docker compose...${NC}"
docker compose -f compose.dev.yml up -d

echo -e "${GREEN}✅ A4S services are now running${NC}"
echo ""
echo "Services:"
echo "  - Gateway: http://localhost:8080"
echo "  - API: http://localhost:8000"
echo "  - Qdrant: http://localhost:6333"
echo "  - FalkorDB: http://localhost:6379"
echo ""
echo "To view logs: docker compose -f compose.dev.yml logs -f"
echo "To stop: docker compose -f compose.dev.yml down"
