# server.py
from __future__ import annotations
from pathlib import Path
from datetime import datetime
from typing import Literal, Optional, Dict, List, Tuple

import json
import os
import uuid
import logging
import numpy as np
from pydantic import BaseModel, Field, field_validator
from jsonschema import validate as json_validate, ValidationError as JSONSchemaError

from mcp.server.fastmcp import FastMCP, Context
from mcp.types import CallToolResult, TextContent
from starlette.responses import JSONResponse

# --- Configure Logging ---
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("simulation-mcp")

# --- storage paths ---
BASE = Path(__file__).parent
# Use environment variable for storage path, fallback to local
STORAGE_PATH = os.getenv("STORAGE_PATH", str(BASE / "storage"))
OUT_DIR = Path(STORAGE_PATH)
OUT_DIR.mkdir(exist_ok=True, parents=True)

# --- Input/Output models (become tool schemas automatically) ---

class TimeSpan(BaseModel):
    start: float = Field(..., description="Start time")
    end: float = Field(..., description="End time")
    steps: int = Field(400, description="Number of points in t-grid (>= 2)")
    preview_mode: bool = Field(
        default=False,
        description="When true, limit steps to 100 for faster preview rendering"
    )

    @field_validator("steps")
    @classmethod
    def _min_steps(cls, v: int) -> int:
        if v < 2:
            raise ValueError("steps must be >= 2")
        return v

class SimulateModelInput(BaseModel):
    domain: Literal["epidemiology","physics","finance","custom"] = "epidemiology"
    model_type: Literal["SIR","LotkaVolterra","Logistic","Projectile","MonteCarlo"] = "SIR"
    parameters: Dict[str, float] = Field(..., description="Model parameters")
    initial_conditions: Dict[str, float] = Field(..., description="State variable initial values")
    time_span: TimeSpan = Field(..., description="Time grid definition")
    method: Literal["RK45","RK23","DOP853"] = "RK45"
    sensitivity: Optional[Dict[str, float]] = Field(
        default=None,
        description="Optional +/- perturbations for one-way sensitivity, e.g. {'beta':0.05}"
    )
    tags: Optional[List[str]] = None
    return_data: bool = Field(
        default=True,
        description="Return actual data points in response (recommended for interactive UIs)"
    )
    save_artifacts: bool = Field(
        default=False,
        description="Save CSV and plot files to disk. Default False for stateless operation. Chat apps should handle persistence via their own storage (e.g., Supabase)."
    )

class Artifact(BaseModel):
    kind: Literal["plot","csv","json"]
    path: str
    sha256: Optional[str] = None

class SimulateModelOutput(BaseModel):
    status: Literal["success","error"]
    message: str
    summary: Optional[str] = None
    artifacts: List[Artifact] = []
    metrics: Dict[str, float] = {}
    columns: Optional[List[str]] = None
    data: Optional[List[Dict[str, float]]] = Field(
        default=None,
        description="Time series data points for interactive visualization"
    )

# --- JSON Schema (extra belt-and-suspenders validation) ---
SCHEMA_PATH = BASE / "schemas" / "simulate_model_input.json"
if SCHEMA_PATH.exists():
    INPUT_SCHEMA = json.loads(SCHEMA_PATH.read_text())
else:
    INPUT_SCHEMA = None  # optional; Pydantic already validates

# --- Solver registry ---
from models.sir import simulate_sir
from models.lotka_volterra import simulate_lotka_volterra
from models.logistic import simulate_logistic
from models.projectile import simulate_projectile
from models.monte_carlo import simulate_monte_carlo

SolverResult = Tuple[np.ndarray, np.ndarray, Dict[str, float]]  # t, Y, metrics

SOLVERS = {
    ("epidemiology","SIR"): simulate_sir,
    ("epidemiology","LotkaVolterra"): simulate_lotka_volterra,
    ("epidemiology","Logistic"): simulate_logistic,
    ("physics","Projectile"): simulate_projectile,
    ("finance","MonteCarlo"): simulate_monte_carlo,
}

# --- Utility: write CSV & plot ---
def write_csv(t: np.ndarray, Y: np.ndarray, headers: List[str], run_id: str) -> Path:
    import csv
    csv_path = OUT_DIR / f"{run_id}.csv"
    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["t", *headers])
        for i in range(len(t)):
            writer.writerow([float(t[i]), *[float(v) for v in Y[:, i]]])
    return csv_path

