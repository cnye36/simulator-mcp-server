# models/monte_carlo.py
from __future__ import annotations
import numpy as np
from typing import Dict, Tuple

def simulate_monte_carlo(
    parameters: Dict[str, float],
    y0: Dict[str, float],
    tspan: Tuple[float, float],
    steps: int,
    method: str = "RK45"  # Not used for Monte Carlo, but kept for API consistency
):
    """
    Monte Carlo simulation for geometric Brownian motion (e.g., stock price modeling).

    Parameters:
        mu: Drift rate (expected return, annualized)
        sigma: Volatility (standard deviation, annualized)
        n_paths: Number of simulation paths to run (default: 100)
        seed: Random seed for reproducibility (optional)

    State variables:
        S: Asset price / value

    Model:
        dS = mu * S * dt + sigma * S * dW
        where dW is a Wiener process (random walk)

    Returns average across all paths for visualization.
    """
    mu = float(parameters.get("mu", 0.1))  # drift (10% annual return)
    sigma = float(parameters.get("sigma", 0.2))  # volatility (20% annual)
    n_paths = int(parameters.get("n_paths", 100))  # number of Monte Carlo paths
    seed = parameters.get("seed", None)  # optional random seed

    # Initial conditions
    S0 = float(y0.get("S", 100.0))  # initial asset price

    # Set random seed if provided
    if seed is not None:
        np.random.seed(int(seed))

    # Create time grid
    t = np.linspace(tspan[0], tspan[1], steps)
    dt = (tspan[1] - tspan[0]) / (steps - 1) if steps > 1 else 0.0

    # Generate random paths
    # Each path is a geometric Brownian motion
    paths = np.zeros((n_paths, steps))
    paths[:, 0] = S0

    for i in range(1, steps):
        # Generate random normal increments for all paths
        dW = np.random.normal(0, np.sqrt(dt), n_paths)

        # Update each path using geometric Brownian motion
        # S(t+dt) = S(t) * exp((mu - 0.5*sigma^2)*dt + sigma*dW)
        paths[:, i] = paths[:, i-1] * np.exp(
            (mu - 0.5 * sigma**2) * dt + sigma * dW
        )

    # Calculate statistics across all paths at each time point
    S_mean = np.mean(paths, axis=0)  # mean path
    S_median = np.median(paths, axis=0)  # median path
    S_std = np.std(paths, axis=0)  # standard deviation
    S_min = np.min(paths, axis=0)  # minimum value
    S_max = np.max(paths, axis=0)  # maximum value

    # Percentiles
    S_p5 = np.percentile(paths, 5, axis=0)   # 5th percentile
    S_p25 = np.percentile(paths, 25, axis=0)  # 25th percentile
    S_p75 = np.percentile(paths, 75, axis=0)  # 75th percentile
    S_p95 = np.percentile(paths, 95, axis=0)  # 95th percentile

    # Calculate metrics
    final_mean = float(S_mean[-1])
    final_median = float(S_median[-1])
    final_std = float(S_std[-1])
    final_min = float(S_min[-1])
    final_max = float(S_max[-1])

    # Expected return and realized return
    expected_return = (final_mean - S0) / S0 * 100  # percentage
    max_return = (final_max - S0) / S0 * 100
    min_return = (final_min - S0) / S0 * 100

    # Probability of profit (final price > initial price)
    prob_profit = np.mean(paths[:, -1] > S0) * 100  # percentage

    metrics = {
        "S_initial": S0,
        "S_final_mean": final_mean,
        "S_final_median": final_median,
        "S_final_std": final_std,
        "S_final_min": final_min,
        "S_final_max": final_max,
        "expected_return_pct": float(expected_return),
        "max_return_pct": float(max_return),
        "min_return_pct": float(min_return),
        "prob_profit_pct": float(prob_profit),
        "n_paths": n_paths,
        "mu": mu,
        "sigma": sigma,
        "summary": f"Monte Carlo ({n_paths} paths): Mean final price {final_mean:.2f} (return {expected_return:.1f}%), probability of profit {prob_profit:.1f}%"
    }

    # Return data in the expected format
    # We return the mean path as the primary state variable
    # Other statistics are available in metrics and can be accessed separately
    # Shape: (state_variables, time_points)
    Y = np.array([S_mean])  # Return mean path as primary state variable

    # Store percentile data in metrics for reference
    metrics["percentiles"] = {
        "p5": S_p5.tolist(),
        "p25": S_p25.tolist(),
        "p75": S_p75.tolist(),
        "p95": S_p95.tolist(),
    }

    return t, Y, metrics
