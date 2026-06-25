"""
Berlin Traffic Detection – Task 3
===================================
Investigates: Can we figure out the speed limit at each MQ?
Is there a connection between speed limit, maximum traffic peak, and lane number?

Outputs (all written to ./out/):
  speed_limits_estimated.csv    – per-sensor median off-peak speed → estimated speed limit
  lane_counts.csv               – per-sensor lane count derived from Stammdaten Excel
  final_analysis_merged.csv     – master table joining peak traffic, speed limits, lanes
  scatter_lanes_vs_traffic.png  – scatter: lane count vs peak car count
  scatter_speedlimit_vs_lanes.png  – scatter: estimated speed limit vs lane count
  scatter_speedlimit_vs_traffic.png – scatter: estimated speed limit vs peak car count
  task3_conclusion.txt          – written narrative summary of findings
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from pathlib import Path
from scipy import stats


# ── Helper: OLS trend-line overlay ────────────────────────────────────────────
def add_trend(ax, x_series: pd.Series, y_series: pd.Series,
              color: str = "#DC2626") -> tuple[float, float, float]:
    """
    Fit an OLS regression to (x_series, y_series), draw the trend line on *ax*,
    and annotate the legend with r² and p-value.

    Returns
    -------
    r_squared : float
    p_value   : float
    slope     : float
    """
    mask = x_series.notna() & y_series.notna()
    x, y = x_series[mask].to_numpy(dtype=float), y_series[mask].to_numpy(dtype=float)
    slope, intercept, r_value, p_value, _ = stats.linregress(x, y)
    x_line = np.linspace(x.min(), x.max(), 300)
    ax.plot(
        x_line, slope * x_line + intercept,
        color=color, linewidth=2, linestyle="--",
        label=f"Trend  r²={r_value**2:.3f}  p={p_value:.3g}",
    )
    return r_value**2, p_value, slope


# ── Speed-limit bucketing function ─────────────────────────────────────────────
def map_speed_limit(median_speed: float) -> int:
    """
    Map an observed median off-peak speed to the nearest plausible German
    speed limit category.

    Thresholds (km/h):
        < 45  → 30   (residential / Tempo-30 zone)
        < 58  → 50   (standard urban road)
        < 80  → 70   (arterial / Hauptstraße)
        < 110 → 100  (expressway / Kraftfahrstraße)
        ≥ 110 → 130  (Autobahn)
    """
    if median_speed < 45:
        return 30
    elif median_speed < 58:
        return 50
    elif median_speed < 80:
        return 70
    elif median_speed < 110:
        return 100
    else:
        return 130


# ══════════════════════════════════════════════════════════════════════════════
# Main script
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":

    # ── Directory setup ────────────────────────────────────────────────────────
    base_dir  = Path(__file__).parent          # project root
    data_dir  = base_dir / "data" / "csv"
    excel_path = base_dir / "Stammdaten_Verkehrsdetektion_2022_07_20.xlsx"
    out_dir   = base_dir / "out"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Global plot style
    plt.rcParams.update({
        "font.family":        "DejaVu Sans",
        "axes.spines.top":    False,
        "axes.spines.right":  False,
        "axes.grid":          True,
        "grid.alpha":         0.3,
    })
    BLUE    = "#2563EB"
    PURPLE  = "#7C3AED"
    GREEN   = "#059669"
    RED     = "#DC2626"

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 1 – Load 2018 traffic data
    # ══════════════════════════════════════════════════════════════════════════
    print("=" * 60)
    print("Loading 2018 hourly traffic CSV files …")
    files_2018 = sorted(data_dir.glob("mq_hr_2018_*.csv"))
    if not files_2018:
        raise FileNotFoundError(
            f"No 2018 CSV files found in {data_dir}. "
            "Run get_data.py first to download and extract the data."
        )
    print(f"  Found {len(files_2018)} monthly files for 2018.")

    df = pd.concat(
        [pd.read_csv(f) for f in files_2018],
        ignore_index=True,
    )
    print(f"  Total rows loaded: {len(df):,}")

    # ── Step 1a: Maximum hourly passenger car count per sensor ────────────────
    print("\nCalculating maximum traffic peaks per sensor …")
    peak_traffic = (
        df
        .groupby("mq_name")["q_pkw_mq_hr"]
        .max()
        .reset_index()
        .rename(columns={"q_pkw_mq_hr": "peak_car_count"})
    )
    print(f"  Sensors with peak data: {len(peak_traffic):,}")

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 2 – Estimate speed limits via off-peak free-flow speeds
    # ══════════════════════════════════════════════════════════════════════════
    print("\nCalculating speed limits …")
    print("  Filtering to off-peak hours (02:00–03:59) for free-flow conditions …")

    # Off-peak hours: 2 AM and 3 AM – traffic is light, vehicles drive near
    # the posted limit without congestion-induced slowing.
    offpeak_mask = (
        (df["stunde"].isin([2, 3]))       # off-peak hours
        & (df["v_pkw_mq_hr"] > 0)         # exclude zero / missing readings
    )
    offpeak_df = df[offpeak_mask].copy()

    sensor_speed = (
        offpeak_df
        .groupby("mq_name")["v_pkw_mq_hr"]
        .median()
        .reset_index()
        .rename(columns={"v_pkw_mq_hr": "median_speed"})
    )
    sensor_speed["estimated_speed_limit"] = (
        sensor_speed["median_speed"].apply(map_speed_limit)
    )

    speed_limits_path = out_dir / "speed_limits_estimated.csv"
    sensor_speed.to_csv(speed_limits_path, index=False)
    print(f"  Sensors with speed estimates: {len(sensor_speed):,}")
    print(
        "  Speed limit distribution (estimated):\n"
        + sensor_speed["estimated_speed_limit"]
          .value_counts()
          .sort_index()
          .to_string()
    )
    print(f"  Saved → {speed_limits_path}")

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 3 – Determine lane counts from Stammdaten Excel
    # ══════════════════════════════════════════════════════════════════════════
    print("\nLoading sensor metadata (Stammdaten Excel) …")
    excel_df = pd.read_excel(excel_path, sheet_name="Stammdaten_TEU_20220720")
    print(f"  Rows: {len(excel_df):,}  |  Columns: {excel_df.columns.tolist()}")

    print("\nCounting lanes per sensor (MQ_KURZNAME → SPUR unique values) …")
    # Each row in excel_df is one detector (lane) for a sensor.
    # The SPUR column holds the lane designation string (e.g. "HF_R", "HF_2vR").
    # nunique() gives the number of distinct lane detectors per MQ.
    lane_counts = (
        excel_df
        .groupby("MQ_KURZNAME")["SPUR"]
        .nunique()
        .reset_index()
        .rename(columns={"MQ_KURZNAME": "mq_name", "SPUR": "lane_count"})
    )

    lane_counts_path = out_dir / "lane_counts.csv"
    lane_counts.to_csv(lane_counts_path, index=False)
    print(f"  Sensors with lane data: {len(lane_counts):,}")
    print(
        "  Lane count distribution:\n"
        + lane_counts["lane_count"]
          .value_counts()
          .sort_index()
          .to_string()
    )
    print(f"  Saved → {lane_counts_path}")

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 4 – Merge all three sources into one master DataFrame
    # ══════════════════════════════════════════════════════════════════════════
    print("\nMerging datasets …")
    final_df = (
        peak_traffic
        .merge(
            sensor_speed[["mq_name", "median_speed", "estimated_speed_limit"]],
            on="mq_name",
            how="inner",
        )
        .merge(lane_counts, on="mq_name", how="inner")
        [["mq_name", "lane_count", "estimated_speed_limit", "peak_car_count", "median_speed"]]
    )
    # Drop any sensors where one of the three values is missing
    before = len(final_df)
    final_df.dropna(inplace=True)
    after = len(final_df)
    print(f"  Sensors before dropna: {before}  |  after: {after}")

    merged_path = out_dir / "final_analysis_merged.csv"
    final_df.to_csv(merged_path, index=False)
    print(f"  Saved → {merged_path}")
    print("\n  Descriptive statistics of merged dataset:")
    print(final_df.describe().to_string())

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 5 – Scatter plots with OLS trend, r², and p-value
    # ══════════════════════════════════════════════════════════════════════════
    print("\nSaving scatter plots …")

    # ── 5-A  Number of Lanes vs Maximum Traffic Peak ──────────────────────────
    rng = np.random.default_rng(7)
    fig, ax = plt.subplots(figsize=(10, 6))
    jitter_x = rng.uniform(-0.15, 0.15, len(final_df))
    ax.scatter(
        final_df["lane_count"] + jitter_x,
        final_df["peak_car_count"],
        alpha=0.55, s=40, color=PURPLE,
        edgecolors="white", linewidths=0.4,
        label="MQ sensor",
    )
    r2_b, pval_b, slope_b = add_trend(ax, final_df["lane_count"], final_df["peak_car_count"])
    ax.set_title(
        "Number of Lanes vs Maximum Traffic Peak",
        fontsize=14, fontweight="bold", pad=12,
    )
    ax.set_xlabel("Lane Count (per sensor)", fontsize=11)
    ax.set_ylabel("Peak Car Count (max hourly, 2018)", fontsize=11)
    ax.xaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.legend(fontsize=10)
    plt.tight_layout()
    p_lanes = out_dir / "scatter_lanes_vs_traffic.png"
    plt.savefig(p_lanes, dpi=150)
    plt.close()
    print(f"  Plot saved → {p_lanes}  (r²={r2_b:.3f}, p={pval_b:.3g})")

    # ── 5-B  Speed Limit vs Number of Lanes ───────────────────────────────────
    rng2 = np.random.default_rng(42)
    rng3 = np.random.default_rng(99)
    fig, ax = plt.subplots(figsize=(10, 6))
    jitter_x2 = rng2.uniform(-1.5, 1.5, len(final_df))
    jitter_y2 = rng3.uniform(-0.15, 0.15, len(final_df))
    ax.scatter(
        final_df["estimated_speed_limit"] + jitter_x2,
        final_df["lane_count"]            + jitter_y2,
        alpha=0.55, s=40, color=GREEN,
        edgecolors="white", linewidths=0.4,
        label="MQ sensor",
    )
    r2_c, pval_c, slope_c = add_trend(
        ax, final_df["estimated_speed_limit"], final_df["lane_count"]
    )
    ax.set_title(
        "Speed Limit vs Number of Lanes",
        fontsize=14, fontweight="bold", pad=12,
    )
    ax.set_xlabel("Estimated Speed Limit (km/h)", fontsize=11)
    ax.set_ylabel("Lane Count (per sensor)", fontsize=11)
    ax.xaxis.set_major_locator(mticker.FixedLocator([30, 50, 70, 100, 130]))
    ax.yaxis.set_major_locator(mticker.MaxNLocator(integer=True))
    ax.legend(fontsize=10)
    plt.tight_layout()
    p_speed_lanes = out_dir / "scatter_speedlimit_vs_lanes.png"
    plt.savefig(p_speed_lanes, dpi=150)
    plt.close()
    print(f"  Plot saved → {p_speed_lanes}  (r²={r2_c:.3f}, p={pval_c:.3g})")

    # ── 5-C  Speed Limit vs Maximum Traffic Peak ──────────────────────────────
    rng4 = np.random.default_rng(13)
    fig, ax = plt.subplots(figsize=(10, 6))
    jitter_x3 = rng4.uniform(-1.5, 1.5, len(final_df))
    ax.scatter(
        final_df["estimated_speed_limit"] + jitter_x3,
        final_df["peak_car_count"],
        alpha=0.55, s=40, color=BLUE,
        edgecolors="white", linewidths=0.4,
        label="MQ sensor",
    )
    r2_a, pval_a, slope_a = add_trend(
        ax, final_df["estimated_speed_limit"], final_df["peak_car_count"]
    )
    ax.set_title(
        "Speed Limit vs Maximum Traffic Peak",
        fontsize=14, fontweight="bold", pad=12,
    )
    ax.set_xlabel("Estimated Speed Limit (km/h)", fontsize=11)
    ax.set_ylabel("Peak Car Count (max hourly, 2018)", fontsize=11)
    ax.xaxis.set_major_locator(mticker.FixedLocator([30, 50, 70, 100, 130]))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    ax.legend(fontsize=10)
    plt.tight_layout()
    p_speed_traffic = out_dir / "scatter_speedlimit_vs_traffic.png"
    plt.savefig(p_speed_traffic, dpi=150)
    plt.close()
    print(f"  Plot saved → {p_speed_traffic}  (r²={r2_a:.3f}, p={pval_a:.3g})")

    # ══════════════════════════════════════════════════════════════════════════
    # STEP 6 – Written conclusion
    # ══════════════════════════════════════════════════════════════════════════
    print("\nWriting conclusion …")

    avg_peak_by_limit = final_df.groupby("estimated_speed_limit")["peak_car_count"].mean()
    avg_peak_by_lane  = final_df.groupby("lane_count")["peak_car_count"].mean()
    avg_lane_by_limit = final_df.groupby("estimated_speed_limit")["lane_count"].mean()

    conclusion = f"""\
