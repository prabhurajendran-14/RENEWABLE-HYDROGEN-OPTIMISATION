import numpy as np
import pandas as pd

def generate_price_signal(timestamps: pd.Series, base=0.18):
    """
    Synthetic electricity price pattern (£/kWh):
    - cheaper overnight
    - more expensive during evening peak
    """
    hours = pd.to_datetime(timestamps).dt.hour.to_numpy()
    price = np.full(len(hours), base, dtype=float)

    # Overnight discount
    price[(hours >= 0) & (hours < 6)] -= 0.05

    # Morning bump
    price[(hours >= 7) & (hours < 10)] += 0.10

    # Evening peak
    price[(hours >= 16) & (hours < 20)] += 0.30

    # Small noise
    price += np.random.normal(0, 0.005, size=len(price))
    price = np.clip(price, 0.05, None)

    return price