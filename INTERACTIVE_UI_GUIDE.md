# Interactive UI Integration Guide

This guide explains how to use the MCP server's new interactive features for building real-time epidemic calculators and simulation dashboards.

## 🎯 New Features

### 1. **Direct Data Return** (No More File Paths!)
The server now returns actual simulation data in JSON format, not just file paths.

### 2. **Preview Mode**
Fast rendering with reduced data points for real-time slider interactions.

### 3. **Optional Artifact Saving**
Skip file creation for even faster responses in interactive mode.

---

## 📊 Example Use Cases

### Use Case 1: Interactive Epidemic Calculator (Like the Screenshot)

**Goal:** User adjusts sliders (transmission rate, recovery time, etc.) and sees real-time graph updates.

#### Frontend Implementation

```typescript
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import Plotly from 'plotly.js';

// Initialize MCP client
const client = new Client({
  name: "epidemic-calculator",
  version: "1.0.0"
}, { capabilities: {} });

await client.connect(transport);

// User adjusts transmission rate slider
betaSlider.addEventListener('input', async (e) => {
  const beta = parseFloat(e.target.value);
  
  // Call server with preview mode for fast response
  const result = await client.callTool({
    name: "simulate_model",
    arguments: {
      domain: "epidemiology",
      model_type: "SIR",
      parameters: {
        beta: beta,        // From slider
        gamma: 0.1         // Recovery rate
      },
      initial_conditions: {
        S: 0.99,
        I: 0.01,
        R: 0
      },
      time_span: {
        start: 0,
        end: 160,
        steps: 600,
        preview_mode: true  // ⚡ Fast rendering (100 points max)
      },
      method: "RK45",
      return_data: true,      // ✅ Get actual data
      save_artifacts: false   // ⚡ Skip file saving
    }
  });
  
  // Parse the result
  const simulation = JSON.parse(result.content[0].text);
  
  // Update Plotly graph with real data
  updateGraph(simulation.data);
});

function updateGraph(data) {
  // data is array of objects: [{t: 0, S: 0.99, I: 0.01, R: 0}, ...]
  
  const traces = [
    {
      x: data.map(d => d.t),
      y: data.map(d => d.S),
      name: 'Susceptible',
      type: 'scatter',
      line: { color: '#3b82f6' }
    },
    {
      x: data.map(d => d.t),
      y: data.map(d => d.I),
      name: 'Infected',
      type: 'scatter',
      line: { color: '#ef4444' }
    },
    {
      x: data.map(d => d.t),
      y: data.map(d => d.R),
      name: 'Recovered',
      type: 'scatter',
      line: { color: '#10b981' }
    }
  ];
  
  Plotly.newPlot('graph', traces, {
    title: 'SIR Epidemic Model',
    xaxis: { title: 'Time (days)' },
    yaxis: { title: 'Population Fraction' }
  });
}
```

### Use Case 2: High-Quality Export with Full Resolution

**Goal:** After user finalizes parameters, generate high-quality plot and CSV for download.

```typescript
// User clicks "Export Results" button
exportButton.addEventListener('click', async () => {
  const result = await client.callTool({
    name: "simulate_model",
    arguments: {
      domain: "epidemiology",
      model_type: "SIR",
      parameters: { beta: 0.3, gamma: 0.1 },
      initial_conditions: { S: 0.99, I: 0.01, R: 0 },
      time_span: {
        start: 0,
        end: 160,
        steps: 1000,           // High resolution
        preview_mode: false    // ⚡ Full quality
      },
      return_data: true,
      save_artifacts: true     // ✅ Save files for download
    }
  });
  
  const simulation = JSON.parse(result.content[0].text);
  
  // Files are saved on server
  console.log('CSV:', simulation.artifacts[0].path);
  console.log('Plot:', simulation.artifacts[1].path);
  
  // Could download via additional endpoint or use data directly
});
```

---

## 📋 API Reference

### Request Parameters

#### New Fields in `time_span`:

```typescript
{
  time_span: {
    start: number,           // Start time
    end: number,            // End time
    steps: number,          // Number of data points (default: 400)
    preview_mode: boolean   // NEW: Limit to 100 points for speed (default: false)
  }
}
```

#### New Top-Level Fields:

```typescript
{
  return_data: boolean,     // NEW: Return actual data in response (default: true)
  save_artifacts: boolean   // NEW: Save CSV/plot files (default: true)
}
```

### Response Format

