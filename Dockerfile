# Multi-stage Dockerfile for MTG Card App
# Optimized for size and security

# Stage 1: Builder - compile dependencies
FROM python:3.11-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy only requirements first for better caching
COPY pyproject.toml README_PYPI.md LICENSE ./

# Install dependencies in a virtual environment
RUN python -m venv /app/venv
ENV PATH="/app/venv/bin:$PATH"

# Install the package and dependencies
COPY . .
RUN pip install --no-cache-dir -e .

# Stage 2: Runtime - minimal image
FROM python:3.11-slim

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 mtguser && \
    mkdir -p /home/mtguser/.mtg && \
    mkdir -p /home/mtguser/data && \
    chown -R mtguser:mtguser /home/mtguser

# Copy virtual environment from builder
COPY --from=builder /app/venv /app/venv

# Copy application code
WORKDIR /app
COPY --from=builder /app /app

# Set up environment
ENV PATH="/app/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    MTG_DATA_DIR=/home/mtguser/data \
    MTG_CONFIG_DIR=/home/mtguser/.mtg

# Switch to non-root user
USER mtguser

# Create volume mount points
VOLUME ["/home/mtguser/data", "/home/mtguser/.mtg"]

# Expose port if web UI is added in future
# EXPOSE 8000

# Default command: show version
CMD ["mtg", "--version"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD mtg --version || exit 1

# Labels for metadata
LABEL org.opencontainers.image.title="MTG Card App" \
      org.opencontainers.image.description="AI-powered Magic: The Gathering combo finder" \
      org.opencontainers.image.version="0.1.0" \
      org.opencontainers.image.authors="topherhaynie" \
      org.opencontainers.image.url="https://github.com/topherhaynie/mtg_card_app" \
      org.opencontainers.image.source="https://github.com/topherhaynie/mtg_card_app" \
      org.opencontainers.image.licenses="MIT"
