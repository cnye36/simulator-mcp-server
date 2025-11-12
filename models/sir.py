# models/sir.py
from __future__ import annotations
import numpy as np
from typing import Dict, Tuple
from scipy.integrate import solve_ivp

def simulate_sir(
    parameters: Dict[str, float],
    y0: Dict[str, float],
    tspan: Tuple[float, float],
    steps: int,
    method: str = "RK45"
):
    beta = float(parameters.get("beta", 0.3))
    gamma = float(parameters.get("gamma", 0.1))

    S0 = float(y0.get("S", 0.99))
    I0 = float(y0.get("I", 0.01))
    R0 = float(y0.get("R", 0.0))
    y0_vec = np.array([S0, I0, R0], dtype=float)

    def sir_rhs(t, y):
        S, I, R = y
        dS = -beta * S * I
        dI = beta * S * I - gamma * I
        dR = gamma * I
        return [dS, dI, dR]

    t_eval = np.linspace(tspan[0], tspan[1], steps)
    sol = solve_ivp(sir_rhs, t_span=tspan, y0=y0_vec, method=method, t_eval=t_eval, rtol=1e-6, atol=1e-9)
    if not sol.success:
        raise RuntimeError(sol.message)

    # Basic metrics
    I_peak = float(sol.y[1, :].max())
    t_peak = float(sol.t[sol.y[1, :].argmax()])
    metrics = {
        "I_peak": I_peak,
        "t_peak": t_peak,
        "summary": f"Peak infection {I_peak:.4f} at t ≈ {t_peak:.2f}"
    }

    # shape Y as (state, time)
    return sol.t, sol.y, metrics
