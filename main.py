import os
import numpy as np
import pandas as pd

from src.config import Config
from src.data_simulation import simulate_solar_like_power
from src.forecasting import perfect_forecast
from src.baseline import naive_controller, ramp_limited_reactive_controller
from src.optimisation_engine import optimise_schedule_objective2
from src.evaluation import evaluate, to_results_df
from src.plotting import plot_schedules, plot_tradeoff
from src.pricing import generate_price_signal
from src.optimisation_engine import optimise_schedule_objective3
from src.evaluation import evaluate_with_cost

def main():
    cfg = Config()
    T = int((cfg.horizon_hours * 60) / cfg.freq_minutes)
    freq = f"{cfg.freq_minutes}min"

    # --- Simulate renewable power ---
    df = simulate_solar_like_power(
        start="2026-02-24 00:00:00",
        periods=T,
        freq=freq,
        peak_kw=cfg.renewable_peak,
        noise_std=cfg.noise_std,
        seed=cfg.random_seed,
    )

    forecast = perfect_forecast(df).to_numpy()
    forecast = forecast + np.random.normal(0, 5, size=len(forecast))
    forecast = np.clip(forecast, 0, None)
    # --- Generate electricity price signal ---
    prices = generate_price_signal(df["timestamp"])

    # --- Baselines ---
    baseline_naive = naive_controller(forecast, cfg.p_min, cfg.p_max)
    baseline_ramp = ramp_limited_reactive_controller(
        forecast, cfg.p_min, cfg.p_max, ramp_limit=15.0
    )

    baseline_naive_metrics = evaluate(baseline_naive, cfg.efficiency)
    baseline_ramp_metrics = evaluate(baseline_ramp, cfg.efficiency)

    print("Baseline (naive) metrics:", baseline_naive_metrics)
    print("Baseline (ramp-limited) metrics:", baseline_ramp_metrics)

    # --- Lambda Sensitivity Sweep ---
    lambda_values = [0.0, 0.05, 0.2, 1.0, 3.0, 8.0]

    tradeoff_rows = []
    schedules_by_lambda = {}

    for lam in lambda_values:
        opt = optimise_schedule_objective2(
            renewable_forecast=forecast,
            p_min=cfg.p_min,
            p_max=cfg.p_max,
            ramp_limit=cfg.ramp_limit,
            efficiency=cfg.efficiency,
            lambda_ramp=lam,
            eps=cfg.abs_smooth_eps,
        )

        schedule = opt["schedule_kw"]
        metrics = evaluate(schedule, cfg.efficiency)

        tradeoff_rows.append({
            "lambda": lam,
            "success": opt["success"],
            "total_hydrogen": metrics["total_hydrogen"],
            "total_ramp": metrics["total_ramp"],
            "max_ramp": metrics["max_ramp"],
            "mean_power": metrics["mean_power"],
            "iterations": opt["nit"],
        })

        schedules_by_lambda[lam] = schedule

    tradeoff_df = pd.DataFrame(tradeoff_rows)

    print("\n=== Lambda (λ) Sensitivity Results ===")
    print(tradeoff_df.to_string(index=False))

    # --- Choose main lambda for schedule plot ---
    chosen_lambda = 1.0
    optimised = schedules_by_lambda[chosen_lambda]
    optimised_metrics = evaluate(optimised, cfg.efficiency)

    print(f"\nChosen λ for main comparison: {chosen_lambda}")
    print("Optimised metrics (chosen λ):", optimised_metrics)
    
    # Cost-Aware Optimisation
    alpha_h2 = 1.50  # hydrogen reward weight (we may tune this)
    opt3 = optimise_schedule_objective3(
        renewable_forecast=forecast,
        prices=prices,
        p_min=cfg.p_min,
        p_max=cfg.p_max,
        ramp_limit=cfg.ramp_limit,
        efficiency=cfg.efficiency,
        lambda_ramp=1.0,
        alpha_h2=alpha_h2,
        eps=cfg.abs_smooth_eps,
    )

    schedule_obj3 = opt3["schedule_kw"]
    metrics_obj3 = evaluate_with_cost(schedule_obj3, cfg.efficiency, prices)

    print("\n=== Objective 3 (Cost-Aware) Results ===")
    print("Objective 3 metrics:", metrics_obj3)
    print("Objective 3 optimiser status:", opt3["success"], opt3["message"])
   
    # Cost comparison (same prices)
    baseline_naive_cost = evaluate_with_cost(baseline_naive, cfg.efficiency, prices)
    baseline_ramp_cost = evaluate_with_cost(baseline_ramp, cfg.efficiency, prices)
    obj2_cost = evaluate_with_cost(optimised, cfg.efficiency, prices)

    print("\n=== Cost comparison (same price signal) ===")
    print("Baseline naive (cost):", baseline_naive_cost)
    print("Baseline ramp-limited (cost):", baseline_ramp_cost)
    print(f"Objective 2 (chosen λ={chosen_lambda}) (cost):", obj2_cost)
    print("Objective 3 (cost):", metrics_obj3)

    print("\n=== Headline summary ===")
    print(f"Objective 2 cost_per_h2: {obj2_cost['cost_per_h2']:.4f}")
    print(f"Objective 3 cost_per_h2: {metrics_obj3['cost_per_h2']:.4f}")    
   
    # --- Build results dataframe ---
    results_df = to_results_df(
        df["timestamp"],
        df["renewable_kw"],
        baseline_naive,
        baseline_ramp,
        optimised,
    )

    # --- Save plots ---
    os.makedirs("outputs/figures", exist_ok=True)

    plot_schedules(
        results_df,
        outpath="outputs/figures/schedule_plot.png",
    )

    plot_tradeoff(
        tradeoff_df,
        outpath="outputs/figures/tradeoff_curve.png",
    )


if __name__ == "__main__":
    main()