#!/bin/bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"
AGENT_NAME="${AGENT_NAME:-test_agent}"
AGENT_ID=""  # Will be set by server during registration
AGENT_DESCRIPTION="${AGENT_DESCRIPTION:-E2E test agent}"
AGENT_VERSION="${AGENT_VERSION:-1.0.0}"
AGENT_PORT="${AGENT_PORT:-8000}"

MODEL_PROVIDER="${MODEL_PROVIDER:-google}"
MODEL_ID="${MODEL_ID:-gemini-3-flash-preview}"
AGENT_INSTRUCTION="${AGENT_INSTRUCTION:-You are a helpful test agent.}"

IMAGE_NAME="${IMAGE_NAME:-hello-world-agent}"
TEST_MESSAGE="${TEST_MESSAGE:-Hello}"
MAX_WAIT_SECONDS="${MAX_WAIT_SECONDS:-60}"

CLEANUP="${CLEANUP:-false}"
SKIP_BUILD="${SKIP_BUILD:-false}"

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
    log_info "Registering agent: ${AGENT_NAME}..."

    local container_name="a4s-agent-${AGENT_NAME}"
    local agent_url="http://${container_name}:${AGENT_PORT}"

    local payload
    payload=$(cat <<EOF
{
    "name": "${AGENT_NAME}",
    "description": "${AGENT_DESCRIPTION}",
    "version": "${AGENT_VERSION}",
    "url": "${agent_url}",
    "port": ${AGENT_PORT}
}
EOF
)

    local response
    response=$(api_request POST "/api/v1/agents" "$payload")

    if echo "$response" | grep -q '"id"'; then
        AGENT_ID=$(echo "$response" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
        log_success "Agent registered with ID: ${AGENT_ID}"
    else
        log_error "Failed to register agent: $response"
        exit 1
    fi
}

start_agent() {
    log_info "Starting agent container..."

    local payload
    payload=$(cat <<EOF
{
    "image": "${IMAGE_NAME}",
    "model_provider": "${MODEL_PROVIDER}",
    "model_id": "${MODEL_ID}",
    "instruction": "${AGENT_INSTRUCTION}"
}
EOF
)

    local response
    response=$(api_request POST "/api/v1/agents/${AGENT_ID}/start" "$payload")

    if echo "$response" | grep -q '"status"'; then
        local status
        status=$(echo "$response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
        log_success "Agent started with status: $status"
    else
        log_error "Failed to start agent: $response"
        exit 1
    fi
}

wait_for_agent() {
    log_info "Waiting for agent to be ready (max ${MAX_WAIT_SECONDS}s)..."

    local elapsed=0
    local interval=2

    while [[ $elapsed -lt $MAX_WAIT_SECONDS ]]; do
        local response
        response=$(api_request GET "/api/v1/agents/${AGENT_ID}/status" 2>/dev/null || echo "")
        local status
        status=$(echo "$response" | grep -o '"status":"[^"]*"' | cut -d'"' -f4 || echo "")

        if [[ "$status" == "running" ]]; then
            log_success "Agent is running"
            return 0
        elif [[ "$status" == "error" ]]; then
            log_error "Agent is in error state"
            return 1
        fi

        echo -n "."
        sleep $interval
        elapsed=$((elapsed + interval))
    done

    echo ""
    log_error "Timeout waiting for agent to be ready"
    return 1
}

docker_curl() {
    docker run --rm --network a4s-network curlimages/curl:latest "$@"
}

test_agent() {
    log_info "Testing agent with A2A message..."

    local agent_info
    agent_info=$(api_request GET "/api/v1/agents/${AGENT_ID}")
    local agent_url
    agent_url=$(echo "$agent_info" | grep -o '"url":"[^"]*"' | cut -d'"' -f4)

    if [[ -z "$agent_url" ]]; then
        log_error "Could not get agent URL"
        return 1
    fi

    sleep 3

    log_info "Checking agent card at ${agent_url}/.well-known/agent.json"
    local card_response
    card_response=$(docker_curl -s "${agent_url}/.well-known/agent.json" 2>/dev/null || echo "")

    if ! echo "$card_response" | grep -q '"name"'; then
        log_warn "Agent card not yet available, waiting..."
        sleep 10
        card_response=$(docker_curl -s "${agent_url}/.well-known/agent.json" 2>/dev/null || echo "")
    fi

    sleep 2
    log_info "Sending A2A message to ${agent_url}/"

    local message_id="msg-$(date +%s)"
    local request_id="req-$(date +%s)"

    local a2a_payload="{\"jsonrpc\":\"2.0\",\"method\":\"message/send\",\"params\":{\"message\":{\"role\":\"user\",\"parts\":[{\"text\":\"${TEST_MESSAGE}\"}],\"messageId\":\"${message_id}\"},\"configuration\":{\"acceptedOutputModes\":[\"text\"]}},\"id\":\"${request_id}\"}"

    local response
    response=$(docker_curl -s -X POST "${agent_url}/" \
        -H "Content-Type: application/json" \
        -d "$a2a_payload" \
        --max-time 60)

    if [[ -z "$response" ]]; then
        log_error "No response from agent"
        return 1
    fi

    log_info "Response:"
    echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"

    if echo "$response" | grep -q '"jsonrpc"'; then
        log_success "A2A communication successful"
    else
        log_error "Invalid A2A response"
        return 1
    fi
}

cleanup() {
    log_info "Cleaning up..."

    log_info "Stopping agent..."
    api_request POST "/api/v1/agents/${AGENT_ID}/stop" 2>/dev/null || true

    log_info "Deleting agent from registry..."
    api_request DELETE "/api/v1/agents/${AGENT_ID}" 2>/dev/null || true

    log_success "Cleanup completed"
}

show_help() {
    cat <<EOF
Usage: $0 [OPTIONS]

E2E test runner for A4S agent orchestration.

Options:
    --cleanup       Run cleanup after tests (stop and delete agent)
    --skip-build    Skip building the Docker image
    --help, -h      Show this help message

Environment Variables:
    API_URL             API base URL (default: http://localhost:8000)
    AGENT_NAME          Agent name (default: test_agent)
    MODEL_PROVIDER      Model provider (default: google)
    MODEL_ID            Model ID (default: gemini-2.0-flash)
    IMAGE_NAME          Docker image name (default: hello-world-agent)
    MAX_WAIT_SECONDS    Max wait time for agent ready (default: 60)

Prerequisites:
    - Docker must be running
    - Infrastructure must be up: docker compose -f compose.dev.yml up -d
    - Required API key must be set (GOOGLE_API_KEY, OPENAI_API_KEY, etc.)
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
    echo "  A4S E2E Test Runner"
    echo "=========================================="
    echo ""

    if [[ "$CLEANUP" == "true" ]]; then
        trap cleanup EXIT
    fi

    check_infrastructure
    build_image
    register_agent
    start_agent
    wait_for_agent
    test_agent

    echo ""
    log_success "All E2E tests passed!"

    if [[ "$CLEANUP" != "true" ]]; then
        echo ""
        log_info "Agent is still running. To cleanup manually:"
        log_info "  curl -X POST ${API_URL}/api/v1/agents/${AGENT_ID}/stop"
        log_info "  curl -X DELETE ${API_URL}/api/v1/agents/${AGENT_ID}"
    fi
}

main "$@"
