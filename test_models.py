#!/usr/bin/env python3
"""Quick test script for new simulation models"""

from models.lotka_volterra import simulate_lotka_volterra
from models.logistic import simulate_logistic

def test_lotka_volterra():
    """Test Lotka-Volterra model"""
    print("Testing Lotka-Volterra model...")
    parameters = {"alpha": 1.0, "beta": 0.1, "delta": 0.075, "gamma": 1.5}
    initial_conditions = {"x": 10.0, "y": 5.0}
    tspan = (0.0, 100.0)
    steps = 200

    t, Y, metrics = simulate_lotka_volterra(parameters, initial_conditions, tspan, steps)

    print(f"  ✓ Shape: t={len(t)}, Y={Y.shape}")
    print(f"  ✓ Metrics: {metrics['summary']}")
    print(f"  ✓ Prey range: {metrics['x_min']:.2f} - {metrics['x_max']:.2f}")
    print(f"  ✓ Predator range: {metrics['y_min']:.2f} - {metrics['y_max']:.2f}")
    print()

def test_logistic():
    """Test Logistic growth model"""
    print("Testing Logistic growth model...")
    parameters = {"r": 0.5, "K": 100.0}
    initial_conditions = {"P": 10.0}
    tspan = (0.0, 50.0)
    steps = 200

    t, Y, metrics = simulate_logistic(parameters, initial_conditions, tspan, steps)

    print(f"  ✓ Shape: t={len(t)}, Y={Y.shape}")
    print(f"  ✓ Metrics: {metrics['summary']}")
    print(f"  ✓ Initial population: {metrics['P_initial']:.2f}")
    print(f"  ✓ Final population: {metrics['P_final']:.2f}")
    print(f"  ✓ Carrying capacity: {metrics['K']:.2f}")
    print()

if __name__ == "__main__":
    print("="*60)
    print("Testing New Simulation Models")
    print("="*60)
    print()

    try:
        test_lotka_volterra()
        test_logistic()
        print("="*60)
        print("✅ All tests passed!")
        print("="*60)
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
