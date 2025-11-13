# Architecture: Stateless MCP Server for Chat Applications

## 🎯 Design Philosophy

**This MCP server is a stateless compute service** - it performs simulations and returns results. It does NOT:
- ❌ Store user data
- ❌ Handle authentication
- ❌ Manage user sessions
- ❌ Persist simulation results

**Your chat app handles:**
- ✅ User authentication (via Supabase)
- ✅ Chat history and context
- ✅ Storing simulation results (if needed)
- ✅ User-specific data management

---

## 📊 How It Works

### Request Flow

```
┌─────────────────────────────────┐
│   Your Chat App (Supabase)      │
│   - User authenticated          │
│   - Chat context stored         │
│   - User wants simulation       │
└──────────────┬──────────────────┘
               │ HTTP POST
               │ (No auth needed)
               ▼
┌─────────────────────────────────┐
│   MCP Server (Stateless)        │
│   - Receives parameters         │
│   - Runs simulation             │
│   - Returns JSON data           │
│   - No storage, no auth         │
└──────────────┬──────────────────┘
               │ JSON Response
               │ (data + metrics)
               ▼
┌─────────────────────────────────┐
│   Your Chat App                 │
│   - Receives results            │
│   - Stores in Supabase (if needed)│
│   - Displays to user            │
│   - Manages user context        │
└─────────────────────────────────┘
```

---

## 💾 Storage Strategy

### Option 1: No Persistence (Recommended for Most Cases)

**When to use:** Real-time interactive simulations, ephemeral results

```typescript
// Chat app calls MCP server
const result = await mcpClient.callTool({
  name: "simulate_model",
  arguments: {
    // ... parameters
    return_data: true,
    save_artifacts: false  // No files needed
  }
});

// Use data immediately, don't store
displayGraph(result.data);
```

**Benefits:**
- ✅ Fastest response
- ✅ No storage costs
- ✅ Simple architecture
- ✅ Results are fresh each time

### Option 2: Store in Supabase (For Chat History)

**When to use:** Users want to see past simulations in chat history

```typescript
// Chat app calls MCP server
const result = await mcpClient.callTool({
  name: "simulate_model",
  arguments: {
    // ... parameters
    return_data: true,
    save_artifacts: false
  }
});

// Store in Supabase
await supabase.from('simulations').insert({
  user_id: currentUser.id,
  chat_id: currentChat.id,
  parameters: result.arguments,
  data: result.data,  // Store JSON data
  metrics: result.metrics,
  created_at: new Date()
});

// Display to user
displayGraph(result.data);
```

**Benefits:**
- ✅ Chat history preserved
- ✅ Users can reference past simulations
- ✅ Full control over data retention
- ✅ User-specific access control

### Option 3: Generate Files Client-Side (For Exports)

**When to use:** Users want to download CSV/PNG files

```typescript
// Chat app calls MCP server
const result = await mcpClient.callTool({
  name: "simulate_model",
  arguments: {
    // ... parameters
    return_data: true,
    save_artifacts: false  // Don't save on server
  }
});

// Generate CSV client-side
const csv = generateCSV(result.data, result.columns);
const blob = new Blob([csv], { type: 'text/csv' });
const url = URL.createObjectURL(blob);

// Download
const a = document.createElement('a');
a.href = url;
a.download = 'simulation.csv';
a.click();

// Generate PNG client-side (using Chart.js, Plotly, etc.)
const canvas = generatePlot(result.data);
canvas.toBlob((blob) => {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'simulation.png';
  a.click();
});
```

**Benefits:**
- ✅ No server storage needed
- ✅ Files generated on-demand
- ✅ User controls downloads
- ✅ No cleanup required

### Option 4: Upload to Supabase Storage (For Sharing)

**When to use:** Users want to share simulation files

```typescript
// Chat app calls MCP server
const result = await mcpClient.callTool({
  name: "simulate_model",
  arguments: {
    // ... parameters
    return_data: true,
    save_artifacts: false
  }
});

// Generate files client-side
const csv = generateCSV(result.data);
const png = await generatePNG(result.data);

// Upload to Supabase Storage
const { data: csvFile } = await supabase.storage
  .from('simulations')
  .upload(`${user.id}/${simulationId}.csv`, csv);

const { data: pngFile } = await supabase.storage
  .from('simulations')
  .upload(`${user.id}/${simulationId}.png`, png);

// Get public URLs
const csvUrl = supabase.storage
  .from('simulations')
  .getPublicUrl(`${user.id}/${simulationId}.csv`);

const pngUrl = supabase.storage
  .from('simulations')
  .getPublicUrl(`${user.id}/${simulationId}.png`);

// Store metadata in Supabase
await supabase.from('simulations').insert({
  user_id: user.id,
  chat_id: chatId,
  csv_url: csvUrl.data.publicUrl,
  png_url: pngUrl.data.publicUrl,
  // ... other metadata
});
```

**Benefits:**
- ✅ Files accessible via URLs
- ✅ User-specific access control
- ✅ Can share links
- ✅ Managed by Supabase

---

## 🔐 Authentication Strategy

### MCP Server: No Authentication Needed ✅

**Why:**
- Server is stateless
- No user data stored
- No sensitive operations
- Just computes and returns

**Security:**
- Rate limiting (optional, via Render or nginx)
- Input validation (already implemented)
- No user context = no user data leaks

### Chat App: Handles All Authentication ✅

