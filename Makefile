dc_up:
	@docker compose up -d

dc_build:
	@docker compose build --no-cache

dc_down:
	@docker compose down -v

test:
	@uv run pytest -n auto

lint:
	@uv run ruff check .

pre_commit:
	@uv run pre-commit run -a

test_cov:
	@uv run pytest -n auto --cov=src --cov-report=term-missing --cov-report=html

migration:
	@cd src && uv run python manage.py makemigrations

migrate:
	@cd src && uv run python manage.py migrate

server: migrate
	@cd src && uv run python manage.py runserver

messages:
	@cd src && uv run python manage.py makemessages -l pt_BR

# ============================================================
# Local — PostgreSQL via Docker (requer .env.local)
# Copie sample.env.local para .env.local antes de usar:
#   cp sample.env.local .env.local
# ============================================================

local_dc_up:
	@docker compose -f docker-compose.local.yml --env-file .env.local up -d

local_dc_down:
	@docker compose -f docker-compose.local.yml down -v

local_migrate: local_dc_up
	@set -a && . ./.env.local && set +a && cd src && uv run python manage.py migrate

local_server: local_migrate
	@set -a && . ./.env.local && set +a && cd src && uv run python manage.py runserver

local_test: local_dc_up
	@set -a && . ./.env.local && set +a && uv run pytest -n auto

local_test_cov: local_dc_up
	@set -a && . ./.env.local && set +a && uv run pytest -n auto --cov=src --cov-report=term-missing --cov-report=html

.PHONY: dc_up dc_build dc_down test test_cov lint pre_commit migration migrate server messages \
        local_dc_up local_dc_down local_migrate local_server local_test local_test_cov