```typescript
{
  status: "success" | "error",
  message: string,
  summary: string,          // e.g., "Peak infection 0.3743 at t ≈ 33.89"
  metrics: {
    I_peak: number,         // Peak infection value
    t_peak: number          // Time of peak
  },
  columns: string[],        // ["t", "S", "I", "R"]
  
  // NEW: Actual data points!
  data: Array<{
    t: number,
    S: number,
    I: number,
    R: number
  }>,
  
  artifacts: Array<{
    kind: "csv" | "plot",
    path: string            // Server-side path (if save_artifacts=true)
  }>
}
```

---

## ⚡ Performance Modes

### Mode 1: Interactive Preview (Recommended for Sliders)
```json
{
  "time_span": {
    "preview_mode": true
  },
  "return_data": true,
  "save_artifacts": false
}
```
**Performance:** ~50-100ms response time
**Use for:** Real-time slider updates, live parameter exploration

### Mode 2: Full Resolution
```json
{
  "time_span": {
    "steps": 1000,
    "preview_mode": false
  },
  "return_data": true,
  "save_artifacts": true
}
```
**Performance:** ~200-500ms response time
**Use for:** Final results, exports, high-quality visualizations

### Mode 3: File-Only (Legacy)
```json
{
  "return_data": false,
  "save_artifacts": true
}
```
**Performance:** ~300ms response time
**Use for:** Batch processing, server-side analysis

---

## 🎨 Frontend Examples

### React + Plotly

```typescript
import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import { useMCPClient } from './hooks/useMCPClient';

function EpidemicCalculator() {
  const [beta, setBeta] = useState(0.3);
  const [gamma, setGamma] = useState(0.1);
  const [data, setData] = useState([]);
  const client = useMCPClient('https://your-server.onrender.com/mcp');
  
  useEffect(() => {
    const runSimulation = async () => {
      const result = await client.callTool({
        name: "simulate_model",
        arguments: {
          domain: "epidemiology",
          model_type: "SIR",
          parameters: { beta, gamma },
          initial_conditions: { S: 0.99, I: 0.01, R: 0 },
          time_span: {
            start: 0,
            end: 160,
            steps: 600,
            preview_mode: true
          },
          return_data: true,
          save_artifacts: false
        }
      });
      
      const sim = JSON.parse(result.content[0].text);
      setData(sim.data);
    };
    
    runSimulation();
  }, [beta, gamma]);
  
  return (
    <div>
      <div>
        <label>Transmission Rate (β): {beta}</label>
        <input 
          type="range" 
          min="0" 
          max="1" 
          step="0.01" 
          value={beta}
          onChange={(e) => setBeta(parseFloat(e.target.value))}
        />
      </div>
      
      <div>
        <label>Recovery Rate (γ): {gamma}</label>
        <input 
          type="range" 
          min="0" 
          max="1" 
          step="0.01" 
          value={gamma}
          onChange={(e) => setGamma(parseFloat(e.target.value))}
        />
      </div>
      
      <Plot
        data={[
          {
            x: data.map(d => d.t),
            y: data.map(d => d.S),
            name: 'Susceptible',
            type: 'scatter'
          },
          {
            x: data.map(d => d.t),
            y: data.map(d => d.I),
            name: 'Infected',
            type: 'scatter'
          },
          {
            x: data.map(d => d.t),
            y: data.map(d => d.R),
            name: 'Recovered',
            type: 'scatter'
          }
        ]}
        layout={{
          title: 'SIR Epidemic Model',
          xaxis: { title: 'Time (days)' },
          yaxis: { title: 'Population Fraction' }
        }}
      />
    </div>
  );
}
```

### Vue 3 + Chart.js

```vue
<template>
  <div class="epidemic-calculator">
    <div class="controls">
      <label>
        Transmission Rate (β): {{ beta }}
        <input v-model.number="beta" type="range" min="0" max="1" step="0.01" />
      </label>
      
      <label>
        Recovery Rate (γ): {{ gamma }}
        <input v-model.number="gamma" type="range" min="0" max="1" step="0.01" />
      </label>
    </div>
    
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { Chart } from 'chart.js/auto';
import { useMCPClient } from './composables/useMCPClient';

const beta = ref(0.3);
const gamma = ref(0.1);
const chartCanvas = ref(null);
let chart = null;

const client = useMCPClient('https://your-server.onrender.com/mcp');

async function runSimulation() {
  const result = await client.callTool({
    name: "simulate_model",
    arguments: {
      domain: "epidemiology",
      model_type: "SIR",
      parameters: { beta: beta.value, gamma: gamma.value },
      initial_conditions: { S: 0.99, I: 0.01, R: 0 },
      time_span: {
        start: 0,
        end: 160,
        steps: 600,
        preview_mode: true
      },
      return_data: true,
      save_artifacts: false
    }
  });
  
  const sim = JSON.parse(result.content[0].text);
  updateChart(sim.data);
}

function updateChart(data) {
  if (!chart) {
    chart = new Chart(chartCanvas.value, {
      type: 'line',
      data: {
        labels: data.map(d => d.t),
        datasets: [
          {
            label: 'Susceptible',
            data: data.map(d => d.S),
            borderColor: '#3b82f6'
          },
          {
            label: 'Infected',
            data: data.map(d => d.I),
            borderColor: '#ef4444'
          },
          {
            label: 'Recovered',
            data: data.map(d => d.R),
            borderColor: '#10b981'
          }
        ]
      }
    });
  } else {
    chart.data.labels = data.map(d => d.t);
    chart.data.datasets[0].data = data.map(d => d.S);
    chart.data.datasets[1].data = data.map(d => d.I);
    chart.data.datasets[2].data = data.map(d => d.R);
    chart.update();
  }
}

watch([beta, gamma], runSimulation);
onMounted(runSimulation);
</script>
```

