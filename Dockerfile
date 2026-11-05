FROM python:3.12-slim

# WeasyPrint precisa do Pango; fontes serifadas para os PDFs; fuso para datas e prazos
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 fonts-liberation fonts-dejavu-core tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv==0.11.18

ENV TZ=America/Sao_Paulo \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH=/app/.venv/bin:$PATH \
    NICEGUI_STORAGE_PATH=/app/.nicegui \
    CLUBE_HOST=0.0.0.0 \
    CLUBE_PORTA=8080 \
    CLUBE_PRODUCAO=true

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY . .

EXPOSE 8080
CMD ["sh", "-c", "alembic upgrade head && exec python -m app.main"]
