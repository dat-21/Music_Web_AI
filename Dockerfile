FROM python:3.11-slim AS builder

WORKDIR /app

ENV POETRY_VERSION=1.8.2
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}" poetry-plugin-export

COPY pyproject.toml poetry.lock ./

RUN poetry export -f requirements.txt --only main --without-hashes --output requirements.txt

FROM python:3.11-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN useradd --create-home --shell /usr/sbin/nologin appuser

COPY --from=builder /app/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

RUN chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD curl --fail http://127.0.0.1:8000/health || exit 1