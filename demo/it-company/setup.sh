#!/bin/bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"
IMAGE="${IMAGE:-a4s-personal-assistant:latest}"
MODEL_PROVIDER="${MODEL_PROVIDER:-openrouter}"
MODEL_ID="${MODEL_ID:-google/gemini-3-flash-preview}"
MEMORY_DELAY="${MEMORY_DELAY:-2}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="${SCRIPT_DIR}/data"
AGENTS_FILE="${DATA_DIR}/agents.json"
MEMORY_DIR="${DATA_DIR}/memory"

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_ok()   { echo -e "${GREEN}[OK]${NC} $*"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
log_err()  { echo -e "${RED}[ERROR]${NC} $*" >&2; }

# Temp file for name -> agent_id mapping
ID_MAP=$(mktemp)
echo '{}' > "$ID_MAP"
trap 'rm -f "$ID_MAP"' EXIT

register_agents() {
    log_info "=== Registering Agents ==="

    local agent_count
    agent_count=$(jq '.agents | length' "$AGENTS_FILE")

    for i in $(seq 0 $((agent_count - 1))); do
        local agent_json name display_name
        agent_json=$(jq -c ".agents[$i]" "$AGENTS_FILE")
        name=$(echo "$agent_json" | jq -r '.name')
        display_name=$(echo "$agent_json" | jq -r '.display_name')

        local payload
        payload=$(echo "$agent_json" | jq \
            --arg img "$IMAGE" \
            --arg provider "$MODEL_PROVIDER" \
            --arg model_id "$MODEL_ID" \
            '{
                name: .name,
                description: .description,
                mode: "serverless",
                spawn_config: {
                    image: $img,
                    model: { provider: $provider, model_id: $model_id },
                    instruction: .spawn_config.instruction,
                    tools: .spawn_config.tools
                }
            }')

        local response http_code body
        response=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}/api/v1/agents" \
            -H "Content-Type: application/json" \
            -d "$payload")
        http_code=$(echo "$response" | tail -1)
        body=$(echo "$response" | sed '$d')

        if [[ "$http_code" != "201" ]]; then
            log_err "Failed to register ${name} (HTTP ${http_code}): ${body}"
            exit 1
        fi

        local agent_id
        agent_id=$(echo "$body" | jq -r '.id')

        local tmp
        tmp=$(jq --arg name "$name" --arg id "$agent_id" '. + {($name): $id}' "$ID_MAP")
        echo "$tmp" > "$ID_MAP"

        log_ok "${display_name} (${name}) -> ${agent_id}"
    done

    echo ""
    log_ok "Registered ${agent_count} agents"
}

seed_memories() {
    log_info "=== Seeding Memories ==="

    local total_success=0
    local total_failed=0
    local agent_count
    agent_count=$(jq '.agents | length' "$AGENTS_FILE")

    for i in $(seq 0 $((agent_count - 1))); do
        local name
        name=$(jq -r ".agents[$i].name" "$AGENTS_FILE")

        local agent_id
        agent_id=$(jq -r --arg name "$name" '.[$name]' "$ID_MAP")
        if [[ -z "$agent_id" || "$agent_id" == "null" ]]; then
            log_warn "No registered ID for ${name}, skipping"
            continue
        fi

        local memory_file="${MEMORY_DIR}/$(echo "$name" | tr '-' '_').json"
        if [[ ! -f "$memory_file" ]]; then
            log_warn "No memory file for ${name}"
            continue
        fi

        local memory_count
        memory_count=$(jq '.memories | length' "$memory_file")
        log_info "${name}: seeding ${memory_count} memories..."

        local success=0
        for j in $(seq 0 $((memory_count - 1))); do
            local payload
            payload=$(jq -c --arg agent_id "$agent_id" \
                ".memories[$j] | {
                    messages: .episode_body,
                    agent_id: \$agent_id,
                    metadata: { name: .name, knowledge_type: .knowledge_type }
                }" "$memory_file")

            local response http_code
            response=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}/api/v1/memories" \
                -H "Content-Type: application/json" \
                -H "X-Requester-Id: ${agent_id}" \
                -d "$payload")
            http_code=$(echo "$response" | tail -1)

            if [[ "$http_code" == "201" ]]; then
                success=$((success + 1))
            else
                local body mem_name
                body=$(echo "$response" | sed '$d')
                mem_name=$(jq -r ".memories[$j].name" "$memory_file")
                log_err "  Failed '${mem_name}': ${body}"
                total_failed=$((total_failed + 1))
            fi

            sleep "$MEMORY_DELAY"
        done

        total_success=$((total_success + success))
        log_ok "${name}: ${success}/${memory_count}"
    done

    echo ""
    log_info "Memory seeding complete: ${total_success} succeeded, ${total_failed} failed"
    echo ""
    log_info "Memories are processed asynchronously."
    log_info "Wait a few minutes before testing to allow processing to complete."
}

