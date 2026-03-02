import numpy as np
from scipy.optimize import minimize

def _smooth_abs(x: np.ndarray, eps: float) -> np.ndarray:
    return np.sqrt(x**2 + eps)

def optimise_schedule_objective2(
    renewable_forecast: np.ndarray,
    p_min: float,
    p_max: float,
    ramp_limit: float,
    efficiency: float,
    lambda_ramp: float,
    eps: float,
) -> dict:
    """
    Solve Objective 2:
    Minimise:  -sum(H(P_t)) + lambda * sum(|P_t - P_{t-1}|)
    Subject to bounds, renewable cap, ramp constraints.
    Returns dict with schedule + metadata.
    """
    renewable_forecast = np.asarray(renewable_forecast)
    T = len(renewable_forecast)

    # Effective upper bound each step
    ub = np.minimum(p_max, renewable_forecast)
    lb = np.zeros(T)  # allow off state
    # But if on, must be >= p_min. We'll handle via soft rule later if needed.
    # For now: allow 0..ub and add a mild penalty for being between 0 and p_min if you want v1.1.
    bounds = [(lb[i], ub[i]) for i in range(T)]

    # Initial guess: baseline clipped
    x0 = np.minimum(renewable_forecast, p_max)

    def objective(P):
        P = np.asarray(P)
        hydrogen = efficiency * P
        ramps = _smooth_abs(P[1:] - P[:-1], eps)
        # minimize negative hydrogen + ramp penalty
        return -np.sum(hydrogen) + lambda_ramp * np.sum(ramps)

    # Ramp constraints: |P_t - P_{t-1}| <= ramp_limit
    # Represent as two inequalities:
    # (P_t - P_{t-1}) <= ramp_limit and (P_{t-1} - P_t) <= ramp_limit
    cons = []
    for t in range(1, T):
        cons.append({"type": "ineq", "fun": lambda P, t=t: ramp_limit - (P[t] - P[t-1])})
        cons.append({"type": "ineq", "fun": lambda P, t=t: ramp_limit - (P[t-1] - P[t])})

    res = minimize(objective, x0=x0, bounds=bounds, constraints=cons, method="SLSQP", options={"maxiter": 500})

    return {
        "success": bool(res.success),
        "message": res.message,
        "schedule_kw": res.x,
        "objective_value": res.fun,
        "nit": res.nit,
    }

def optimise_schedule_objective3(
    renewable_forecast: np.ndarray,
    prices: np.ndarray,
    p_min: float,
    p_max: float,
    ramp_limit: float,
    efficiency: float,
    lambda_ramp: float,
    alpha_h2: float,
    eps: float,
) -> dict:
    """
    Objective 3 (economic optimisation):
    Minimise:  sum(price_t * P_t) + lambda * sum(|ΔP|) - alpha * sum(H(P_t))

    Intuition:
      - price_t * P_t encourages using less power when electricity is expensive
      - ramp penalty encourages smooth operation
      - hydrogen reward encourages producing hydrogen (prevents trivial P=0 solution)

    Constraints:
      - 0 <= P_t <= min(p_max, renewable_forecast_t)
      - |P_t - P_{t-1}| <= ramp_limit
    """
    renewable_forecast = np.asarray(renewable_forecast)
    prices = np.asarray(prices)
    T = len(renewable_forecast)

    # Bounds: 0..available (and <= p_max)
    ub = np.minimum(p_max, renewable_forecast)
    bounds = [(0.0, ub[i]) for i in range(T)]

    # Initial guess
    x0 = np.minimum(renewable_forecast, p_max)

    def objective(P):
        P = np.asarray(P)
        hydrogen = efficiency * P
        ramps = _smooth_abs(P[1:] - P[:-1], eps)

        cost = np.sum(prices * P)
        smoothness = lambda_ramp * np.sum(ramps)
        reward_h2 = alpha_h2 * np.sum(hydrogen)

        return cost + smoothness - reward_h2

    # Ramp constraints
    cons = []
    for t in range(1, T):
        cons.append({"type": "ineq", "fun": lambda P, t=t: ramp_limit - (P[t] - P[t-1])})
        cons.append({"type": "ineq", "fun": lambda P, t=t: ramp_limit - (P[t-1] - P[t])})

    res = minimize(
        objective,
        x0=x0,
        bounds=bounds,
        constraints=cons,
        method="SLSQP",
        options={"maxiter": 800},
    )

    return {
        "success": bool(res.success),
        "message": res.message,
        "schedule_kw": res.x,
        "objective_value": res.fun,
        "nit": res.nit,
    }