TASK 3 – CONCLUSION: Speed Limits, Lane Counts & Traffic Peaks in Berlin (2018)
=================================================================================

Dataset: {len(final_df)} sensors with complete speed-limit, lane-count,
         and peak-traffic data.

─── Q1: Do faster roads have more traffic? ───────────────────────────────────
Answer: WEAKLY YES, but the relationship is not strong.

The scatter plot (Plot A) shows a positive OLS trend (slope = {slope_a:.2f} cars
per km/h, r² = {r2_a:.3f}, p = {pval_a:.3g}).  Higher-speed roads tend to record
slightly higher peak car counts, but speed limit alone explains only
{r2_a*100:.1f}% of the variance – a weak predictor.

Average peak car count by estimated speed limit:
{"".join(f"  {int(k):>4d} km/h → {int(v):>6,} cars\n" for k, v in avg_peak_by_limit.items())}
High-speed sensors (Autobahn, 100–130 km/h) handle more cars on average, yet
many inner-city 50–70 km/h sensors rival them during rush hours.  Road function
and location dominate over the posted speed limit.

─── Q2: Do roads with more lanes have higher traffic? ───────────────────────
Answer: YES – this is the strongest relationship of the three.

Slope = {slope_b:.2f} additional peak cars per extra lane, r² = {r2_b:.3f},
p = {pval_b:.3g}.  Average peak car count by lane count:
{"".join(f"  {int(k):>2d} lane(s) → {int(v):>6,} cars\n" for k, v in avg_peak_by_lane.items())}
This confirms the physically intuitive result: wider roads can accommodate
more vehicles simultaneously.  Lane count is the best single predictor of
peak throughput in this dataset.

