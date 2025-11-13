#!/bin/bash

# Test script for MCP server
# Usage: ./test_mcp.sh

SERVER_URL="https://simulator-mcp-server.onrender.com/mcp"

echo "🧪 Testing MCP Server..."
echo ""

# Test 1: List available tools
echo "1️⃣ Testing tools/list..."
curl -s -X POST "$SERVER_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list"
  }'

echo ""
echo ""

# Test 2: Call simulate_model tool
echo "2️⃣ Testing simulate_model tool..."
curl -s -X POST "$SERVER_URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "simulate_model",
      "arguments": {
        "spec": {
          "domain": "epidemiology",
          "model_type": "SIR",
          "parameters": {
            "beta": 0.3,
            "gamma": 0.1
          },
          "initial_conditions": {
            "S": 0.99,
            "I": 0.01,
            "R": 0
          },
          "time_span": {
            "start": 0,
            "end": 160,
            "steps": 100,
            "preview_mode": true
          },
          "method": "RK45",
          "return_data": true,
          "save_artifacts": false
        }
      }
    }
  }'

echo ""
echo "✅ Tests complete!"

