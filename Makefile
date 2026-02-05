.PHONY: help
help: ## Show this help
	@awk 'BEGIN {FS = ":.*?## "; printf "Usage: make [target]\n\n"} \
		/^##@/ {printf "\n%s\n", substr($$0, 5)} \
		/^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

##@ Development

.PHONY: format
format: ## Format code with ruff
	uv run ruff format

.PHONY: lint
lint: ## Check code with ruff
	uv run ruff check --fix

.PHONY: setup-dev
setup-dev: ## Setup development environment
	uv run pre-commit install

##@ Docker

.PHONY: up
up: ## Start services
	docker build -t a4s-personal-assistant:latest -f agents/personal-assistant/Dockerfile .
	docker compose -f compose.dev.yml up -d

.PHONY: down
down: ## Stop services
	docker compose -f compose.dev.yml down

.PHONY: deploy
deploy: ## Deploy services
	@echo ""
	@echo "Services:"
	@echo "  - Gateway: http://localhost:8080"
	@echo "  - API: http://localhost:8000"
	@echo "  - Qdrant: http://localhost:6333"
	@echo "  - FalkorDB: http://localhost:6379"
