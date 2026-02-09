#!/bin/bash
set -euo pipefail

API_URL="${API_URL:-http://localhost:8000}"
IMAGE="${IMAGE:-a4s-personal-assistant:latest}"
MODEL_PROVIDER="${MODEL_PROVIDER:-google}"
MODEL_ID="${MODEL_ID:-gemini-3-flash-preview}"

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $*"; }
log_ok() { echo -e "${GREEN}[OK]${NC} $*"; }
log_err() { echo -e "${RED}[ERROR]${NC} $*" >&2; }

LAST_AGENT_ID=""

register_agent() {
    local name="$1"
    local description="$2"
    local instruction="$3"

    log_info "Registering agent: ${name}"

    local instruction_json
    instruction_json=$(printf '%s' "$instruction" | jq -Rs .)

    local payload
    payload=$(cat <<EOF
{
    "name": "${name}",
    "description": "${description}",
    "owner_id": "demo",
    "mode": "serverless",
    "spawn_config": {
        "image": "${IMAGE}",
        "model": {"provider": "${MODEL_PROVIDER}", "model_id": "${MODEL_ID}"},
        "instruction": ${instruction_json},
        "tools": []
    }
}
EOF
)

    local response
    response=$(curl -s -X POST "${API_URL}/api/v1/agents" \
        -H "Content-Type: application/json" \
        -d "$payload")

    local agent_id
    agent_id=$(echo "$response" | jq -r '.id // empty')

    if [[ -z "$agent_id" ]]; then
        log_err "Failed to register ${name}: ${response}"
        exit 1
    fi

    LAST_AGENT_ID="$agent_id"
    log_ok "${name} -> ${agent_id}"
}

create_channel() {
    local name="$1"
    local description="$2"
    shift 2
    local ids=("$@")

    log_info "Creating channel: ${name}"

    local ids_json
    ids_json=$(printf '%s\n' "${ids[@]}" | jq -R . | jq -s .)

    local payload
    payload=$(cat <<EOF
{
    "name": "${name}",
    "description": "${description}",
    "agent_ids": ${ids_json},
    "owner_id": "demo"
}
EOF
)

    local response
    response=$(curl -s -X POST "${API_URL}/api/v1/channels" \
        -H "Content-Type: application/json" \
        -d "$payload")

    local channel_id
    channel_id=$(echo "$response" | jq -r '.id // empty')

    if [[ -z "$channel_id" ]]; then
        log_err "Failed to create channel: ${response}"
        exit 1
    fi

    log_ok "${name} -> ${channel_id} (${#ids[@]} agents)"
}

main() {
    echo "=========================================="
    echo "  A4S Demo Setup"
    echo "=========================================="
    echo ""

    # Check API
    if ! curl -sf "${API_URL}/livez" > /dev/null 2>&1; then
        log_err "API not available at ${API_URL}"
        log_err "Start infrastructure first: docker compose -f compose.dev.yml up -d"
        exit 1
    fi
    log_ok "API is available"
    echo ""

    # -- Agents --
    log_info "=== Registering Agents ==="

    register_agent "mneme" \
        "Personal AI companion that learns from conversations and builds a knowledge graph of people, projects, preferences, and context" \
        "$(cat <<'INST'
You are Mneme, a personal AI companion that continuously learns from your user. You build a knowledge graph of everything meaningful - people, projects, preferences, and context.

When you encounter meaningful information:
1. Call add_memory immediately to save it
2. Briefly mention what you saved at the end of your response

Save: people, roles, relationships, work projects, decisions, deadlines, preferences, goals, interests.
Skip: trivial exchanges, duplicates (search first), sensitive info, ephemeral details.

When calling add_memory, use clear searchable titles, include context and relationships.
Search memory before asking questions - you may already know the answer. Surface relevant context proactively.
Never fabricate information.
INST
)"
    local mneme_id="${LAST_AGENT_ID}"

    register_agent "code-reviewer" \
        "Code review specialist that analyzes code for bugs, security issues, performance problems, and style improvements" \
        "$(cat <<'INST'
