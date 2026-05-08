FROM python:3.11-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PROJECT_DIR=/app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR $PROJECT_DIR

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project

COPY . /app

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen

RUN SECRET_KEY=dummy-key uv run python src/manage.py collectstatic --noinput

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH=/app/src

WORKDIR /app/src

EXPOSE 8000

CMD ["gunicorn", "personal_finance_api.wsgi:application", "--bind", "0.0.0.0:8000"]
