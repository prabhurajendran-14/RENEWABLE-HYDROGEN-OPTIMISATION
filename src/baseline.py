import numpy as np

def naive_controller(renewable_forecast: np.ndarray, p_min: float, p_max: float) -> np.ndarray:
    """
    Baseline 1 (naive): use as much renewable as possible, clipped to [0, p_max].
    If renewable < p_min: operate at 0 (off).
    NOTE: No ramp constraints.
    """
    renewable_forecast = np.asarray(renewable_forecast)
    p = np.clip(renewable_forecast, 0, p_max)
    p = np.where(p >= p_min, p, 0.0)
    return p


def ramp_limited_reactive_controller(
    renewable_forecast: np.ndarray,
    p_min: float,
    p_max: float,
    ramp_limit: float,
) -> np.ndarray:
    """
    Baseline 2 (reactive + realistic):
    Follow available renewable power, but enforce:
      - bounds [0, p_max]
      - if on then >= p_min (otherwise off)
      - ramp limit per timestep

    This gives a fair baseline vs the optimiser (which also respects ramp limits).
    """
    renewable_forecast = np.asarray(renewable_forecast)
    T = len(renewable_forecast)
    schedule = np.zeros(T)

    for t in range(T):
        # Desired power is "use what's available", clipped to max
        desired = min(renewable_forecast[t], p_max)

        # If desired is below p_min, we choose to stay off (0)
        if desired < p_min:
            desired = 0.0

        if t == 0:
            schedule[t] = desired
            continue

        # Enforce ramp limit from previous step
        prev = schedule[t - 1]
        lower = max(0.0, prev - ramp_limit)
        upper = min(p_max, prev + ramp_limit)

        # Also cannot exceed renewable available at time t
        upper = min(upper, renewable_forecast[t])

        # Clip desired into [lower, upper]
        p_t = min(max(desired, lower), upper)

        # Enforce min-on rule again (either 0 or >= p_min)
        if 0.0 < p_t < p_min:
            # choose whichever is closer: off (0) or p_min (if feasible)
            if (p_min <= upper) and (abs(p_min - p_t) < abs(0.0 - p_t)):
                p_t = p_min
            else:
                p_t = 0.0

        schedule[t] = p_t

    return schedule