# Deployment Guide

## Transport Modes

This MCP server supports multiple transport modes:

- **`streamable-http`** (recommended for production): HTTP-based MCP standard
- **`stdio`** (default for local dev): stdin/stdout communication
- **`sse`** (deprecated): Server-Sent Events over HTTP

The transport mode is controlled via the `MCP_TRANSPORT` environment variable.

## Quick Start

### 1. Verify Requirements Installation

```bash
# Test that requirements.txt can be parsed
pip install --dry-run -r requirements.txt

# Install dependencies (if dry-run succeeds)
pip install -r requirements.txt
```

### 2. Local Testing

#### Option A: stdio mode (default)
```bash
# Activate virtual environment
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Test the server starts (will wait for input on stdio)
python server.py
```

#### Option B: HTTP mode (production-like)
```bash
# Activate virtual environment
source venv/bin/activate

# Run with HTTP transport
export MCP_TRANSPORT=streamable-http
python server.py

# Test health endpoint
curl http://localhost:8000/health
```

### 3. Docker Build Test

```bash
# Build the image
docker build -t simulation-mcp:latest .

# Test run with HTTP mode (production default)
docker run -p 8000:8000 --rm simulation-mcp:latest

# In another terminal, test health endpoint
curl http://localhost:8000/health

# Test with stdio mode (local dev)
docker run -it --rm -e MCP_TRANSPORT=stdio simulation-mcp:latest
```

### 4. Docker Compose Deployment

```bash
# Build and start (configured for HTTP mode)
docker-compose up --build

# In another terminal, test the server
curl http://localhost:8000/health

# Check logs
docker-compose logs -f

# Stop when done
docker-compose down
```

## Troubleshooting

### Issue: `pip install -r requirements.txt` fails

**Solution:** Ensure you're using the correct format. The requirements.txt should have one package per line:
```
mcp[cli]>=1.2.0
pydantic>=2.7
...
```

### Issue: Matplotlib fails in Docker

**Solution:** The Dockerfile includes system dependencies for matplotlib. If you see errors, ensure:
- `libpng-dev` and `libfreetype6-dev` are installed (already in Dockerfile)
- If building locally, install: `sudo apt-get install libpng-dev libfreetype6-dev`

### Issue: Storage directory permissions

**Solution:** Ensure the storage directory exists and is writable:
```bash
mkdir -p storage
chmod 755 storage
```

### Issue: Module import errors

**Solution:** Ensure you're running from the project root and all dependencies are installed:
```bash
python -c "import mcp, pydantic, numpy, scipy, matplotlib; print('All imports successful')"
```

## Deploying to Render

### Prerequisites
- GitHub repository with your code
- Render account (free tier available)

### Steps

1. **Push your code to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Create Web Service on Render:**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the `render.yaml` configuration

3. **Automatic Configuration:**
   The `render.yaml` file configures:
   - Docker environment
   - HTTP transport mode
   - Persistent disk (10GB) at `/data`
   - Health check at `/health`
   - Environment variables

4. **Access Your Server:**
   - Render provides: `https://your-app.onrender.com`
   - Health check: `https://your-app.onrender.com/health`
   - MCP endpoint: `https://your-app.onrender.com/mcp`

### Environment Variables on Render

Set these in the Render dashboard if needed (already configured in `render.yaml`):

- `MCP_TRANSPORT=streamable-http` - HTTP mode for MCP
- `STORAGE_PATH=/data/storage` - Use Render persistent disk
- `PORT=8000` - Server port (Render may override)

## Production Considerations

1. **✅ Artifact Storage**: Configured with Render Disk (10GB persistent volume at `/data`)
2. **✅ Health Checks**: Implemented at `/health` endpoint
3. **✅ HTTP Transport**: Using `streamable-http` (MCP standard)
4. **Resource Limits**: Configure in Render dashboard based on your needs:
   - Free tier: 512 MB RAM, 0.1 CPU
   - Starter: 512 MB RAM, 0.5 CPU
   - Standard: 2 GB RAM, 1 CPU
5. **Logging**: Consider adding structured logging (e.g., JSON logs) for better observability
6. **Monitoring**: Use Render's built-in monitoring or integrate external services
7. **Scaling**: For high volume, consider:
   - Upgrading Render instance size
   - Using cloud storage (S3) instead of disk
   - Implementing request queuing

