# Deploy to Render - Quick Start Guide

## ✅ Your Server is Ready to Deploy!

All configuration is complete. Just follow these steps to deploy.

## 📋 Pre-Deployment Checklist

- [x] HTTP transport configured (`streamable-http`)
- [x] Health check endpoint at `/health`
- [x] Host binding set to `0.0.0.0`
- [x] Dockerfile ready
- [x] render.yaml configured with persistent disk
- [x] Logging enabled
- [x] Data return for interactive UIs
- [x] .gitignore configured

**Status: 100% Ready! 🚀**

---

## 🚀 Deployment Steps

### Step 1: Initialize Git (if not already done)

```bash
cd /home/cnye/fiverr-projects/joseph-weblet-app/simulation-mcp-server

# Check if already a git repo
git status

# If not initialized, run:
git init
git add .
git commit -m "Initial commit: Production-ready MCP server"
```

### Step 2: Push to GitHub

```bash
# Create a new repository on GitHub (via web interface)
# Then connect it:

git remote add origin https://github.com/YOUR_USERNAME/simulation-mcp-server.git
git branch -M main
git push -u origin main
```

### Step 3: Deploy on Render

1. **Go to [render.com](https://render.com)**
2. **Sign in** (or create account)
3. Click **"New +"** → **"Web Service"**
4. Click **"Connect a repository"**
5. **Authorize GitHub** if needed
6. **Select your repository** (`simulation-mcp-server`)
7. Render will **auto-detect `render.yaml`** ✨
8. Review the configuration (should show):
   - Name: `simulation-mcp-server`
   - Environment: Docker
   - Plan: Starter ($7/month) or Free tier
   - Disk: 10GB at `/data`
9. Click **"Create Web Service"**

### Step 4: Wait for Build (~5-10 minutes)

Render will:
1. Clone your repo
2. Build Docker image
3. Deploy to production
4. Start the server

Watch the logs in real-time!

### Step 5: Get Your URL

Once deployed, you'll see:
```
🎉 Your service is live at https://simulation-mcp-server-xxxx.onrender.com
```

---

## 🧪 Testing Your Deployed Server

### Test 1: Health Check

```bash
curl https://your-app-name.onrender.com/health
```

**Expected:**
```json
{
  "status": "healthy",
  "service": "simulation-mcp",
  "version": "0.1.0",
  "storage": "/data/storage",
  "solvers": 1
}
```

### Test 2: MCP Endpoint

```bash
curl -X POST https://your-app-name.onrender.com/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'
```

### Test 3: Run a Simulation

```bash
curl -X POST https://your-app-name.onrender.com/mcp \
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

---

## 🔄 CI/CD - Automatic Deployments

**YES! Render has automatic CI/CD** 🎉

### How It Works

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Update simulation logic"
   git push origin main
   ```

2. **Render automatically:**
   - Detects the push
   - Rebuilds the Docker image
   - Deploys the new version
   - Zero downtime (with paid plans)

3. **Watch it happen:**
   - Go to Render Dashboard
   - See "Deploying..." status
   - Watch logs in real-time
   - Get notified when complete

### Iteration Workflow

```bash
# Make changes locally
vim server.py

# Commit and push
git add .
git commit -m "Add Lotka-Volterra model"
git push

# Render auto-deploys in ~3-5 minutes
# No manual steps needed!
```

### Disable Auto-Deploy (Optional)

If you want manual control:
1. Go to Render Dashboard
2. Click your service
3. Settings → "Auto-Deploy"
4. Toggle OFF

Then deploy manually when ready:
1. Click "Manual Deploy"
2. Select branch
3. Click "Deploy"

---

## 📊 Monitoring on Render

### View Logs

**Real-time:**
1. Render Dashboard → Your Service
2. Click "Logs" tab
3. See all startup and request logs

**Search logs:**
- Use the search box
- Filter by time range
- Look for emoji markers (📊, ✅, ❌)

### View Metrics

**Built-in metrics:**
- CPU usage
- Memory usage
- Request count
- Response times

**Available in:**
- Dashboard → Your Service → "Metrics" tab

### Alerts

Set up alerts for:
- Service down
- High CPU/memory
- Deploy failures

**Configure in:**
- Settings → "Alerts"

---

## 🔧 Common Render Issues & Fixes

### Issue: Build Fails

**Check:**
1. Logs for error message
2. Dockerfile syntax
3. requirements.txt compatibility

**Fix:**
- Push a fix to GitHub
- Render auto-rebuilds

### Issue: Service Won't Start

**Check logs for:**
```
Port 8000 already in use
```

**Fix:** Render sets PORT env var automatically, our server uses it ✅

### Issue: Health Check Failing

**Logs will show:**
```
Health check failed after 10 attempts
```

**Possible causes:**
- Server not starting (check logs)
- Wrong health check path
- Port mismatch

**Our config:**
```yaml
healthCheckPath: /health  # ✅ Correct
```

### Issue: Slow First Request (Free Tier)

**Render free tier:**
- Spins down after 15 min inactivity
- First request after spin-down: 30-60s
- Subsequent requests: fast

**Solution:**
- Upgrade to paid tier ($7/month)
- Or expect cold starts on free tier

---

## 💰 Render Pricing

### Free Tier
- ✅ 750 hours/month free
- ✅ Good for testing
- ❌ Spins down after 15 min inactivity
- ❌ No persistent disk
- ❌ Shared resources

### Starter ($7/month)
- ✅ Always on
- ✅ 512 MB RAM, 0.5 CPU
- ✅ 10GB persistent disk included ($0.25/GB)
- ✅ Perfect for this server
- ✅ **Recommended**

### Standard ($25/month)
- ✅ 2 GB RAM, 1 CPU
- ✅ Better performance
- ✅ More concurrent requests

---

## 🔗 Connecting Your Chat App

Once deployed, update your chat app configuration:

### Environment Variable
```bash
MCP_SERVER_URL=https://your-app-name.onrender.com/mcp
```

### In Your Code
```typescript
const client = new MCPClient({
  serverUrl: process.env.MCP_SERVER_URL || "https://your-app-name.onrender.com/mcp"
});
```

### Testing Connection

```typescript
// Test health first
const healthResponse = await fetch("https://your-app-name.onrender.com/health");
const health = await healthResponse.json();
console.log("Server health:", health);

// Then connect MCP client
await client.connect();
console.log("MCP connected!");
```

---

## 📝 Deployment Checklist

Before going live:

- [ ] Code pushed to GitHub
- [ ] Render service created
- [ ] Build completed successfully
- [ ] Health check passes
- [ ] Test simulation endpoint
- [ ] Update chat app URL
- [ ] Test chat app connection
- [ ] Monitor logs for issues
- [ ] Set up alerts (optional)
- [ ] Document production URL

---

## 🎯 Quick Commands Reference

```bash
# Local development
git status
git add .
git commit -m "Your message"
git push origin main

# Test deployed server
curl https://your-app.onrender.com/health

# View logs (via Dashboard UI)
# Render Dashboard → Service → Logs tab

# Manual deploy (via Dashboard UI)
# Render Dashboard → Service → Manual Deploy
```

---

## 🆘 Getting Help

**Render Support:**
- [Render Docs](https://render.com/docs)
- [Community Forum](https://community.render.com)
- Support via dashboard (paid plans)

**Your Server Logs:**
- Check LOGGING_GUIDE.md
- Look for emoji markers (📊, ✅, ❌)
- Search for "ERROR" or "error"

**Common Log Patterns:**
```
✅ Simulation completed successfully  # Good!
❌ Solver error: ...                   # Check parameters
🔄 Running solver...                   # In progress
```

---

## 🎉 You're Ready!

1. **Push to GitHub** ← Do this now
2. **Connect to Render** ← Takes 2 minutes
3. **Watch it deploy** ← 5-10 minutes
4. **Test endpoint** ← Verify it works
5. **Update chat app** ← Use production URL
6. **Iterate freely** ← Push to auto-deploy

**Render handles all the networking complexity for you!** 🚀

No more local Docker issues. Just push and deploy.

---

## 📞 Next Steps

1. **Run the deployment commands above**
2. **Get your production URL**
3. **Share the URL** (I'll help you test it)
4. **Connect your chat app**
5. **Start building your epidemic calculator!**

Happy deploying! 🎊

