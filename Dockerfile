FROM python:3.11-slim

WORKDIR /app

# Install curl for HEALTHCHECK
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8101

# Docker Healthcheck
HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost:8101/health || exit 1

ENV AUTOCAR_API_URL=https://auto.wan.ma

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8101"]
