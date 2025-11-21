dc_up:
	@docker compose up -d

dc_down:
	@docker compose down -v

migration:
	@cd src && poetry run python manage.py makemigrations

migrate: dc_up
	@cd src && poetry run python manage.py migrate

server: dc_up
	@cd src && poetry run python manage.py runserver 0.0.0.0:8000

.PHONY: dc_up dc_down migration migrate server