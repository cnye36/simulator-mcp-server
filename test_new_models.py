#!/usr/bin/env python3
"""
Test script for new Projectile and Monte Carlo simulation models
"""
import json
from models.projectile import simulate_projectile
from models.monte_carlo import simulate_monte_carlo

def test_projectile():
    """Test the projectile motion simulation"""
    print("=" * 80)
    print("Testing Projectile Simulation")
    print("=" * 80)

    parameters = {
        "g": 9.81,      # gravity
        "v0": 20.0,     # initial velocity 20 m/s
        "angle": 45.0   # launch angle 45 degrees
    }

    initial_conditions = {
        "x": 0.0,   # starting horizontal position
        "y": 0.0,   # starting height
        "vx": 0.0,  # will be calculated from v0 and angle (0 means use calculated)
        "vy": 0.0   # will be calculated from v0 and angle (0 means use calculated)
    }

    tspan = (0.0, 5.0)  # simulate for 5 seconds
    steps = 100

    try:
        t, Y, metrics = simulate_projectile(parameters, initial_conditions, tspan, steps)

        print(f"✅ Simulation successful!")
        print(f"   Time points: {len(t)}")
        print(f"   State variables: {Y.shape[0]} (x, y, vx, vy)")
        print(f"   Output shape: {Y.shape}")
        print(f"\nMetrics:")
        for key, value in metrics.items():
            if key != "summary":
                print(f"   {key}: {value}")
        print(f"\nSummary: {metrics['summary']}")
        print()
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_monte_carlo():
    """Test the Monte Carlo simulation"""
    print("=" * 80)
    print("Testing Monte Carlo Simulation")
    print("=" * 80)

    parameters = {
        "mu": 0.1,       # 10% annual drift
        "sigma": 0.2,    # 20% annual volatility
        "n_paths": 1000, # run 1000 paths
        "seed": 42       # for reproducibility
    }

    initial_conditions = {
        "S": 100.0  # starting asset price
    }

    tspan = (0.0, 1.0)  # simulate for 1 year
    steps = 252  # trading days in a year

    try:
        t, Y, metrics = simulate_monte_carlo(parameters, initial_conditions, tspan, steps)

        print(f"✅ Simulation successful!")
        print(f"   Time points: {len(t)}")
        print(f"   State variables: {Y.shape[0]} (S_mean)")
        print(f"   Output shape: {Y.shape}")
        print(f"\nMetrics:")
        for key, value in metrics.items():
            if key not in ["summary", "percentiles"]:
                print(f"   {key}: {value}")
        print(f"\nSummary: {metrics['summary']}")

        # Check percentiles were calculated
        if "percentiles" in metrics:
            print(f"\n✅ Percentile data available (p5, p25, p75, p95)")

        print()
        return True
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n🧪 Testing New Simulation Models\n")

    projectile_ok = test_projectile()
    monte_carlo_ok = test_monte_carlo()

    print("=" * 80)
    print("Test Results")
    print("=" * 80)
    print(f"Projectile:   {'✅ PASS' if projectile_ok else '❌ FAIL'}")
    print(f"Monte Carlo:  {'✅ PASS' if monte_carlo_ok else '❌ FAIL'}")
    print()

    if projectile_ok and monte_carlo_ok:
        print("🎉 All tests passed!")
        exit(0)
    else:
        print("❌ Some tests failed")
        exit(1)
