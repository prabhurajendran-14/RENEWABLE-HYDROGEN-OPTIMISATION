import matplotlib.pyplot as plt

def plot_schedules(df, outpath=None):
    plt.figure()
    plt.plot(df["timestamp"], df["renewable_kw"], label="Renewable (available)")
    plt.plot(df["timestamp"], df["baseline_naive_kw"], label="Baseline (naive)")
    plt.plot(df["timestamp"], df["baseline_ramp_kw"], label="Baseline (ramp-limited)")
    plt.plot(df["timestamp"], df["optimised_kw"], label="Optimised schedule")
    plt.legend()
    plt.title("Renewable Availability vs Electrolyser Power Schedule")
    plt.xlabel("Time")
    plt.ylabel("kW")
    plt.xticks(rotation=30)
    plt.tight_layout()
    if outpath:
        plt.savefig(outpath, dpi=200)
    plt.show()


def plot_tradeoff(tradeoff_df, outpath=None):
    """
    Plot trade-off between smoothness (total_ramp) and productivity (total_hydrogen)
    for different lambda values.
    """
    plt.figure()
    plt.plot(tradeoff_df["total_ramp"], tradeoff_df["total_hydrogen"], marker="o")

    # Label each point with lambda
    for _, r in tradeoff_df.iterrows():
        plt.text(r["total_ramp"] + 2, r["total_hydrogen"] + 2, f"λ={r['lambda']}", fontsize=8)
    plt.title("Trade-off: Hydrogen Production vs Ramping Penalty (λ)")
    plt.xlabel("Total Ramp (lower is smoother)")
    plt.ylabel("Total Hydrogen (higher is better)")
    plt.tight_layout()
    if outpath:
        plt.savefig(outpath, dpi=200)
    plt.show()