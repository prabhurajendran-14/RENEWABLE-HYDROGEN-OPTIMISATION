import numpy as np

def hydrogen_production(power_kw: np.ndarray, efficiency: float) -> np.ndarray:
    """
    Simple model: hydrogen units proportional to power * efficiency.
    Units can be 'relative' for prototype, or kWh-equivalent hydrogen.
    """
    power_kw = np.asarray(power_kw)
    return efficiency * power_kw