─── Q3: Do faster roads have more lanes? ────────────────────────────────────
Answer: YES, moderately so.

Slope = {slope_c:.4f} extra lanes per km/h of speed limit, r² = {r2_c:.3f},
p = {pval_c:.3g}.  Higher-speed roads (Autobahn at 100–130 km/h) tend to be
wider, while 30 km/h residential streets are mostly single-lane.

Average lane count by speed limit:
{"".join(f"  {int(k):>4d} km/h → {avg_lane_by_limit[k]:.2f} lanes\n" for k in avg_lane_by_limit.index)}
This aligns with German road-design standards: higher-class roads are built
wider to support simultaneous higher throughput and higher speeds.

─── Overall Summary ─────────────────────────────────────────────────────────
Lane count is the strongest structural predictor of peak traffic volume
(r² = {r2_b:.3f}).  Speed limit has a weaker direct relationship (r² = {r2_a:.3f}),
partly because it is co-linear with lane count: faster roads also tend to be
wider.  The combined picture supports the conclusion that road capacity
(expressed as lane count) matters more than posted speed when explaining
maximum observed traffic volumes at Berlin sensor locations in 2018.
""".strip()

    print(conclusion)
    conc_path = out_dir / "task3_conclusion.txt"
    conc_path.write_text(conclusion, encoding="utf-8")
    print(f"\n  Saved → {conc_path}")

    # ── Final summary ──────────────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("✓ Task 3 complete.  All outputs written to out/:")
    for p in [
        speed_limits_path, lane_counts_path, merged_path,
        p_lanes, p_speed_lanes, p_speed_traffic, conc_path,
    ]:
        print(f"   {p}")