def write_plot(t: np.ndarray, Y: np.ndarray, headers: List[str], run_id: str) -> Path:
    import matplotlib.pyplot as plt  # runtime import to keep import cost low
    fig = plt.figure()
    for idx, name in enumerate(headers):
        plt.plot(t, Y[idx, :], label=name)
    plt.legend()
    plt.xlabel("t")
    plt.ylabel("state")
    plt.title(f"Simulation {run_id}")
    png_path = OUT_DIR / f"{run_id}.png"
    fig.savefig(png_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return png_path

# --- Build server ---

mcp = FastMCP(
    "Simulation MCP",
    host=os.getenv("FASTMCP_HOST", "0.0.0.0"),  # Explicitly bind to 0.0.0.0 for production
    port=int(os.getenv("PORT", "8000")),
    stateless_http=True  # Enable stateless mode - no session management needed
)

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint for deployment platforms"""
    logger.info("Health check requested")
    return JSONResponse({
        "status": "healthy",
        "service": "simulation-mcp",
        "version": "0.1.0",
        "storage": str(OUT_DIR),
        "solvers": len(SOLVERS)
    })

@mcp.tool()
def simulate_model(spec: SimulateModelInput, ctx: Context | None = None) -> CallToolResult:
    """
    Run a simulation described by a structured JSON spec and return artifacts + metrics.
    
    Features:
    - Returns actual data points for interactive visualization (set return_data=True)
    - Preview mode for faster rendering with fewer data points (set time_span.preview_mode=True)
    - Optional artifact saving (set save_artifacts=False for faster response)
    """
    run_id = f"{spec.model_type.lower()}_{datetime.utcnow().strftime('%Y%m%dT%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    logger.info("="*80)
    logger.info(f"📊 New simulation request received - Run ID: {run_id}")
    logger.info(f"   Domain: {spec.domain}")
    logger.info(f"   Model: {spec.model_type}")
    logger.info(f"   Parameters: {spec.parameters}")
    logger.info(f"   Initial conditions: {spec.initial_conditions}")
    logger.info(f"   Time span: start={spec.time_span.start}, end={spec.time_span.end}, steps={spec.time_span.steps}")
    logger.info(f"   Preview mode: {spec.time_span.preview_mode}")
    logger.info(f"   Return data: {spec.return_data}")
    logger.info(f"   Save artifacts: {spec.save_artifacts}")
    logger.info(f"   Method: {spec.method}")
    
    # Optional JSON Schema pass (in addition to Pydantic)
    if INPUT_SCHEMA is not None:
        try:
            logger.debug("Validating against JSON schema...")
            json_validate(instance=json.loads(spec.model_dump_json()), schema=INPUT_SCHEMA)
            logger.debug("✅ JSON schema validation passed")
        except JSONSchemaError as e:
            logger.error(f"❌ JSON schema validation failed: {e.message}")
            return CallToolResult(
                content=[TextContent(type="text", text=f"JSON schema validation failed: {e.message}")],
                isError=True
            )

    key = (spec.domain, spec.model_type)
    if key not in SOLVERS:
        logger.error(f"❌ No solver registered for domain={spec.domain}, model_type={spec.model_type}")
        logger.info(f"   Available solvers: {list(SOLVERS.keys())}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"No solver registered for domain={spec.domain}, model_type={spec.model_type}")],
            isError=True
        )

    # Apply preview mode: limit steps for faster rendering
    actual_steps = spec.time_span.steps
    if spec.time_span.preview_mode:
        actual_steps = min(spec.time_span.steps, 100)
        logger.info(f"⚡ Preview mode enabled: reducing steps from {spec.time_span.steps} to {actual_steps}")

    try:
        logger.info(f"🔄 Running solver: {spec.model_type} with {actual_steps} steps...")
        start_time = datetime.utcnow()
        
        t, Y, metrics = SOLVERS[key](
            parameters=spec.parameters,
            y0=spec.initial_conditions,
            tspan=(spec.time_span.start, spec.time_span.end),
            steps=actual_steps,
            method=spec.method
        )
        
        elapsed = (datetime.utcnow() - start_time).total_seconds()
        logger.info(f"✅ Solver completed in {elapsed:.3f} seconds")
        logger.info(f"   Output shape: t={len(t)} points, Y={Y.shape}")
        logger.info(f"   Metrics: {metrics}")
        
    except Exception as e:
        logger.error(f"❌ Solver error: {type(e).__name__}: {str(e)}")
        logger.exception("Full traceback:")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Solver error: {type(e).__name__}: {str(e)}")],
            isError=True
        )

    headers = list(spec.initial_conditions.keys())
    
    # Optionally save artifacts (can skip for faster response in interactive mode)
    artifacts = []
    if spec.save_artifacts:
        logger.info("💾 Saving artifacts...")
        try:
            csv_path = write_csv(t, Y, headers, run_id)
            logger.info(f"   ✅ CSV saved: {csv_path}")
            
            png_path = write_plot(t, Y, headers, run_id)
            logger.info(f"   ✅ Plot saved: {png_path}")
            
            artifacts = [
                Artifact(kind="csv", path=str(csv_path)),
                Artifact(kind="plot", path=str(png_path))
            ]
        except Exception as e:
            logger.error(f"   ❌ Failed to save artifacts: {e}")
    else:
        logger.info("⏭️  Skipping artifact saving (save_artifacts=False)")

    # Convert numpy arrays to JSON-serializable list of dicts
    data_points = None
    if spec.return_data:
        logger.info(f"📦 Converting {len(t)} data points to JSON format...")
        try:
            data_points = []
            for i in range(len(t)):
                point = {"t": float(t[i])}
                for idx, header in enumerate(headers):
                    point[header] = float(Y[idx, i])
                data_points.append(point)
            logger.info(f"   ✅ Data conversion complete ({len(data_points)} points)")
        except Exception as e:
            logger.error(f"   ❌ Data conversion failed: {e}")
    else:
        logger.info("⏭️  Skipping data return (return_data=False)")

    summary = metrics.get("summary", "")
    output = SimulateModelOutput(
        status="success",
        message="Simulation completed",
        summary=summary,
        artifacts=artifacts,
        metrics={k: float(v) for k, v in metrics.items() if k != "summary"},
        columns=["t", *headers],
        data=data_points
    )

    logger.info(f"✨ Simulation {run_id} completed successfully")
    logger.info(f"   Response size: ~{len(output.model_dump_json())} bytes")
    logger.info("="*80)

    # Return both human-readable text and a structured payload
    return CallToolResult(
        content=[TextContent(type="text", text=output.model_dump_json(indent=2))],
        _meta={"result": output.model_dump(mode="json")}
    )

if __name__ == "__main__":
    # Support multiple transport modes via environment variable
    # Default to stdio for local dev, streamable-http for production
    transport = os.getenv("MCP_TRANSPORT", "stdio")
    
    logger.info("="*80)
    logger.info("🚀 Starting Simulation MCP Server")
    logger.info("   Version: 0.1.0")
    logger.info(f"   Transport: {transport}")
    logger.info(f"   Storage: {OUT_DIR} (temporary, stateless operation)")
    logger.info(f"   Registered solvers: {list(SOLVERS.keys())}")
    logger.info(f"   Log level: {os.getenv('LOG_LEVEL', 'INFO')}")
    logger.info("   ⚠️  Stateless mode: No authentication required")
    logger.info("   ⚠️  Chat apps should handle persistence via their own storage")
    logger.info("="*80)
    
    if transport == "streamable-http" or transport == "http":
        # Production mode: HTTP transport (MCP standard)
        host = os.getenv("FASTMCP_HOST", "127.0.0.1")
        port = os.getenv("PORT", "8000")
        logger.info("🌐 Running in HTTP mode (streamable-http)")
        logger.info(f"   Binding to: {host}:{port}")
        logger.info("   Set FASTMCP_HOST=0.0.0.0 for external access")
        mcp.run(transport="streamable-http")
    elif transport == "sse":
        # Deprecated SSE mode (kept for backwards compatibility)
        logger.warning("⚠️  Running in deprecated SSE mode")
        mcp.run(transport="sse", mount_path="/mcp")
    else:
        # Development mode: stdio transport
        # Usage: `uv run mcp dev server.py` or `python server.py`
        logger.info("💻 Running in stdio mode (local development)")
        mcp.run()
