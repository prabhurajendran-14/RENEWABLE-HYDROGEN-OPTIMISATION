import numpy as np
import pandas as pd

def simulate_solar_like_power(start: str, periods: int, freq: str, peak_kw: float, noise_std: float, seed: int) -> pd.DataFrame:
    """
    Create a solar-like renewable power profile with noise.
    Returns DataFrame with columns: ['timestamp', 'renewable_kw']
    """
    rng = np.random.default_rng(seed)
    ts = pd.date_range(start=start, periods=periods, freq=freq)

    # Solar-like curve: sine wave clipped at 0
    t = np.arange(periods)
    daily_phase = (t / periods) * np.pi  # 0..pi across day
    base = np.sin(daily_phase) * peak_kw
    base = np.clip(base, 0, None)

    noise = rng.normal(0, noise_std, size=periods)
    renewable = np.clip(base + noise, 0, None)

    return pd.DataFrame({"timestamp": ts, "renewable_kw": renewable})