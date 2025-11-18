# models/logistic.py
from __future__ import annotations
import numpy as np
from typing import Dict, Tuple
from scipy.integrate import solve_ivp

def simulate_logistic(
    parameters: Dict[str, float],
    y0: Dict[str, float],
    tspan: Tuple[float, float],
    steps: int,
    method: str = "RK45"
):
    """
    Logistic population growth model.

    Parameters:
        r: Growth rate
        K: Carrying capacity

    State variables:
        P: Population

    Equation:
        dP/dt = r*P*(1 - P/K)
    """
    r = float(parameters.get("r", 0.5))
    K = float(parameters.get("K", 100.0))

    P0 = float(y0.get("P", 10.0))
    y0_vec = np.array([P0], dtype=float)

    def logistic_rhs(t, y):
        P = y[0]
        dP = r * P * (1 - P / K)
        return [dP]

    t_eval = np.linspace(tspan[0], tspan[1], steps)
    sol = solve_ivp(logistic_rhs, t_span=tspan, y0=y0_vec, method=method, t_eval=t_eval, rtol=1e-6, atol=1e-9)
    if not sol.success:
        raise RuntimeError(sol.message)

    # Calculate metrics
    P_vals = sol.y[0, :]

    P_initial = float(P_vals[0])
    P_final = float(P_vals[-1])
    P_max = float(P_vals.max())

    # Find time to reach 50% of carrying capacity
    halfway_point = K * 0.5
    idx_halfway = np.argmin(np.abs(P_vals - halfway_point))
    t_halfway = float(sol.t[idx_halfway])

    # Find time to reach 90% of carrying capacity
    ninety_percent = K * 0.9
    idx_ninety = np.argmin(np.abs(P_vals - ninety_percent))
    t_ninety = float(sol.t[idx_ninety])

    metrics = {
        "P_initial": P_initial,
        "P_final": P_final,
        "P_max": P_max,
        "K": K,
        "t_halfway": t_halfway,
        "t_ninety": t_ninety,
        "summary": f"Population grows from {P_initial:.2f} to {P_final:.2f} (K={K:.2f}), reaching 90% at t ≈ {t_ninety:.2f}"
    }

    # shape Y as (state, time)
    return sol.t, sol.y, metrics
