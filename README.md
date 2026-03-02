# Renewable-Powered Hydrogen Electrolyser Optimisation

## Overview
This project develops a constrained optimisation framework for scheduling a hydrogen electrolyser powered by variable renewable energy over a 24-hour horizon with 5-minute resolution. The model maximises hydrogen production while respecting operational constraints including renewable availability, power bounds, and ramp-rate limits.

Two optimisation strategies are implemented:

Objective 2 (Smoothness-aware optimisation): maximises hydrogen production while penalising ramping behaviour through a λ sensitivity analysis.

Objective 3 (Cost-aware optimisation): incorporates a time-varying electricity price signal to minimise cost per unit hydrogen while maintaining operational smoothness.

The framework demonstrates how operational, economic, and physical constraints can be integrated into a structured optimisation-based control strategy.

## Problem Formulation
The optimisation problem is solved over a 24-hour horizon with 5-minute resolution.

Constraints:
- 0 ≤ P_t ≤ min(P_max, Renewable_t)
- |P_t − P_{t-1}| ≤ Ramp_limit

Objective 2:
Maximise hydrogen production while penalising ramping.
Objective 3:
Minimise electricity cost while rewarding hydrogen production and penalising ramping.

## Key Results
- λ sensitivity analysis demonstrates a clear trade-off between operational smoothness and hydrogen yield.
- Cost-aware optimisation reduces cost per kg of hydrogen compared to baseline and smoothness-only control.
- The optimiser successfully adapts production in response to peak electricity pricing periods.
- Robustness tested under forecast uncertainty.

The model generates:
- Schedule comparison plots
- Hydrogen vs ramp trade-off curve
- Cost comparison metrics

## Technologies Used
- Python
- NumPy
- SciPy (SLSQP optimisation)
- Pandas
- Matplotlib


## How to Run
  pip install -r requirements.txt
  python main.py
