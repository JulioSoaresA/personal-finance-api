dc_up:
	@docker compose up -d

dc_build:
	@docker compose build --no-cache

dc_down:
	@docker compose down -v

test: dc_up
	@uv run pytest -n auto

lint:
	uv run ruff check .

pre_commit:
	@uv run pre-commit run -a

test_cov: dc_up
	@uv run pytest -n auto --cov=src --cov-report=term-missing --cov-report=html

migration:
	@cd src && uv run python manage.py makemigrations

migrate: dc_up
	@cd src && uv run python manage.py migrate

server: dc_up migrate
	@cd src && uv run python manage.py runserver

messages:
	@cd src && uv run python manage.py makemessages -l pt_BR

.PHONY: test test_cov dc_up dc_down dc_build migration migrate server lint pre_commit messages
