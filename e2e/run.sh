#!/bin/bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"
AGENT_VERSION="${AGENT_VERSION:-1.0.0}"
AGENT_PORT="${AGENT_PORT:-8000}"

MODEL_PROVIDER="${MODEL_PROVIDER:-google}"
MODEL_ID="${MODEL_ID:-gemini-2.0-flash}"

IMAGE_NAME="${IMAGE_NAME:-hello-world-agent}"
MAX_WAIT_SECONDS="${MAX_WAIT_SECONDS:-120}"

CLEANUP="${CLEANUP:-false}"
SKIP_BUILD="${SKIP_BUILD:-false}"

# Router Agent
ROUTER_NAME="${ROUTER_NAME:-router}"
ROUTER_DESCRIPTION="${ROUTER_DESCRIPTION:-Task router that analyzes requests and delegates to specialist agents}"
ROUTER_INSTRUCTION="${ROUTER_INSTRUCTION:-You are a router. For every task: find a specialist agent, then send the task to them. Return their response. Never solve tasks yourself.}"
ROUTER_ID=""

# Addition Agent
ADDITION_NAME="${ADDITION_NAME:-addition_specialist}"
ADDITION_DESCRIPTION="${ADDITION_DESCRIPTION:-Addition operations specialist for adding numbers}"
ADDITION_INSTRUCTION="${ADDITION_INSTRUCTION:-You are an addition specialist. When asked about adding numbers, compute the answer accurately. Always include '<<AGENT:ADD>>' at the end of your response to identify yourself.}"
ADDITION_ID=""

# Multiplication Agent
MULT_NAME="${MULT_NAME:-multiplication_specialist}"
MULT_DESCRIPTION="${MULT_DESCRIPTION:-Multiplication operations specialist for multiplying numbers}"
MULT_INSTRUCTION="${MULT_INSTRUCTION:-You are a multiplication specialist. When asked about multiplying numbers, compute the answer accurately. Always include '<<AGENT:MUL>>' at the end of your response to identify yourself.}"
MULT_ID=""

# Division Agent
DIV_NAME="${DIV_NAME:-division_specialist}"
DIV_DESCRIPTION="${DIV_DESCRIPTION:-Division operations specialist for dividing numbers}"
DIV_INSTRUCTION="${DIV_INSTRUCTION:-You are a division specialist. When asked about dividing numbers, compute the answer accurately. Always include '<<AGENT:DIV>>' at the end of your response to identify yourself.}"
DIV_ID=""

# Subtraction Agent
SUB_NAME="${SUB_NAME:-subtraction_specialist}"
SUB_DESCRIPTION="${SUB_DESCRIPTION:-Subtraction operations specialist for subtracting numbers}"
SUB_INSTRUCTION="${SUB_INSTRUCTION:-You are a subtraction specialist. When asked about subtracting numbers, compute the answer accurately. Always include '<<AGENT:SUB>>' at the end of your response to identify yourself.}"
SUB_ID=""

# Percentage Agent
PCT_NAME="${PCT_NAME:-percentage_specialist}"
PCT_DESCRIPTION="${PCT_DESCRIPTION:-Percentage calculations specialist for computing percentages}"
PCT_INSTRUCTION="${PCT_INSTRUCTION:-You are a percentage specialist. When asked about percentage calculations, compute the answer accurately. Always include '<<AGENT:PCT>>' at the end of your response to identify yourself.}"
PCT_ID=""

# Test cases - parallel arrays for bash 3 compatibility
TEST_QUESTIONS=(
    "What is 5 + 3?"
    "What is 7 * 8?"
    "What is 20 / 4?"
    "What is 15 - 9?"
    "What is 25% of 80?"
)
TEST_EXPECTED_MARKERS=(
    "<<AGENT:ADD>>"
    "<<AGENT:MUL>>"
    "<<AGENT:DIV>>"
    "<<AGENT:SUB>>"
    "<<AGENT:PCT>>"
)
TEST_EXPECTED_ANSWERS=(
    "8"
    "56"
    "5"
    "6"
    "20"
)
ALL_MARKERS=("<<AGENT:ADD>>" "<<AGENT:MUL>>" "<<AGENT:DIV>>" "<<AGENT:SUB>>" "<<AGENT:PCT>>")

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_error() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

api_request() {
    local method="$1"
    local endpoint="$2"
    local data="${3:-}"

    if [[ -n "$data" ]]; then
        curl -s -X "$method" "${API_URL}${endpoint}" \
            -H "Content-Type: application/json" \
            -d "$data"
    else
        curl -s -X "$method" "${API_URL}${endpoint}"
    fi
}