---

## 🚀 Testing the New Features

### Test with curl:

```bash
curl -X POST https://your-server.onrender.com/mcp \
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
        "parameters": { "beta": 0.3, "gamma": 0.1 },
        "initial_conditions": { "S": 0.99, "I": 0.01, "R": 0 },
        "time_span": {
          "start": 0,
          "end": 160,
          "steps": 600,
          "preview_mode": true
        },
        "return_data": true,
        "save_artifacts": false
      }
    }
  }'
```

### Expected Response:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "status": "success",
    "message": "Simulation completed",
    "summary": "Peak infection 0.3743 at t ≈ 33.89",
    "metrics": {
      "I_peak": 0.3743,
      "t_peak": 33.89
    },
    "columns": ["t", "S", "I", "R"],
    "data": [
      { "t": 0, "S": 0.99, "I": 0.01, "R": 0 },
      { "t": 0.267, "S": 0.9892, "I": 0.0108, "R": 0.0000 },
      ...
    ],
    "artifacts": []
  }
}
```

---

## 📈 Performance Benchmarks

| Mode | Steps | Preview | Artifacts | Response Time |
|------|-------|---------|-----------|---------------|
| Interactive | 600 | ✅ Yes | ❌ No | ~50-100ms |
| Standard | 600 | ❌ No | ❌ No | ~150-200ms |
| Full | 1000 | ❌ No | ✅ Yes | ~300-500ms |

**Note:** Times measured on Render Starter tier (0.5 CPU, 512 MB RAM)

---

## 🎯 Best Practices

### 1. **Use Preview Mode for Sliders**
```typescript
// ✅ Good: Fast updates
time_span: { preview_mode: true, steps: 600 }

// ❌ Bad: Slow updates
time_span: { preview_mode: false, steps: 1000 }
```

### 2. **Debounce Rapid Inputs**
```typescript
import { debounce } from 'lodash';

const runSimulation = debounce(async (beta, gamma) => {
  // Call server
}, 300); // Wait 300ms after last input

betaSlider.addEventListener('input', (e) => {
  runSimulation(e.target.value, gamma);
});
```

### 3. **Show Loading States**
```typescript
const [loading, setLoading] = useState(false);

const runSimulation = async () => {
  setLoading(true);
  try {
    const result = await client.callTool(...);
    updateGraph(result.data);
  } finally {
    setLoading(false);
  }
};
```

### 4. **Cache Static Results**
```typescript
const cache = new Map();

const runSimulation = async (beta, gamma) => {
  const key = `${beta}-${gamma}`;
  if (cache.has(key)) {
    return cache.get(key);
  }
  
  const result = await client.callTool(...);
  cache.set(key, result);
  return result;
};
```

---

## 🔧 Troubleshooting

### Issue: Slow Response Times
**Solution:** Enable preview mode and disable artifacts:
```json
{
  "time_span": { "preview_mode": true },
  "save_artifacts": false
}
```

### Issue: Data Not Returning
**Solution:** Ensure `return_data` is set to `true`:
```json
{
  "return_data": true
}
```

### Issue: Too Much Data for Frontend
**Solution:** Reduce steps or enable preview mode:
```json
{
  "time_span": { "steps": 200, "preview_mode": true }
}
```

---

## 📚 Next Steps

1. **Deploy your server** to Render following DEPLOYMENT.md
2. **Build your frontend** using the examples above
3. **Test with different parameters** to find optimal performance
4. **Add more models** (Lotka-Volterra, Logistic, etc.) as needed

Happy building! 🚀



