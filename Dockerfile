FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_HOME=/etc/poetry \
    PROJECT_DIR=/app
ENV PATH="$POETRY_HOME/bin:$PATH"

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR $PROJECT_DIR

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

COPY poetry.toml poetry.lock pyproject.toml ./

RUN poetry config virtualenvs.create false \
 && poetry install --no-interaction --no-ansi --no-root

COPY . /app

ENV PYTHONPATH=/app/src

WORKDIR /app/src

EXPOSE 8000

CMD ["gunicorn", "personal_finance_api.wsgi:application", "--bind", "0.0.0.0:8000"]