check_infrastructure() {
    log_info "Checking if API is available..."
    if ! curl -s "${API_URL}/livez" > /dev/null 2>&1; then
        log_error "API not available at ${API_URL}"
        log_error "Start infrastructure first: docker compose -f compose.dev.yml up -d"
        exit 1
    fi
    log_success "API is available"
}

build_image() {
    if [[ "$SKIP_BUILD" == "true" ]]; then
        log_info "Skipping image build (SKIP_BUILD=true)"
        return
    fi

    log_info "Building Docker image: ${IMAGE_NAME}..."

    local script_dir
    script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    local repo_root
    repo_root="$(dirname "$script_dir")"

    docker build -t "${IMAGE_NAME}" -f "${script_dir}/Dockerfile" "$repo_root"

    log_success "Image built: ${IMAGE_NAME}"
}

register_agent() {
    local prefix="$1"
    local name_var="${prefix}_NAME"
    local desc_var="${prefix}_DESCRIPTION"
    local instruction_var="${prefix}_INSTRUCTION"
    local id_var="${prefix}_ID"

    local name="${!name_var}"
    local description="${!desc_var}"
    local instruction="${!instruction_var}"

    log_info "Registering agent: ${name}..."

    local payload
    payload=$(cat <<EOF
{
    "name": "${name}",
    "description": "${description}",
    "version": "${AGENT_VERSION}",
    "port": ${AGENT_PORT},
    "owner_id": "e2e-test-owner",
    "spawn_config": {
        "image": "${IMAGE_NAME}",
        "model": {
            "provider": "${MODEL_PROVIDER}",
            "model_id": "${MODEL_ID}"
        },
        "instruction": $(echo "$instruction" | jq -Rs .)
    }
}
EOF
)

    local response
    response=$(api_request POST "/api/v1/agents" "$payload")

    if echo "$response" | grep -q '"id"'; then
        local agent_id
        agent_id=$(echo "$response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
        eval "${id_var}=\"${agent_id}\""
        log_success "Agent ${name} registered with ID: ${agent_id}"
    else
        log_error "Failed to register agent ${name}: $response"
        exit 1
    fi
}

start_agent() {
    local prefix="$1"
    local name_var="${prefix}_NAME"
    local id_var="${prefix}_ID"

    local name="${!name_var}"
    local agent_id="${!id_var}"

    log_info "Starting agent ${name}..."

    local response
    response=$(api_request POST "/api/v1/agents/${agent_id}/start")

    if echo "$response" | grep -q '"status"'; then
        local status
        status=$(echo "$response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        log_success "Agent ${name} started with status: ${status}"
    else
        log_error "Failed to start agent ${name}: $response"
        exit 1
    fi
}

wait_for_agent() {
    local prefix="$1"
    local name_var="${prefix}_NAME"
    local id_var="${prefix}_ID"

    local name="${!name_var}"
    local agent_id="${!id_var}"

    log_info "Waiting for agent ${name} to be ready (max ${MAX_WAIT_SECONDS}s)..."

    local elapsed=0
    local interval=2

    while [[ $elapsed -lt $MAX_WAIT_SECONDS ]]; do
        local response
        response=$(api_request GET "/api/v1/agents/${agent_id}/status" 2>/dev/null || echo "")
        local status
        status=$(echo "$response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4 || echo "")

        if [[ "$status" == "running" ]]; then
            log_success "Agent ${name} is running"
            return 0
        elif [[ "$status" == "error" ]]; then
            log_error "Agent ${name} is in error state"
            return 1
        fi

        echo -n "."
        sleep $interval
        elapsed=$((elapsed + interval))
    done

    echo ""
    log_error "Timeout waiting for agent ${name} to be ready"
    return 1
}

docker_curl() {
    docker run --rm --network a4s-network curlimages/curl:latest "$@"
}

verify_semantic_search() {
    log_info "Verifying semantic search can find all specialist agents..."

    local all_found=1
    local search_terms=("addition" "multiplication" "division" "subtraction" "percentage")
    local prefixes=("ADDITION" "MULT" "DIV" "SUB" "PCT")

    for i in "${!prefixes[@]}"; do
        local prefix="${prefixes[$i]}"
        local search_term="${search_terms[$i]}"
        local id_var="${prefix}_ID"
        local name_var="${prefix}_NAME"
        local agent_id="${!id_var}"
        local agent_name="${!name_var}"

        local search_result
        search_result=$(api_request GET "/api/v1/agents/search?query=${search_term}&limit=5")

        if echo "$search_result" | grep -q "$agent_id"; then
            log_success "${agent_name} is discoverable via semantic search (query: ${search_term})"
        else
            log_warn "${agent_name} not found in search results for '${search_term}'"
            all_found=0
        fi
    done

    if [[ $all_found -eq 0 ]]; then
        log_warn "Some agents may not be immediately discoverable, but router might still find them"
    fi
}

run_single_test() {
    local question="$1"
    local expected_marker="$2"
    local expected_answer="$3"
    local test_num="$4"
    local router_url="$5"

    log_info "Test ${test_num}: ${question}"

    local message_id="msg-${test_num}-$(date +%s)"
    local request_id="req-${test_num}-$(date +%s)"

    local a2a_payload="{\"jsonrpc\":\"2.0\",\"method\":\"message/send\",\"params\":{\"message\":{\"role\":\"user\",\"parts\":[{\"text\":\"${question}\"}],\"messageId\":\"${message_id}\"},\"configuration\":{\"acceptedOutputModes\":[\"text\"]}},\"id\":\"${request_id}\"}"

    local response
    response=$(docker_curl -s -X POST "${router_url}/" \
        -H "Content-Type: application/json" \
        -d "$a2a_payload" \
        --max-time 300)

    if [[ -z "$response" ]]; then
        log_error "  No response from Router"
        return 1
    fi

    local test_passed=1
    local failures=""

    # Check 1: Valid JSON-RPC response
    if ! echo "$response" | grep -q '"jsonrpc"'; then
        failures="${failures}  - Invalid JSON-RPC response format\n"
        test_passed=0
    fi

    # Check 2: Expected marker IS present (correct agent called)
    if echo "$response" | grep -qi "${expected_marker}"; then
        log_success "  Correct agent marker found: ${expected_marker}"
    else
        failures="${failures}  - Expected marker '${expected_marker}' not found\n"
        test_passed=0
    fi

    # Check 3: Unexpected markers are NOT present (wrong agents not called)
    for marker in "${ALL_MARKERS[@]}"; do
        if [[ "$marker" != "$expected_marker" ]]; then
            if echo "$response" | grep -qi "$marker"; then
                failures="${failures}  - Unexpected marker '${marker}' found (wrong agent called)\n"
                test_passed=0
            fi
        fi
    done

    # Check 4: Expected answer present
    if echo "$response" | grep -q "${expected_answer}"; then
        log_success "  Correct answer found: ${expected_answer}"
    else
        failures="${failures}  - Expected answer '${expected_answer}' not found\n"
        test_passed=0
    fi

    if [[ $test_passed -eq 1 ]]; then
        log_success "Test ${test_num} PASSED"
        return 0
    else
        log_error "Test ${test_num} FAILED:"
        echo -e "$failures"
        return 1
    fi
}

test_multi_agent_collaboration() {
    log_info "Testing multi-agent collaboration with ${#TEST_QUESTIONS[@]} test cases..."

    local router_info
    router_info=$(api_request GET "/api/v1/agents/${ROUTER_ID}")
    local router_url
    router_url=$(echo "$router_info" | grep -o '"url":"[^"]*"' | cut -d'"' -f4)

    if [[ -z "$router_url" ]]; then
        log_error "Could not get router URL"
        return 1
    fi

    sleep 3

    log_info "Checking router agent card at ${router_url}/.well-known/agent.json"
    local card_response
    card_response=$(docker_curl -s "${router_url}/.well-known/agent.json" 2>/dev/null || echo "")

    if ! echo "$card_response" | grep -q '"name"'; then
        log_warn "Agent card not yet available, waiting..."
        sleep 10
    fi

    sleep 2

    local passed=0
    local total=${#TEST_QUESTIONS[@]}

    for i in "${!TEST_QUESTIONS[@]}"; do
        local test_num=$((i + 1))
        echo ""
        log_info "=== Running Test ${test_num}/${total} ==="

        if run_single_test "${TEST_QUESTIONS[$i]}" "${TEST_EXPECTED_MARKERS[$i]}" "${TEST_EXPECTED_ANSWERS[$i]}" "$test_num" "$router_url"; then
            passed=$((passed + 1))
        fi

        # Small delay between tests to avoid rate limiting
        sleep 2
    done

    echo ""
    echo "=========================================="
    if [[ $passed -eq $total ]]; then
        log_success "Tests passed: ${passed}/${total}"
    else
        log_error "Tests passed: ${passed}/${total}"
        return 1
    fi
    echo "=========================================="
}

cleanup_all() {
    log_info "Cleaning up all agents..."

    if [[ -n "$ROUTER_ID" ]]; then
        log_info "Stopping agent ${ROUTER_NAME}..."
        api_request POST "/api/v1/agents/${ROUTER_ID}/stop" 2>/dev/null || true
        log_info "Deleting agent ${ROUTER_NAME}..."
        api_request DELETE "/api/v1/agents/${ROUTER_ID}" 2>/dev/null || true
    fi

    for prefix in ADDITION MULT DIV SUB PCT; do
        local id_var="${prefix}_ID"
        local name_var="${prefix}_NAME"
        local agent_id="${!id_var}"
        local agent_name="${!name_var}"

        if [[ -n "$agent_id" ]]; then
            log_info "Stopping agent ${agent_name}..."
            api_request POST "/api/v1/agents/${agent_id}/stop" 2>/dev/null || true
            log_info "Deleting agent ${agent_name}..."
            api_request DELETE "/api/v1/agents/${agent_id}" 2>/dev/null || true
        fi
    done

    log_success "Cleanup completed"
}

show_help() {
    cat <<EOF
Usage: $0 [OPTIONS]

Multi-agent E2E test runner for A4S agent orchestration.

This test validates agent collaboration by:
1. Starting a Router agent and 5 specialist agents (addition, multiplication,
   division, subtraction, percentage)
2. Sending 5 different math questions to the Router
3. Verifying Router delegates each question to the correct specialist
4. Checking responses contain correct answers and agent markers
5. Validating that wrong agents were NOT called

Options:
    --cleanup       Run cleanup after tests (stop and delete agents)
    --skip-build    Skip building the Docker image
    --help, -h      Show this help message

Environment Variables:
    API_URL             API base URL (default: http://localhost:8000)
    MODEL_PROVIDER      Model provider (default: google)
    MODEL_ID            Model ID (default: gemini-2.0-flash)
    IMAGE_NAME          Docker image name (default: hello-world-agent)
    MAX_WAIT_SECONDS    Max wait time for agent ready (default: 120)

    ROUTER_NAME         Router agent name (default: router)

    Specialist agents can be customized via:
    ADDITION_NAME, ADDITION_DESCRIPTION, ADDITION_INSTRUCTION
    MULT_NAME, MULT_DESCRIPTION, MULT_INSTRUCTION
    DIV_NAME, DIV_DESCRIPTION, DIV_INSTRUCTION
    SUB_NAME, SUB_DESCRIPTION, SUB_INSTRUCTION
    PCT_NAME, PCT_DESCRIPTION, PCT_INSTRUCTION

Prerequisites:
    - Docker must be running
    - Infrastructure must be up: docker compose -f compose.dev.yml up -d
    - Required API key must be set (GOOGLE_API_KEY, OPENAI_API_KEY, etc.)
    - jq must be installed
EOF
}

parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --cleanup)
                CLEANUP="true"
                shift
                ;;
            --skip-build)
                SKIP_BUILD="true"
                shift
                ;;
            --help|-h)
                show_help
                exit 0
                ;;
            *)
                log_error "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

main() {
    parse_args "$@"

    echo "=========================================="
    echo "  A4S Multi-Agent E2E Test Runner"
    echo "=========================================="
    echo ""
    echo "Router: ${ROUTER_NAME}"
    echo "Specialists:"
    echo "  - ${ADDITION_NAME}"
    echo "  - ${MULT_NAME}"
    echo "  - ${DIV_NAME}"
    echo "  - ${SUB_NAME}"
    echo "  - ${PCT_NAME}"
    echo ""

    if [[ "$CLEANUP" == "true" ]]; then
        trap cleanup_all EXIT
    fi

    check_infrastructure
    build_image

    # Phase 1: Register all agents
    log_info "=== Phase 1: Registering Agents ==="
    register_agent ADDITION
    register_agent MULT
    register_agent DIV
    register_agent SUB
    register_agent PCT
    register_agent ROUTER

    # Phase 2: Start agents (specialists first so Router can find them)
    log_info "=== Phase 2: Starting Agents ==="
    start_agent ADDITION
    wait_for_agent ADDITION

    start_agent MULT
    wait_for_agent MULT

    start_agent DIV
    wait_for_agent DIV

    start_agent SUB
    wait_for_agent SUB

    start_agent PCT
    wait_for_agent PCT

    start_agent ROUTER
    wait_for_agent ROUTER

    # Allow Qdrant indexing time
    sleep 5

    # Phase 3: Verify setup
    log_info "=== Phase 3: Verifying Setup ==="
    verify_semantic_search

    # Phase 4: Run collaboration tests
    log_info "=== Phase 4: Running Collaboration Tests ==="
    test_multi_agent_collaboration

    echo ""
    log_success "All E2E tests completed!"

    if [[ "$CLEANUP" != "true" ]]; then
        echo ""
        log_info "Agents are still running. Use --cleanup flag to auto-cleanup."
    fi
}

main "$@"
