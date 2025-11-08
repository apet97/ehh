# Multi-stage build for production-ready container

# Builder stage
FROM python:3.11-slim AS builder
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.11-slim
WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 clankerbot && chown -R clankerbot:clankerbot /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/clankerbot/.local

# Copy application code
COPY --chown=clankerbot:clankerbot . .

# Switch to non-root user
USER clankerbot

# Update PATH
ENV PATH=/home/clankerbot/.local/bin:$PATH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/healthz')"

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
