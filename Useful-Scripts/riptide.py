#%%
import numpy as np

def compute_cost_and_width(periods, T=600, duty_cycle=0.1):
    """
    Compute pulse width at 10% duty cycle and relative computational cost.

    Parameters:
    -----------
    periods : array-like
        Period(s) in milliseconds.
    T : float
        Observation time in seconds. Default: 600 (10 minutes).
    duty_cycle : float
        Duty cycle as fraction (e.g., 0.1 for 10%). Default: 0.1

    Returns:
    --------
    result : list of dicts
        Each dict contains period_ms, pulse_width_ms, cost
    """
    results = []
    for P_ms in periods:
        P_s = P_ms / 1000
        nu0 = 1 / P_s
        b = int(1 / duty_cycle)  # number of phase bins
        width_ms = P_ms * duty_cycle

        # Asymptotic computational cost (arbitrary units)
        x = T * nu0 * b
        cost = x * (np.log2(x) if x > 0 else 0)

        results.append({
            'period_ms': P_ms,
            'pulse_width_ms': width_ms,
            'cost': cost
        })
    return results

# Run for 1, 10, 100, 1000, 10000 ms
periods_ms = [1, 10, 100, 1000, 10000]
results = compute_cost_and_width(periods_ms)

for res in results:
    print(f"Period: {res['period_ms']:>6} ms | Pulse width: {res['pulse_width_ms']:>7.2f} ms | Computation: {res['cost']:>12.2e}")
