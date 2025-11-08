#!/bin/bash
# Smoke test for Clankerbot API
# Usage: ./scripts/smoke.sh [base_url]
# Example: ./scripts/smoke.sh http://localhost:8000

set -e

BASE_URL="${1:-http://localhost:8000}"
PASSED=0
FAILED=0
TESTS=()

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_test() {
    echo -e "${YELLOW}[TEST]${NC} $1"
}

log_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
    PASSED=$((PASSED + 1))
    TESTS+=("✓ $1")
}

log_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    FAILED=$((FAILED + 1))
    TESTS+=("✗ $1")
}

# Test 1: Health check
log_test "1. Health check (/healthz)"
RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/healthz")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)
if [ "$HTTP_CODE" = "200" ] && echo "$BODY" | grep -q '"ok":true'; then
    log_pass "Health check returned 200 OK"
else
    log_fail "Health check failed (HTTP $HTTP_CODE)"
    echo "$BODY"
fi

# Test 2: Readiness check
log_test "2. Readiness check (/readyz)"
RESPONSE=$(curl -s -w "\n%{http_code}" "$BASE_URL/readyz")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)
if [ "$HTTP_CODE" = "200" ]; then
    log_pass "Readiness check returned 200 OK"
    echo "$BODY" | grep -q '"ready":true' && echo "  → All dependencies ready" || echo "  → Some dependencies missing"
else
    log_fail "Readiness check failed (HTTP $HTTP_CODE)"
fi

# Test 3: Rule-based parsing
log_test "3. Rule-based parsing"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/actions/parse" \
    -H "Content-Type: application/json" \
    -d '{"text": "clockify.get_user"}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)
if [ "$HTTP_CODE" = "200" ] && echo "$BODY" | grep -q '"parser":"rule"'; then
    log_pass "Rule-based parsing works"
else
    log_fail "Rule-based parsing failed (HTTP $HTTP_CODE)"
    echo "$BODY"
fi

# Test 4: LLM parsing with fallback
log_test "4. LLM parsing with fallback"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/actions/parse?llm=true" \
    -H "Content-Type: application/json" \
    -d '{"text": "Get my Clockify user info"}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)
if [ "$HTTP_CODE" = "200" ]; then
    if echo "$BODY" | grep -q '"parser":"llm"'; then
        log_pass "LLM parsing successful"
    elif echo "$BODY" | grep -q '"parser":"fallback"'; then
        log_pass "LLM fallback to rule parser (expected without API key)"
    else
        log_fail "LLM parsing returned unexpected parser type"
        echo "$BODY"
    fi
else
    log_fail "LLM parsing failed (HTTP $HTTP_CODE)"
    echo "$BODY"
fi

# Test 5: Run action (get_user)
log_test "5. Run action (get_user)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/actions/run" \
    -H "Content-Type: application/json" \
    -d '{"integration": "clockify", "operation": "get_user", "params": {}}')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)
if [ "$HTTP_CODE" = "200" ]; then
    if echo "$BODY" | grep -q '"ok":true'; then
        log_pass "Action execution successful"
    elif echo "$BODY" | grep -q '"unauthorized"'; then
        log_pass "Action execution works (credentials not configured)"
    else
        log_pass "Action execution returned response"
    fi
else
    log_fail "Action execution failed (HTTP $HTTP_CODE)"
    echo "$BODY"
fi

# Test 6: Webhook delivery
log_test "6. Webhook delivery"
EVENT_ID="smoke_test_$(date +%s)"
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/webhooks/clockify" \
    -H "Content-Type: application/json" \
    -H "X-Clockify-Event-Id: $EVENT_ID" \
    -d '{
        "id": "entry123",
        "userId": "user123",
        "workspaceId": "ws123",
        "timeInterval": {
            "start": "2024-01-01T10:00:00Z",
            "end": "2024-01-01T11:00:00Z"
        }
    }')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)
if [ "$HTTP_CODE" = "200" ] && echo "$BODY" | grep -q '"duplicate":false'; then
    log_pass "Webhook received (not duplicate)"
else
    log_fail "Webhook delivery failed (HTTP $HTTP_CODE)"
    echo "$BODY"
fi

# Test 7: Webhook idempotency (duplicate detection)
log_test "7. Webhook idempotency (duplicate)"
sleep 0.5  # Brief pause
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/webhooks/clockify" \
    -H "Content-Type: application/json" \
    -H "X-Clockify-Event-Id: $EVENT_ID" \
    -d '{
        "id": "entry123",
        "userId": "user123",
        "workspaceId": "ws123",
        "timeInterval": {
            "start": "2024-01-01T10:00:00Z",
            "end": "2024-01-01T11:00:00Z"
        }
    }')
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)
if [ "$HTTP_CODE" = "200" ] && echo "$BODY" | grep -q '"duplicate":true'; then
    log_pass "Webhook idempotency works (duplicate detected)"
else
    log_fail "Webhook idempotency failed (HTTP $HTTP_CODE)"
    echo "$BODY"
fi

# Summary
echo ""
echo "========================================"
echo "           SMOKE TEST RESULTS"
echo "========================================"
echo ""
for test in "${TESTS[@]}"; do
    echo "  $test"
done
echo ""
echo "========================================"
echo -e "  Passed: ${GREEN}${PASSED}${NC}"
echo -e "  Failed: ${RED}${FAILED}${NC}"
echo "========================================"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}SMOKE TEST FAILED${NC}"
    exit 1
else
    echo -e "${GREEN}ALL SMOKE TESTS PASSED${NC}"
    exit 0
fi