You are a code review specialist. When given code, analyze it for:
1. Bugs and logic errors
2. Security vulnerabilities (injection, XSS, auth issues)
3. Performance problems
4. Readability and maintainability

Provide specific, actionable feedback with line references. Prioritize issues by severity. Suggest fixes, not just problems.
INST
)"
    local code_reviewer_id="${LAST_AGENT_ID}"

    register_agent "technical-writer" \
        "Technical documentation writer that creates clear API docs, guides, READMEs, and architecture documents" \
        "$(cat <<'INST'
You are a technical writer. Create clear, well-structured documentation including:
- API references with request/response examples
- Getting started guides with step-by-step instructions
- Architecture decision records
- README files

Use consistent formatting. Include code examples. Write for developers who are new to the project.
INST
)"
    local tech_writer_id="${LAST_AGENT_ID}"

    register_agent "devops-engineer" \
        "DevOps specialist for CI/CD pipelines, Docker, Kubernetes, infrastructure-as-code, and deployment strategies" \
        "$(cat <<'INST'
You are a DevOps engineer. Help with:
- CI/CD pipeline design and troubleshooting
- Docker and container orchestration
- Infrastructure-as-code (Terraform, Pulumi)
- Monitoring and observability setup
- Deployment strategies (blue-green, canary, rolling)

Prioritize reliability and reproducibility. Explain trade-offs between approaches.
INST
)"
    local devops_id="${LAST_AGENT_ID}"

    register_agent "data-analyst" \
        "Data analysis specialist for SQL queries, data visualization, statistical analysis, and reporting" \
        "$(cat <<'INST'
You are a data analyst. Help with:
- Writing and optimizing SQL queries
- Data visualization recommendations
- Statistical analysis and hypothesis testing
- Building dashboards and reports
- Data cleaning and transformation

Explain your methodology. Provide queries that are readable and well-commented.
INST
)"
    local data_analyst_id="${LAST_AGENT_ID}"

    register_agent "security-auditor" \
        "Security specialist for threat modeling, vulnerability assessment, secure coding practices, and compliance" \
        "$(cat <<'INST'
You are a security auditor. Help with:
- Threat modeling and attack surface analysis
- Vulnerability assessment of code and architecture
- Secure coding practice recommendations
- Authentication and authorization design
- Compliance requirements (OWASP, SOC2, GDPR)

Categorize findings by severity (critical, high, medium, low). Provide remediation steps.
INST
)"
    local security_id="${LAST_AGENT_ID}"

    echo ""

    # -- Channels --
    log_info "=== Creating Channels ==="

    create_channel "engineering" \
        "Software engineering team for code reviews, documentation, and DevOps" \
        "$code_reviewer_id" "$tech_writer_id" "$devops_id"

    create_channel "data-team" \
        "Data and analytics team for queries, analysis, and reporting" \
        "$data_analyst_id" "$mneme_id"

    create_channel "security" \
        "Security review channel for audits, threat modeling, and compliance" \
        "$security_id" "$code_reviewer_id"

    create_channel "all-hands" \
        "All agents available for cross-functional collaboration" \
        "$mneme_id" "$code_reviewer_id" "$tech_writer_id" "$devops_id" "$data_analyst_id" "$security_id"

    echo ""
    echo "=========================================="
    log_ok "Demo setup complete"
    echo ""
    echo "Agents (serverless - start on first request):"
    echo "  mneme            ${mneme_id}"
    echo "  code-reviewer    ${code_reviewer_id}"
    echo "  technical-writer ${tech_writer_id}"
    echo "  devops-engineer  ${devops_id}"
    echo "  data-analyst     ${data_analyst_id}"
    echo "  security-auditor ${security_id}"
    echo ""
    echo "Channels:"
    echo "  engineering  -> code-reviewer, technical-writer, devops-engineer"
    echo "  data-team    -> data-analyst, mneme"
    echo "  security     -> security-auditor, code-reviewer"
    echo "  all-hands    -> all 6 agents"
    echo "=========================================="
}

main "$@"
