# models/projectile.py
from __future__ import annotations
import numpy as np
from typing import Dict, Tuple
from scipy.integrate import solve_ivp

def simulate_projectile(
    parameters: Dict[str, float],
    y0: Dict[str, float],
    tspan: Tuple[float, float],
    steps: int,
    method: str = "RK45"
):
    """
    Projectile motion simulation with gravity.

    Parameters:
        g: Gravitational acceleration (default: 9.81 m/s^2)
        v0: Initial velocity magnitude (m/s)
        angle: Launch angle in degrees from horizontal

    State variables:
        x: Horizontal position (m)
        y: Vertical position (m)
        vx: Horizontal velocity (m/s)
        vy: Vertical velocity (m/s)

    Equations:
        dx/dt = vx
        dy/dt = vy
        dvx/dt = 0 (no air resistance)
        dvy/dt = -g
    """
    g = float(parameters.get("g", 9.81))  # gravitational acceleration
    v0 = float(parameters.get("v0", 20.0))  # initial velocity
    angle_deg = float(parameters.get("angle", 45.0))  # launch angle in degrees

    # Convert angle to radians
    angle_rad = np.deg2rad(angle_deg)

    # Calculate initial velocities from v0 and angle
    vx0_calc = v0 * np.cos(angle_rad)
    vy0_calc = v0 * np.sin(angle_rad)

    # Initial conditions
    x0 = float(y0.get("x", 0.0))
    y0_val = float(y0.get("y", 0.0))

    # Use calculated velocities if not explicitly provided or if provided as 0
    if "vx" in y0 and y0["vx"] != 0:
        vx0 = float(y0["vx"])
    else:
        vx0 = vx0_calc

    if "vy" in y0 and y0["vy"] != 0:
        vy0 = float(y0["vy"])
    else:
        vy0 = vy0_calc

    y0_vec = np.array([x0, y0_val, vx0, vy0], dtype=float)

    def projectile_rhs(t, y):
        x, y_pos, vx, vy = y
        dx = vx
        dy = vy
        dvx = 0.0  # no horizontal acceleration
        dvy = -g   # gravity
        return [dx, dy, dvx, dvy]

    t_eval = np.linspace(tspan[0], tspan[1], steps)
    sol = solve_ivp(projectile_rhs, t_span=tspan, y0=y0_vec, method=method, t_eval=t_eval, rtol=1e-6, atol=1e-9)
    if not sol.success:
        raise RuntimeError(sol.message)

    # Calculate metrics
    x_vals = sol.y[0, :]
    y_vals = sol.y[1, :]
    vx_vals = sol.y[2, :]
    vy_vals = sol.y[3, :]

    # Maximum height
    y_max = float(y_vals.max())
    t_max_height = float(sol.t[y_vals.argmax()])

    # Range (horizontal distance when y returns to initial height)
    # Find where projectile lands (y crosses initial height going down)
    initial_height = y0_val

    # Find the last time y crosses initial height
    landing_idx = len(y_vals) - 1
    for i in range(1, len(y_vals)):
        if y_vals[i] < initial_height and y_vals[i-1] >= initial_height:
            landing_idx = i

    range_val = float(x_vals[landing_idx])
    t_landing = float(sol.t[landing_idx])

    # Total velocity at any time
    v_total = np.sqrt(vx_vals**2 + vy_vals**2)
    v_max = float(v_total.max())
    v_final = float(v_total[landing_idx])

    metrics = {
        "max_height": y_max,
        "t_max_height": t_max_height,
        "range": range_val,
        "t_landing": t_landing,
        "v_initial": v0,
        "v_final": v_final,
        "v_max": v_max,
        "angle_deg": angle_deg,
        "summary": f"Projectile reaches max height {y_max:.2f}m at t ≈ {t_max_height:.2f}s, lands at x={range_val:.2f}m (t ≈ {t_landing:.2f}s)"
    }

    # shape Y as (state, time)
    return sol.t, sol.y, metrics
