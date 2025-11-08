#!/bin/bash
#
# Load Testing Script for Clankerbot
#
# This script runs k6 load tests against the Clankerbot API.
#
# Usage:
#   ./scripts/load.sh [BASE_URL]
#
# Arguments:
#   BASE_URL - Optional base URL for the API (default: http://localhost:8000)
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="${1:-http://localhost:8000}"
K6_SCRIPT="tools/k6/parse_and_run.js"

echo -e "${GREEN}Clankerbot Load Testing${NC}"
echo "========================================"
echo ""

# Check if k6 is installed
if ! command -v k6 &> /dev/null; then
    echo -e "${RED}Error: k6 is not installed${NC}"
    echo ""
    echo "To install k6, visit: https://k6.io/docs/get-started/installation/"
    echo ""
    echo "Quick install options:"
    echo "  macOS:   brew install k6"
    echo "  Ubuntu:  sudo gpg -k && sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69 && echo 'deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main' | sudo tee /etc/apt/sources.list.d/k6.list && sudo apt-get update && sudo apt-get install k6"
    echo "  Docker:  docker pull grafana/k6"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓${NC} k6 is installed ($(k6 version | head -n 1))"
echo ""

# Check if the k6 script exists
if [ ! -f "$K6_SCRIPT" ]; then
    echo -e "${RED}Error: k6 script not found at $K6_SCRIPT${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} k6 script found: $K6_SCRIPT"
echo ""

# Check if the server is running
echo "Checking if server is running at $BASE_URL..."
if ! curl -s -f -o /dev/null "$BASE_URL/healthz"; then
    echo -e "${YELLOW}Warning: Server does not appear to be running at $BASE_URL${NC}"
    echo ""
    echo "To start the server, run:"
    echo "  uvicorn app.main:app --reload"
    echo ""
    read -p "Continue anyway? [y/N] " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓${NC} Server is running"
    echo ""
fi

# Run k6 load test
echo "Starting load test..."
echo "Target: $BASE_URL"
echo ""
echo "Test configuration:"
echo "  - Ramp up to 10 RPS over 30 seconds"
echo "  - Maintain 10 RPS for 2 minutes"
echo "  - Ramp down over 30 seconds"
echo ""
echo "Press Ctrl+C to stop the test early"
echo ""

BASE_URL="$BASE_URL" k6 run "$K6_SCRIPT"

# Check if results file was created
if [ -f "load-test-results.json" ]; then
    echo ""
    echo -e "${GREEN}✓${NC} Load test complete! Results saved to load-test-results.json"
    echo ""

    # Print summary if jq is available
    if command -v jq &> /dev/null; then
        echo "Quick Summary:"
        echo "=============="
        jq -r '
            "Total Requests: \(.metrics.http_reqs.values.count)",
            "Request Rate: \(.metrics.http_reqs.values.rate | tonumber | . * 100 | round / 100) req/s",
            "Avg Duration: \(.metrics.http_req_duration.values.avg | tonumber | . * 100 | round / 100) ms",
            "P95 Duration: \(.metrics.http_req_duration.values["p(95)"] | tonumber | . * 100 | round / 100) ms",
            "Error Rate: \((.metrics.errors.values.rate * 100) | tonumber | . * 100 | round / 100)%"
        ' load-test-results.json
    fi
else
    echo -e "${YELLOW}Warning: Results file not found${NC}"
fi

echo ""
echo -e "${GREEN}Done!${NC}"
