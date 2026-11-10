FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    libpq-dev \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock ./

ENV PATH="/app/.venv/bin:$PATH"

RUN uv sync --frozen --no-dev --no-install-project

COPY src/ ./src/

ENV PYTHONPATH="/app"

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
