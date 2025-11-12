# Logging & Debugging Guide

Your MCP server now has comprehensive logging to help you troubleshoot integration issues with your chat app.

## 🔍 What Gets Logged

### Server Startup
- Transport mode (stdio, HTTP, SSE)
- Storage location
- Available solvers
- Port number (for HTTP mode)
- Log level

### Health Checks
- Every time `/health` is accessed

### Simulation Requests
- **Request details**: Domain, model type, all parameters
- **Validation**: JSON schema validation status
- **Solver execution**: Which solver, execution time, output shape
- **Artifact saving**: CSV and plot file creation (if enabled)
- **Data conversion**: JSON serialization progress
- **Response**: Total response size
- **Errors**: Full stack traces for debugging

## 📊 Log Levels

Control log verbosity with the `LOG_LEVEL` environment variable:

| Level | What You See | When to Use |
|-------|--------------|-------------|
| `DEBUG` | Everything including validation details | Deep troubleshooting |
| `INFO` | Normal operations, requests, responses | **Recommended** for development |
| `WARNING` | Issues that don't stop execution | Production monitoring |
| `ERROR` | Failures and exceptions | Problem diagnosis |

### Set Log Level

**Docker Compose:**
```yaml
environment:
  - LOG_LEVEL=INFO  # or DEBUG, WARNING, ERROR
```

**Docker Run:**
```bash
docker run -e LOG_LEVEL=DEBUG simulation-mcp:latest
```

**Render:**
Add to `render.yaml`:
```yaml
envVars:
  - key: LOG_LEVEL
    value: INFO
```

## 📝 Example Log Output

### Successful Request
```
2025-01-15 10:30:45,123 - simulation-mcp - INFO - ================================================================================
2025-01-15 10:30:45,124 - simulation-mcp - INFO - 📊 New simulation request received - Run ID: sir_20250115T103045_a1b2c3d4
2025-01-15 10:30:45,124 - simulation-mcp - INFO -    Domain: epidemiology
2025-01-15 10:30:45,124 - simulation-mcp - INFO -    Model: SIR
2025-01-15 10:30:45,125 - simulation-mcp - INFO -    Parameters: {'beta': 0.3, 'gamma': 0.1}
2025-01-15 10:30:45,125 - simulation-mcp - INFO -    Initial conditions: {'S': 0.99, 'I': 0.01, 'R': 0}
2025-01-15 10:30:45,125 - simulation-mcp - INFO -    Time span: start=0, end=160, steps=600
2025-01-15 10:30:45,125 - simulation-mcp - INFO -    Preview mode: True
2025-01-15 10:30:45,126 - simulation-mcp - INFO -    Return data: True
2025-01-15 10:30:45,126 - simulation-mcp - INFO -    Save artifacts: False
2025-01-15 10:30:45,126 - simulation-mcp - INFO -    Method: RK45
2025-01-15 10:30:45,126 - simulation-mcp - INFO - ⚡ Preview mode enabled: reducing steps from 600 to 100
2025-01-15 10:30:45,127 - simulation-mcp - INFO - 🔄 Running solver: SIR with 100 steps...
2025-01-15 10:30:45,245 - simulation-mcp - INFO - ✅ Solver completed in 0.118 seconds
2025-01-15 10:30:45,245 - simulation-mcp - INFO -    Output shape: t=100 points, Y=(3, 100)
2025-01-15 10:30:45,246 - simulation-mcp - INFO -    Metrics: {'I_peak': 0.3743, 't_peak': 33.89, 'summary': 'Peak infection 0.3743 at t ≈ 33.89'}
2025-01-15 10:30:45,246 - simulation-mcp - INFO - ⏭️  Skipping artifact saving (save_artifacts=False)
2025-01-15 10:30:45,247 - simulation-mcp - INFO - 📦 Converting 100 data points to JSON format...
2025-01-15 10:30:45,250 - simulation-mcp - INFO -    ✅ Data conversion complete (100 points)
2025-01-15 10:30:45,252 - simulation-mcp - INFO - ✨ Simulation sir_20250115T103045_a1b2c3d4 completed successfully
2025-01-15 10:30:45,252 - simulation-mcp - INFO -    Response size: ~12543 bytes
2025-01-15 10:30:45,252 - simulation-mcp - INFO - ================================================================================
```

### Error Example
```
2025-01-15 10:35:12,789 - simulation-mcp - INFO - ================================================================================
2025-01-15 10:35:12,790 - simulation-mcp - INFO - 📊 New simulation request received - Run ID: sir_20250115T103512_xyz789
2025-01-15 10:35:12,790 - simulation-mcp - ERROR - ❌ No solver registered for domain=epidemiology, model_type=InvalidModel
2025-01-15 10:35:12,791 - simulation-mcp - INFO -    Available solvers: [('epidemiology', 'SIR')]
```

### Solver Error Example
```
2025-01-15 10:40:30,456 - simulation-mcp - INFO - 🔄 Running solver: SIR with 600 steps...
2025-01-15 10:40:30,478 - simulation-mcp - ERROR - ❌ Solver error: ValueError: Initial conditions must sum to approximately 1.0
2025-01-15 10:40:30,479 - simulation-mcp - ERROR - Full traceback:
Traceback (most recent call last):
  File "/app/server.py", line 202, in simulate_model
    t, Y, metrics = SOLVERS[key](...)
  File "/app/models/sir.py", line 25, in simulate_sir
    raise ValueError("Initial conditions must sum to approximately 1.0")
ValueError: Initial conditions must sum to approximately 1.0
```

