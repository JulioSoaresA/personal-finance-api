dc_up:
	@docker compose up -d

dc_build:
	@docker compose build --no-cache

dc_down:
	@docker compose down -v

test: dc_up
	@pytest -n auto

lint:
	poetry run ruff check .

pre_commit:
	@pre-commit run -a

test_cov: dc_up
	@pytest -n auto --cov=src --cov-report=term-missing --cov-report=html

migration:
	@docker compose exec app bash -lc "cd /app/src && poetry run python manage.py makemigrations"

migrate: dc_up
	@docker compose exec app bash -lc "cd /app/src && poetry run python manage.py migrate"

server: dc_up
	@docker compose exec -T app bash -lc "cd /app/src && poetry run python manage.py runserver 0.0.0.0:8000"

.PHONY: test test_cov dc_up dc_down dc_build migration migrate server lint pre_commit
