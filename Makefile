
.DEFAULT_GOAL := help

ROOT_DIR := $(dir $(abspath $(lastword $(MAKEFILE_LIST))))

ENV_FILE ?= .env
ENV_PATH := $(abspath $(ENV_FILE))

DOCKER ?= docker
OLLAMA ?= ollama
UV ?= uv
MONITOR_DIR := $(ROOT_DIR)nifi-monitor
MODEL ?= gemma4:e4b-it-q4_K_M
OLLAMA_BIND ?= 127.0.0.1:11434

NIFI_COMPOSE_FILE := $(ROOT_DIR)docker/compose.nifi.yml

NIFI_COMPOSE = $(DOCKER) compose \
	--env-file "$(ENV_PATH)" \
	-f "$(NIFI_COMPOSE_FILE)"

.PHONY: help check-env \
	nifi nifi-up nifi-down nifi-logs nifi-ps \
	nifi-config nifi-pull \
	ollama-serve ollama ollama-gemma ollama-qwen \
	monitor-run monitor-lint monitor-format monitor-format-check \
	monitor-typecheck monitor-test monitor-check

# ==========================================
# Help
# ==========================================

help:
	@printf '%s\n' \
	  'AI Integration & Incident Analysis Platform' \
	  '' \
	  'Apache NiFi:' \
	  '  make nifi          Start NiFi' \
	  '  make nifi-up       Start NiFi' \
	  '  make nifi-down     Stop NiFi (keep volumes)' \
	  '  make nifi-logs     Follow NiFi logs' \
	  '  make nifi-ps       Show NiFi container status' \
	  '  make nifi-config   Validate Compose configuration' \
	  '  make nifi-pull     Pull NiFi Docker image' \
	  '' \
	  'Ollama:' \
	  '  make ollama-serve  Start Ollama server' \
	  '  make ollama        Run configured model' \
	  '  make ollama-gemma  Run Gemma' \
	  '  make ollama-qwen   Run Qwen' \
	  '' \
	  'Python NiFi monitor:' \
	  '  make monitor-run          Run CLI against local NiFi' \
	  '  make monitor-lint         Ruff lint (no changes)' \
	  '  make monitor-format       Ruff auto-format (modifies files)' \
	  '  make monitor-format-check Check formatting (no changes)' \
	  '  make monitor-typecheck    Mypy strict static types' \
	  '  make monitor-test         Run offline pytest tests' \
	  '  make monitor-check        Run all non-mutating quality checks' \
	  '' \
	  'Environment:' \
	  '  ENV_FILE=.env by default' \
	  '  MODEL=gemma4:e4b-it-q4_K_M by default'

# ==========================================
# Environment
# ==========================================

check-env:
	@test -f "$(ENV_PATH)" || { \
		echo "Missing environment file: $(ENV_PATH)"; \
		echo "Create .env from .env.example"; \
		exit 1; \
	}

# ==========================================
# Apache NiFi
# ==========================================

nifi: nifi-up

nifi-up: check-env
	$(NIFI_COMPOSE) up -d nifi

nifi-down: check-env
	$(NIFI_COMPOSE) down

nifi-logs: check-env
	$(NIFI_COMPOSE) logs -f nifi

nifi-ps: check-env
	$(NIFI_COMPOSE) ps

nifi-config: check-env
	$(NIFI_COMPOSE) config --quiet

nifi-pull: check-env
	$(NIFI_COMPOSE) pull nifi

# ==========================================
# Ollama (local model runtime)
# ==========================================

ollama-serve:
	OLLAMA_HOST="$(OLLAMA_BIND)" $(OLLAMA) serve

ollama:
	$(OLLAMA) run "$(MODEL)"

ollama-gemma:
	$(OLLAMA) run "gemma4:e4b-it-q4_K_M"

ollama-qwen:
	$(OLLAMA) run "qwen3.5:9b"

# ==========================================
# Python NiFi monitor (uv-managed project)
# ==========================================

monitor-run:
	cd "$(MONITOR_DIR)" && $(UV) run nifi-monitor

monitor-lint:
	cd "$(MONITOR_DIR)" && $(UV) run ruff check .

monitor-format:
	cd "$(MONITOR_DIR)" && $(UV) run ruff format .

monitor-format-check:
	cd "$(MONITOR_DIR)" && $(UV) run ruff format --check .

monitor-typecheck:
	cd "$(MONITOR_DIR)" && $(UV) run mypy src

monitor-test:
	cd "$(MONITOR_DIR)" && $(UV) run pytest -v

monitor-check: monitor-lint monitor-format-check monitor-typecheck monitor-test
