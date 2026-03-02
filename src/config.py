from dataclasses import dataclass

@dataclass
class Config:
    # Time settings
    freq_minutes: int = 15
    horizon_hours: int = 24

    # Electrolyser constraints (kW)
    p_min: float = 10.0
    p_max: float = 80.0
    ramp_limit: float = 25.0  # max change per timestep (kW)

    # Electrolyser efficiency (simple constant for v1)
    efficiency: float = 0.65

    # Objective 2 parameter (smoothness penalty)
    lambda_ramp: float = 0.2
    abs_smooth_eps: float = 1e-6  # for smooth |x| approximation

    # Synthetic renewable settings
    renewable_peak: float = 100.0
    noise_std: float = 8.0
    random_seed: int = 42