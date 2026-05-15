FROM python:3.11-slim as builder

WORKDIR /app

ENV POETRY_VERSION=1.8.2
ENV POETRY_VIRTUALENVS_CREATE=false

RUN pip install --no-cache-dir "poetry==${POETRY_VERSION}" poetry-plugin-export

COPY pyproject.toml ./

RUN poetry export -f requirements.txt --without-hashes --output requirements.txt

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /app/requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]