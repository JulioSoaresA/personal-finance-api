FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --no-root

COPY . /app

ENV PYTHONPATH=/app/src

WORKDIR /app/src

EXPOSE 8000

CMD ["gunicorn", "personal_finance_api.wsgi:application", "--bind", "0.0.0.0:8000"]
