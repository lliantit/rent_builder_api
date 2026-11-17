# Етап 1 Builder
FROM python:3.11-slim as builder
WORKDIR /app

# Залежності PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Віртуальне середовище та встановлюємо Python-залежності
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Етап 2 Runner
FROM python:3.11-slim as runner
WORKDIR /app

# Встановлюємо бібліотеку для PostgreSQL
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && rm -rf /var/lib/apt/lists/*

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Копіюємо вихідний код проєкту
COPY src/ ./src/

EXPOSE 8000

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]