**Your chat app should:**
1. Authenticate users (via Supabase Auth)
2. Validate user permissions
3. Call MCP server with parameters
4. Store results in Supabase (if needed)
5. Display results to authenticated user

**Example:**

```typescript
// In your chat app API route or server action
export async function runSimulation(params: SimulationParams, userId: string) {
  // 1. Verify user is authenticated
  const { data: user } = await supabase.auth.getUser();
  if (!user || user.id !== userId) {
    throw new Error('Unauthorized');
  }

  // 2. Call MCP server (no auth needed)
  const result = await mcpClient.callTool({
    name: "simulate_model",
    arguments: {
      ...params,
      return_data: true,
      save_artifacts: false
    }
  });

  // 3. Store in Supabase (optional)
  await supabase.from('simulations').insert({
    user_id: userId,
    parameters: params,
    results: result.data,
    metrics: result.metrics
  });

  // 4. Return to user
  return result;
}
```

---

## 📋 Recommended Supabase Schema

If you want to store simulation results:

```sql
-- Simulations table
CREATE TABLE simulations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  chat_id UUID REFERENCES chats(id) ON DELETE CASCADE,
  
  -- Parameters
  domain TEXT NOT NULL,
  model_type TEXT NOT NULL,
  parameters JSONB NOT NULL,
  initial_conditions JSONB NOT NULL,
  time_span JSONB NOT NULL,
  
  -- Results
  data JSONB,  -- Time series data
  metrics JSONB,  -- Calculated metrics
  summary TEXT,
  
  -- Metadata
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast queries
CREATE INDEX idx_simulations_user_id ON simulations(user_id);
CREATE INDEX idx_simulations_chat_id ON simulations(chat_id);
CREATE INDEX idx_simulations_created_at ON simulations(created_at DESC);

-- Row Level Security (RLS)
ALTER TABLE simulations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own simulations"
  ON simulations FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own simulations"
  ON simulations FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own simulations"
  ON simulations FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own simulations"
  ON simulations FOR DELETE
  USING (auth.uid() = user_id);
```

---

## 🎯 Integration Example

### Complete Flow in Your Chat App

```typescript
// pages/api/simulate.ts (Next.js API route example)
import { createClient } from '@supabase/supabase-js';
import { MCPClient } from '@modelcontextprotocol/sdk/client';

const supabase = createClient(
  process.env.SUPABASE_URL!,
  process.env.SUPABASE_SERVICE_ROLE_KEY!
);

const mcpClient = new MCPClient({
  serverUrl: process.env.MCP_SERVER_URL! // https://simulator-mcp-server.onrender.com/mcp
});

export default async function handler(req, res) {
  // 1. Authenticate user
  const authHeader = req.headers.authorization;
  if (!authHeader) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  const { data: { user }, error: authError } = await supabase.auth.getUser(
    authHeader.replace('Bearer ', '')
  );

  if (authError || !user) {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  // 2. Get parameters from request
  const { parameters, initial_conditions, time_span, chat_id } = req.body;

  // 3. Call MCP server (stateless, no auth)
  const result = await mcpClient.callTool({
    name: "simulate_model",
    arguments: {
      domain: "epidemiology",
      model_type: "SIR",
      parameters,
      initial_conditions,
      time_span: {
        ...time_span,
        preview_mode: true  // Fast for interactive
      },
      return_data: true,
      save_artifacts: false  // No files needed
    }
  });

  const simulation = JSON.parse(result.content[0].text);

  // 4. Store in Supabase (optional)
  const { data: storedSim, error: storeError } = await supabase
    .from('simulations')
    .insert({
      user_id: user.id,
      chat_id: chat_id,
      domain: 'epidemiology',
      model_type: 'SIR',
      parameters,
      initial_conditions,
      time_span,
      data: simulation.data,
      metrics: simulation.metrics,
      summary: simulation.summary
    })
    .select()
    .single();

  if (storeError) {
    console.error('Failed to store simulation:', storeError);
    // Continue anyway - simulation succeeded
  }

  // 5. Return results
  return res.status(200).json({
    success: true,
    simulation: {
      ...simulation,
      id: storedSim?.id  // Include DB ID if stored
    }
  });
}
```

---

## ✅ Summary

### MCP Server Responsibilities:
- ✅ Run simulations
- ✅ Return JSON data
- ✅ Calculate metrics
- ✅ Validate inputs

### MCP Server Does NOT:
- ❌ Store user data
- ❌ Handle authentication
- ❌ Manage sessions
- ❌ Persist results

### Your Chat App Responsibilities:
- ✅ Authenticate users (Supabase Auth)
- ✅ Store simulation results (Supabase DB)
- ✅ Manage chat context
- ✅ Handle file generation/export (if needed)
- ✅ Control access to user data

### Benefits:
- ✅ **Simple:** MCP server is just compute
- ✅ **Scalable:** No state = easy to scale
- ✅ **Secure:** No user data on MCP server
- ✅ **Flexible:** Chat app controls persistence
- ✅ **Cost-effective:** No storage costs for MCP server

---

## 🚀 Deployment

**Render Configuration:**
- ✅ No persistent disk needed
- ✅ Stateless operation
- ✅ No authentication setup
- ✅ Just deploy and run

**Cost:**
- Free tier: Works fine (spins down after inactivity)
- Starter ($7/month): Recommended for production
- No storage costs!

---

**Your MCP server is now a pure compute service - perfect for your chat app architecture!** 🎉

