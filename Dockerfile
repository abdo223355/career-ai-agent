# ─────────────────────────────────────────────────────────────────────────────
# STAGE 1: Build Dependencies
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /app

# Install system build dependencies and curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install lightweight CPU-only PyTorch first (avoids 2.5GB CUDA wheel downloads)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─────────────────────────────────────────────────────────────────────────────
# STAGE 2: Production Runtime Container
# ─────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runner

WORKDIR /app

# Install curl for Streamlit healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user and group
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app appuser

# Copy installed pip packages from builder stage
COPY --from=builder /usr/local /usr/local
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy application source code
COPY . .

# Ensure proper permissions for runtime volumes and SQLite DBs
RUN mkdir -p storage data logs && \
    chown -R appuser:appgroup /app

USER appuser

EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "src/ui/chat.py", "--server.port=8501", "--server.address=0.0.0.0"]

