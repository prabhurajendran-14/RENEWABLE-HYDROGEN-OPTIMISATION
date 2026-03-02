import pandas as pd

def perfect_forecast(df: pd.DataFrame) -> pd.Series:
    """
    v1: Use actual renewable as forecast to validate optimisation works.
    Later: replace with SARIMAX forecast.
    """
    return df["renewable_kw"].copy()

# Placeholder for later
def sarimax_forecast(train_series, steps: int):
    """
    v2: Implement SARIMAX later (Objective 3 extension-ready).
    """
    raise NotImplementedError("Implement SARIMAX later if time permits.")