# Resolve a list of agent names to their real IDs from the ID_MAP
resolve_ids() {
    local names=("$@")
    local ids=()
    for name in "${names[@]}"; do
        local id
        id=$(jq -r --arg name "$name" '.[$name]' "$ID_MAP")
        if [[ -z "$id" || "$id" == "null" ]]; then
            log_err "Cannot resolve agent: ${name}"
            exit 1
        fi
        ids+=("$id")
    done
    printf '%s\n' "${ids[@]}" | jq -R . | jq -s .
}

create_channel() {
    local name="$1"
    local description="$2"
    shift 2
    local agent_names=("$@")

    local ids_json
    ids_json=$(resolve_ids "${agent_names[@]}")

    local payload
    payload=$(jq -n \
        --arg name "$name" \
        --arg desc "$description" \
        --argjson ids "$ids_json" \
        '{name: $name, description: $desc, agent_ids: $ids, owner_id: "demo"}')

    local response http_code body
    response=$(curl -s -w "\n%{http_code}" -X POST "${API_URL}/api/v1/channels" \
        -H "Content-Type: application/json" \
        -d "$payload")
    http_code=$(echo "$response" | tail -1)
    body=$(echo "$response" | sed '$d')

    if [[ "$http_code" != "201" ]]; then
        log_err "Failed to create channel ${name} (HTTP ${http_code}): ${body}"
        exit 1
    fi

    local channel_id
    channel_id=$(echo "$body" | jq -r '.id')
    log_ok "${name} -> ${channel_id} (${#agent_names[@]} agents)"
}

create_channels() {
    log_info "=== Creating Channels ==="

    create_channel "engineering" \
        "Backend, frontend, DevOps, and QA engineers" \
        alice-chen bob-martinez carol-kim david-patel \
        emily-wang frank-johnson grace-liu \
        henry-brooks isabel-gomez james-park \
        kate-thompson luis-rodriguez

    create_channel "product" \
        "Product managers and designers" \
        maya-singh nathan-lee olivia-taylor paul-anderson quinn-roberts

    create_channel "marketing" \
        "Marketing strategy and content" \
        rachel-green sarah-miller tom-wilson

    create_channel "leadership" \
        "Managers and leads across departments" \
        alice-chen henry-brooks kate-thompson olivia-taylor rachel-green maya-singh

    create_channel "all-hands" \
        "All agents for cross-functional collaboration" \
        alice-chen bob-martinez carol-kim david-patel \
        emily-wang frank-johnson grace-liu \
        henry-brooks isabel-gomez james-park \
        kate-thompson luis-rodriguez \
        maya-singh nathan-lee \
        olivia-taylor paul-anderson quinn-roberts \
        rachel-green sarah-miller tom-wilson

    echo ""
    log_ok "Created 5 channels"
}

main() {
    echo "=========================================="
    echo "  TechFlow Solutions - IT Company Demo"
    echo "=========================================="
    echo ""

    if ! curl -sf "${API_URL}/livez" > /dev/null 2>&1; then
        log_err "API not available at ${API_URL}"
        log_err "Start infrastructure first: docker compose -f compose.dev.yml up -d"
        exit 1
    fi
    log_ok "API is available"
    echo ""

    register_agents
    echo ""

    seed_memories
    echo ""

    create_channels
    echo ""

    echo "=========================================="
    log_ok "Setup complete!"
    echo ""
    echo "Registered agents (serverless):"
    jq -r 'to_entries[] | "  \(.key)\t\(.value)"' "$ID_MAP" | sort
    echo ""
    echo "Channels:"
    echo "  engineering  -> backend, frontend, devops, QA"
    echo "  product      -> product managers, designers"
    echo "  marketing    -> marketing team"
    echo "  leadership   -> managers and leads"
    echo "  all-hands    -> all 20 agents"
    echo "=========================================="
}

main "$@"
