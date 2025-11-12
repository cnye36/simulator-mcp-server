# Network Connection Fix

## 🐛 Problem

Docker container was running and showing "healthy", but:
- ❌ `curl http://localhost:8000/health` → Connection reset by peer
- ❌ Chat app couldn't connect
- ✅ Docker health checks passed (from inside container)

## 🔍 Root Cause

**FastMCP was binding to `127.0.0.1` (localhost) by default.**

When a server binds to `127.0.0.1` inside a Docker container:
- ✅ Connections from **inside the container** work (health checks)
- ❌ Connections from **outside the container** fail (your app, curl)

## ✅ Solution

**Set `FASTMCP_HOST=0.0.0.0` to bind to all network interfaces.**

This allows connections from:
- ✅ Inside the container (health checks)
- ✅ Host machine (curl from your terminal)
- ✅ External applications (your chat app)

## 🔧 Changes Made

### 1. docker-compose.yml
```yaml
environment:
  - FASTMCP_HOST=0.0.0.0  # NEW: Bind to all interfaces
```

### 2. Dockerfile
```dockerfile
ENV FASTMCP_HOST=0.0.0.0
```

### 3. render.yaml
```yaml
envVars:
  - key: FASTMCP_HOST
    value: "0.0.0.0"
```

## 🧪 Testing the Fix

### Step 1: Rebuild and Restart

```bash
# Stop current container
docker compose down

# Rebuild with new configuration
docker compose up --build
```

### Step 2: Test from Your Terminal

```bash
# Should now work!
curl http://localhost:8000/health
```

**Expected output:**
```json
{
  "status": "healthy",
  "service": "simulation-mcp",
  "version": "0.1.0",
  "storage": "/app/storage",
  "solvers": 1
}
```

### Step 3: Check Logs

You should see in the startup logs:
```
🌐 Running in HTTP mode (streamable-http)
   Binding to: 0.0.0.0:8000
```

Not:
```
   Binding to: 127.0.0.1:8000  # ❌ Wrong!
```

### Step 4: Test Your Chat App

Now your chat app should be able to connect to `http://localhost:8000/mcp`

## 📚 Understanding the Issue

### Network Binding Explained

**`127.0.0.1` (localhost):**
- Only accessible from the same machine
- In Docker: only from inside the container
- ❌ Cannot be accessed from host or other containers

**`0.0.0.0` (all interfaces):**
- Listens on all network interfaces
- In Docker: accessible from host via port mapping
- ✅ Can be accessed from anywhere the port is exposed

### Docker Port Mapping

```yaml
ports:
  - "8000:8000"  # Host:Container
```

This means:
- Container port 8000 → Host port 8000
- **But only works if server binds to 0.0.0.0 inside container!**

## 🔍 Debugging Similar Issues

### Check What the Server is Binding To

Look for this in startup logs:
```
Binding to: 0.0.0.0:8000  # ✅ Good
Binding to: 127.0.0.1:8000  # ❌ Bad
```

### Test Inside Container

```bash
# Open shell inside container
docker exec -it simulation-mcp-server sh

# Test from inside
curl http://localhost:8000/health  # Should work

# Test binding to all interfaces
curl http://0.0.0.0:8000/health    # Should work if bound to 0.0.0.0
```

### Common Symptoms

**Symptom:** Health checks pass, but external connections fail
**Cause:** Server bound to 127.0.0.1

**Symptom:** Works locally, fails in production
**Cause:** Missing FASTMCP_HOST=0.0.0.0 in production config

**Symptom:** curl fails with "Connection reset by peer"
**Cause:** Server not accessible on requested interface

## 📝 Configuration Checklist

For production deployment, ensure:
- [x] `FASTMCP_HOST=0.0.0.0` in docker-compose.yml
- [x] `FASTMCP_HOST=0.0.0.0` in Dockerfile
- [x] `FASTMCP_HOST=0.0.0.0` in render.yaml
- [x] Port exposed in Dockerfile: `EXPOSE 8000`
- [x] Port mapped in docker-compose.yml: `"8000:8000"`
- [x] Logs show correct binding: `Binding to: 0.0.0.0:8000`

## 🎯 Quick Reference

### Environment Variables for Network

| Variable | Value | Purpose |
|----------|-------|---------|
| `FASTMCP_HOST` | `0.0.0.0` | Bind to all interfaces (required for Docker) |
| `PORT` | `8000` | Port number |
| `MCP_TRANSPORT` | `streamable-http` | Use HTTP transport |

### Testing Commands

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test MCP endpoint (POST request needed)
curl -X POST http://localhost:8000/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'

# Check container is running
docker ps | grep simulation-mcp

# View logs
docker logs simulation-mcp-server

# Follow logs in real-time
docker logs -f simulation-mcp-server
```

## ✅ Verification

After rebuilding, you should see:

1. **Container starts successfully**
2. **Logs show:** `Binding to: 0.0.0.0:8000`
3. **curl works:** `curl http://localhost:8000/health`
4. **Chat app connects successfully**

If all checks pass: **Problem solved! 🎉**

---

**Note:** This fix is now permanent in all configuration files. Future deployments will work correctly.

