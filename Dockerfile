FROM python:3.9-slim

# Create a non-root user
RUN useradd -m -u 1000 testuser

WORKDIR /app

# Install basic requirements and system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    bash \
    gcc \
    python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Install basic Python packages
RUN pip install --no-cache-dir pytest unittest2 pip setuptools wheel

# Create and set permissions for package installation directory
RUN mkdir -p /app/.local && \
    chown -R testuser:testuser /app

# Switch to non-root user
USER testuser

# Keep container running
CMD ["python", "-m", "unittest"]