# models/lotka_volterra.py
from __future__ import annotations
import numpy as np
from typing import Dict, Tuple
from scipy.integrate import solve_ivp

def simulate_lotka_volterra(
    parameters: Dict[str, float],
    y0: Dict[str, float],
    tspan: Tuple[float, float],
    steps: int,
    method: str = "RK45"
):
    """
    Lotka-Volterra predator-prey model.

    Parameters:
        alpha: Prey growth rate
        beta: Predation rate
        delta: Predator growth rate from prey consumption
        gamma: Predator death rate

    State variables:
        x: Prey population
        y: Predator population

    Equations:
        dx/dt = alpha*x - beta*x*y
        dy/dt = delta*x*y - gamma*y
    """
    alpha = float(parameters.get("alpha", 1.0))
    beta = float(parameters.get("beta", 0.1))
    delta = float(parameters.get("delta", 0.075))
    gamma = float(parameters.get("gamma", 1.5))

    x0 = float(y0.get("x", 10.0))  # prey
    y0_val = float(y0.get("y", 5.0))  # predator
    y0_vec = np.array([x0, y0_val], dtype=float)

    def lv_rhs(t, y):
        x, y_pred = y
        dx = alpha * x - beta * x * y_pred
        dy = delta * x * y_pred - gamma * y_pred
        return [dx, dy]

    t_eval = np.linspace(tspan[0], tspan[1], steps)
    sol = solve_ivp(lv_rhs, t_span=tspan, y0=y0_vec, method=method, t_eval=t_eval, rtol=1e-6, atol=1e-9)
    if not sol.success:
        raise RuntimeError(sol.message)

    # Calculate metrics
    x_vals = sol.y[0, :]
    y_vals = sol.y[1, :]

    x_max = float(x_vals.max())
    x_min = float(x_vals.min())
    y_max = float(y_vals.max())
    y_min = float(y_vals.min())

    x_mean = float(x_vals.mean())
    y_mean = float(y_vals.mean())

    metrics = {
        "x_max": x_max,
        "x_min": x_min,
        "x_mean": x_mean,
        "y_max": y_max,
        "y_min": y_min,
        "y_mean": y_mean,
        "summary": f"Prey: {x_min:.2f}-{x_max:.2f} (avg {x_mean:.2f}), Predator: {y_min:.2f}-{y_max:.2f} (avg {y_mean:.2f})"
    }

    # shape Y as (state, time)
    return sol.t, sol.y, metrics
