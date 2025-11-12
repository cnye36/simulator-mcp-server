# Changelog

## [Unreleased] - 2025-11-12

### Added
- **HTTP Transport Support**: Server now supports `streamable-http` MCP transport mode (MCP standard)
- **Health Check Endpoint**: Added `/health` endpoint for deployment monitoring
- **Environment-Based Configuration**: Storage path configurable via `STORAGE_PATH` env var
- **Transport Mode Selection**: Choose transport via `MCP_TRANSPORT` env var (streamable-http, sse, stdio)
- **Docker Health Checks**: Added health check configuration to docker-compose.yml
- **Render Deployment Config**: Complete `render.yaml` with persistent disk support
- **Comprehensive Documentation**: 
  - Updated DEPLOYMENT.md with HTTP transport instructions
  - Added HTTP_TRANSPORT_SETUP.md quick reference guide
  - Added Render deployment section

### Changed
- **server.py**: 
  - Storage path now uses environment variable for flexibility
  - Main execution block supports multiple transport modes
  - Removed unused imports (Any, ValidationError)
- **Dockerfile**:
  - Added `curl` for health checks
  - Created `/data` mount point for Render disks
  - Set default environment to HTTP mode
  - Updated documentation comments
- **docker-compose.yml**:
  - Enabled HTTP mode by default
  - Exposed port 8000
  - Added environment variables for HTTP transport
  - Added health check configuration
  - Commented out stdio-specific settings (stdin_open, tty)
- **render.yaml**:
  - Updated transport from `sse` to `streamable-http`
  - Added PORT environment variable
- **requirements.txt**:
  - Already contained uvicorn and starlette (required for HTTP mode)

### Deprecated
- SSE transport mode (still supported but deprecated per MCP standards)

### Technical Details

#### Transport Modes
1. **streamable-http** (Production): HTTP-based MCP standard transport
2. **stdio** (Development): stdin/stdout communication for local testing
3. **sse** (Deprecated): Server-Sent Events over HTTP

#### Environment Variables
| Variable | Default | Description |
|----------|---------|-------------|
| MCP_TRANSPORT | stdio (local), streamable-http (Docker) | Transport mode |
| STORAGE_PATH | ./storage (local), /data/storage (Render) | Artifact storage location |
| PORT | 8000 | Server port |
| PYTHONUNBUFFERED | 1 | Disable Python output buffering |

#### Deployment Targets
- ✅ Local development (stdio mode)
- ✅ Docker / Docker Compose (HTTP mode)
- ✅ Render.com (HTTP mode with persistent disk)
- ❌ Vercel (not suitable - serverless timeouts, no persistent storage)

### Testing

All changes verified:
- ✅ Python syntax validation passed
- ✅ Import structure maintained
- ✅ Linting warnings minimal (only intentional module-level import)
- ✅ Docker configuration validated
- ✅ Render configuration complete

### Migration Guide

No breaking changes for existing deployments. The server automatically:
- Uses stdio mode by default for local development
- Uses HTTP mode when deployed via Docker/Render
- Falls back gracefully based on environment variables

To update existing deployments:
1. Pull latest changes
2. Rebuild Docker image: `docker-compose up --build`
3. Test health endpoint: `curl http://localhost:8000/health`

### Next Steps

Ready for production deployment:
1. Push code to GitHub
2. Connect to Render.com
3. Deploy using `render.yaml`
4. Access via `https://your-app.onrender.com`

### Notes

- Render Disk provides 10GB persistent storage at $0.25/GB/month
- Health checks run every 30 seconds
- Server supports graceful startup (40s grace period)
- Compatible with MCP 1.2.0+ specification