## 🐛 Troubleshooting Your Chat App Integration

### Problem: No logs appearing

**Check:**
1. Server is running: `docker ps` or check Render dashboard
2. Logs are being streamed: `docker logs -f simulation-mcp-server`
3. On Render: Click your service → "Logs" tab

### Problem: Chat app says "connection failed"

**Look for:**
```
No "New simulation request received" log
```
**Means:** Server isn't receiving requests
**Solution:**
- Check URL is correct: `https://your-app.onrender.com/mcp`
- Check transport mode: Should be `streamable-http`
- Test with curl (see below)

### Problem: Chat app gets error response

**Look for:**
```
❌ No solver registered
❌ JSON schema validation failed
❌ Solver error
```
**Means:** Request format is wrong
**Solution:**
- Check the error message in logs
- Verify parameter names match expected format
- See example requests in INTERACTIVE_UI_GUIDE.md

### Problem: Server receives request but chat app doesn't get response

**Look for:**
```
✨ Simulation completed successfully
Response size: ~12543 bytes
```
**Means:** Server sent response, but client didn't receive it
**Solution:**
- Check for network errors in browser console
- Verify MCP client configuration
- Try increasing timeout settings

### Problem: Slow responses

**Look for:**
```
✅ Solver completed in 5.234 seconds  # Too slow!
```
**Means:** Simulation taking too long
**Solution:**
- Enable preview mode: `preview_mode: true`
- Reduce steps: `steps: 100` instead of 600
- Disable artifacts: `save_artifacts: false`

## 🧪 Testing with curl

Test the server directly to isolate issues:

```bash
# Test health check
curl http://localhost:8000/health

# Test simulation (replace with your actual endpoint)
curl -X POST https://your-app.onrender.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "simulate_model",
      "arguments": {
        "domain": "epidemiology",
        "model_type": "SIR",
        "parameters": {"beta": 0.3, "gamma": 0.1},
        "initial_conditions": {"S": 0.99, "I": 0.01, "R": 0},
        "time_span": {"start": 0, "end": 160, "steps": 100, "preview_mode": true},
        "return_data": true,
        "save_artifacts": false
      }
    }
  }'
```

**If curl works but chat app doesn't:**
- Problem is in chat app's MCP client
- Check client configuration
- Verify authentication (if any)

**If curl doesn't work:**
- Problem is with server or network
- Check logs for errors
- Verify deployment on Render

## 📋 Viewing Logs

### Docker Compose (Local)
```bash
# Follow logs in real-time
docker compose logs -f

# View last 100 lines
docker compose logs --tail=100

# Filter by specific text
docker compose logs | grep "ERROR"
```

### Docker (Direct)
```bash
# Follow logs
docker logs -f simulation-mcp-server

# Last 100 lines
docker logs --tail=100 simulation-mcp-server
```

### Render (Production)
1. Go to Render Dashboard
2. Click on your service
3. Click "Logs" tab
4. Logs update in real-time
5. Use search box to filter

## 🎯 Common Patterns to Look For

### Pattern 1: Request Never Arrives
```
# You see:
Health check requested
Health check requested

# But NOT:
📊 New simulation request received
```
**Issue:** Client not sending to correct endpoint or wrong HTTP method

### Pattern 2: Wrong Parameters
```
# You see:
📊 New simulation request received
❌ No solver registered for domain=wrong, model_type=invalid
```
**Issue:** Check parameter names in chat app code

### Pattern 3: Everything Works Locally, Not on Render
```
# Local logs:
✨ Simulation completed successfully

# Render logs:
Connection timeout
```
**Issue:** Check Render environment variables, especially `PORT` and `MCP_TRANSPORT`

## 💡 Pro Tips

1. **Start with INFO level** - Shows all important operations
2. **Use DEBUG for deep issues** - But very verbose
3. **Search for emoji icons** - Quick visual scanning (📊, ✅, ❌, ⚡)
4. **Check timestamps** - Identify slow operations
5. **Watch response sizes** - Large responses may timeout
6. **Test health endpoint first** - Confirms server is running
7. **Compare working vs broken requests** - Side-by-side log comparison

## 🔧 Adjusting Logging

### Make Logs More Verbose
```yaml
# docker-compose.yml
environment:
  - LOG_LEVEL=DEBUG
```

### Make Logs Less Verbose
```yaml
# docker-compose.yml
environment:
  - LOG_LEVEL=WARNING
```

### Log to File (Advanced)
Modify `server.py` logging configuration:
```python
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # Console
        logging.FileHandler('/app/storage/server.log')  # File
    ]
)
```

## 📞 Getting Help

When asking for help, include:
1. **Full log output** (at least 50 lines before error)
2. **Request that was sent** (from chat app)
3. **Expected vs actual behavior**
4. **Environment** (local Docker, Render, etc.)
5. **Log level** being used

Example:
```
I'm getting "No solver registered" errors.

Environment: Render production
Log level: INFO
Request from chat app:
{
  "domain": "epidemiology",
  "model_type": "SIR",
  ...
}

Logs show:
❌ No solver registered for domain=epidemiology, model_type=SIR
Available solvers: [('epidemiology', 'SIR')]
```

---

**Happy Debugging! 🐛🔨**

