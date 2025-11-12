FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for matplotlib and curl for health checks
RUN apt-get update && apt-get install -y \
    libpng-dev \
    libfreetype6-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# Create storage directory (fallback for local dev)
RUN mkdir -p /app/storage

# Create mount point for Render disk
RUN mkdir -p /data

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV MCP_TRANSPORT=streamable-http
ENV PORT=8000
ENV FASTMCP_HOST=0.0.0.0

EXPOSE 8000

# Run the MCP server
# Transport mode controlled by MCP_TRANSPORT env var:
# - streamable-http (default, production)
# - stdio (local development)
CMD ["python", "server.py"]
