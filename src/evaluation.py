import numpy as np
import pandas as pd
from .electrolyser_model import hydrogen_production

def evaluate(schedule_kw: np.ndarray, efficiency: float) -> dict:
    schedule_kw = np.asarray(schedule_kw)
    h = hydrogen_production(schedule_kw, efficiency)
    ramps = np.abs(np.diff(schedule_kw, prepend=schedule_kw[0]))
    return {
        "total_hydrogen": float(np.sum(h)),
        "total_energy": float(np.sum(schedule_kw)),
        "total_ramp": float(np.sum(ramps)),
        "max_ramp": float(np.max(ramps)),
        "mean_power": float(np.mean(schedule_kw)),
    }

def to_results_df(timestamps, renewable, baseline_naive, baseline_ramp, optimised) -> pd.DataFrame:
    return pd.DataFrame({
        "timestamp": timestamps,
        "renewable_kw": renewable,
        "baseline_naive_kw": baseline_naive,
        "baseline_ramp_kw": baseline_ramp,
        "optimised_kw": optimised,
    })

import numpy as np
from .electrolyser_model import hydrogen_production

def evaluate_with_cost(schedule_kw: np.ndarray, efficiency: float, prices: np.ndarray) -> dict:
    schedule_kw = np.asarray(schedule_kw)
    prices = np.asarray(prices)

    h = hydrogen_production(schedule_kw, efficiency)
    ramps = np.abs(np.diff(schedule_kw, prepend=schedule_kw[0]))

    total_cost = float(np.sum(prices * schedule_kw))
    total_h2 = float(np.sum(h))
    cost_per_h2 = total_cost / total_h2 if total_h2 > 0 else float("inf")

    return {
        "total_hydrogen": total_h2,
        "total_energy": float(np.sum(schedule_kw)),
        "total_cost": total_cost,
        "cost_per_h2": float(cost_per_h2),
        "total_ramp": float(np.sum(ramps)),
        "max_ramp": float(np.max(ramps)),
        "mean_power": float(np.mean(schedule_kw)),
    }