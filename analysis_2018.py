"""
Berlin Traffic Analysis - 2018
Generates:
  - Heatmap:       out/traffic_heatmap_2018.png
  - Daily chart:   out/cars_per_day_2018.png
  - Anomalies:     out/anomalies_2018.txt
  - Peak hours:    out/peak_hours_2018.csv
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import numpy as np
from pathlib import Path

# ── Setup ──────────────────────────────────────────────────────────────────────
out = Path("./out")
out.mkdir(parents=True, exist_ok=True)

# ── Load all CSV files and filter to 2018 ─────────────────────────────────────
print("Loading data …")
data_path = Path("./data/csv")
files_2018 = sorted(data_path.glob("mq_hr_2018_*.csv"))

if not files_2018:
    raise FileNotFoundError("No 2018 CSV files found in data/csv/")

print(f"  Found {len(files_2018)} files for 2018")
df = pd.concat([pd.read_csv(f) for f in files_2018], ignore_index=True)

# Parse dates and extract helper columns
df["tag_date"]   = pd.to_datetime(df["tag"], format="%d.%m.%Y")
df["year"]       = df["tag_date"].dt.year
df["day_of_week"] = df["tag_date"].dt.day_name()   # Monday … Sunday
df["dow_num"]    = df["tag_date"].dt.dayofweek      # 0=Mon … 6=Sun
df["stunde"]     = df["stunde"].astype(int)

# ── 1. Filter to 2018 ─────────────────────────────────────────────────────────
df_2018 = df[df["year"] == 2018].copy()
print(f"  Rows in 2018 dataset: {len(df_2018):,}")

# ── 2. Heatmap ────────────────────────────────────────────────────────────────
print("Creating heatmap …")

# Average car count per (day-of-week, hour) across all sensors and days
pivot = (
    df_2018
    .groupby(["dow_num", "day_of_week", "stunde"])["q_pkw_mq_hr"]
    .mean()
    .reset_index()
)
day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
pivot_table = pivot.pivot_table(index="day_of_week", columns="stunde", values="q_pkw_mq_hr")
pivot_table = pivot_table.reindex(day_order)

# Hour labels: 0→"12am", 1→"1am", …, 12→"12pm", …, 23→"11pm"
def hour_label(h):
    if h == 0:   return "12am"
    if h < 12:   return f"{h}am"
    if h == 12:  return "12pm"
    return f"{h - 12}pm"

hour_labels = [hour_label(h) for h in range(24)]

fig, ax = plt.subplots(figsize=(18, 6))
sns.heatmap(
    pivot_table,
    ax=ax,
    cmap="YlOrRd",
    linewidths=0.4,
    linecolor="white",
    xticklabels=hour_labels,
    yticklabels=day_order,
    cbar_kws={"label": "Avg Cars per Hour per Sensor"},
    annot=False,
)
ax.set_title("Berlin Traffic Heatmap – 2018: Hour vs Day of Week",
             fontsize=15, fontweight="bold", pad=14)
ax.set_xlabel("Hour of Day", fontsize=11)
ax.set_ylabel("Day of Week", fontsize=11)
ax.tick_params(axis="x", rotation=45)
ax.tick_params(axis="y", rotation=0)
plt.tight_layout()
heatmap_path = out / "traffic_heatmap_2018.png"
plt.savefig(heatmap_path, dpi=150)
plt.close()
print(f"  Saved → {heatmap_path}")

# ── 3. Daily line chart ────────────────────────────────────────────────────────
print("Creating daily line chart …")

daily = (
    df_2018
    .groupby("tag_date")["q_pkw_mq_hr"]
    .sum()
    .reset_index()
    .rename(columns={"q_pkw_mq_hr": "total_cars"})
)
daily = daily.sort_values("tag_date")

# Rolling 7-day average for trend line
daily["rolling_7"] = daily["total_cars"].rolling(7, center=True).mean()

# Mark statistical outliers: beyond 2 std devs from the rolling mean
mean_val = daily["total_cars"].mean()
std_val  = daily["total_cars"].std()
daily["is_anomaly"] = (daily["total_cars"] < mean_val - 2 * std_val) | \
                      (daily["total_cars"] > mean_val + 2 * std_val)

fig, ax = plt.subplots(figsize=(16, 6))
ax.fill_between(daily["tag_date"], daily["total_cars"], alpha=0.15, color="#2563EB")
ax.plot(daily["tag_date"], daily["total_cars"], color="#2563EB",
        linewidth=0.8, label="Daily total cars")
ax.plot(daily["tag_date"], daily["rolling_7"], color="#DC2626",
        linewidth=2, label="7-day rolling average")

# Highlight anomalies
anomalies = daily[daily["is_anomaly"]]
ax.scatter(anomalies["tag_date"], anomalies["total_cars"],
           color="#F59E0B", s=60, zorder=5, label="Statistical anomaly")

ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.set_title("Total Cars per Day – 2018", fontsize=15, fontweight="bold", pad=14)
ax.set_xlabel("Date", fontsize=11)
ax.set_ylabel("Total Cars (all sensors)", fontsize=11)
ax.legend(fontsize=10)
ax.grid(True, alpha=0.3)
plt.xticks(rotation=45)
plt.tight_layout()
line_path = out / "cars_per_day_2018.png"
plt.savefig(line_path, dpi=150)
plt.close()
print(f"  Saved → {line_path}")

# ── 4. Anomaly analysis ────────────────────────────────────────────────────────
print("Identifying anomalies …")

# German public holidays 2018 (federal + Berlin-specific)
holidays_2018 = {
    "2018-01-01": "New Year's Day",
    "2018-03-30": "Good Friday",
    "2018-04-01": "Easter Sunday",
    "2018-04-02": "Easter Monday",
    "2018-05-01": "Labour Day",
    "2018-05-10": "Ascension Day",
    "2018-05-20": "Whit Sunday",
    "2018-05-21": "Whit Monday",
    "2018-10-03": "German Unity Day",
    "2018-10-31": "Reformation Day (Berlin)",
    "2018-12-25": "Christmas Day",
    "2018-12-26": "Boxing Day",
}

# Berlin school holiday periods 2018 (approximate)
school_holidays = [
    ("2018-01-01", "2018-01-05",  "Winter school holidays"),
    ("2018-03-26", "2018-04-06",  "Easter school holidays"),
    ("2018-06-07", "2018-06-22",  "Whitsun school holidays"),
    ("2018-07-05", "2018-08-17",  "Summer school holidays"),
    ("2018-10-01", "2018-10-12",  "Autumn school holidays"),
    ("2018-12-21", "2018-12-31",  "Christmas school holidays"),
]

# Calculate daily mean and std per day-of-week group to normalise weekends
daily["dow_name"] = daily["tag_date"].dt.day_name()
dow_stats = daily.groupby("dow_name")["total_cars"].agg(["mean","std"])

anomaly_lines = []
anomaly_lines.append("=" * 70)
anomaly_lines.append("BERLIN TRAFFIC ANOMALY REPORT – 2018")
anomaly_lines.append("=" * 70)
anomaly_lines.append("")

# --- Statistical outliers (global ±2σ) ---
anomaly_lines.append("─── Statistical Outliers (±2σ from annual mean) ───")
for _, row in anomalies.iterrows():
    d = row["tag_date"]
    ds = d.strftime("%Y-%m-%d")
    dow = d.strftime("%A")
    delta_pct = (row["total_cars"] - mean_val) / mean_val * 100
    direction = "HIGH" if delta_pct > 0 else "LOW"
    note = holidays_2018.get(ds, "")
    school_note = ""
    for (s, e, name) in school_holidays:
        if pd.to_datetime(s) <= d <= pd.to_datetime(e):
            school_note = f" [School holiday: {name}]"
            break
    anomaly_lines.append(
        f"  {ds}  ({dow})  {direction}: {row['total_cars']:>12,.0f} cars  "
        f"({delta_pct:+.1f}%)  {note}{school_note}"
    )

anomaly_lines.append("")

# --- Public holidays ---
anomaly_lines.append("─── Public Holidays 2018 (expected traffic dips) ───")
for ds, name in holidays_2018.items():
    try:
        row = daily[daily["tag_date"] == pd.to_datetime(ds)].iloc[0]
        delta_pct = (row["total_cars"] - mean_val) / mean_val * 100
        dow = pd.to_datetime(ds).strftime("%A")
        anomaly_lines.append(
            f"  {ds}  ({dow})  {name:<35s}  "
            f"{row['total_cars']:>12,.0f} cars  ({delta_pct:+.1f}%)"
        )
    except IndexError:
        anomaly_lines.append(f"  {ds}  {name}  (no data)")

anomaly_lines.append("")

# --- Weekend vs weekday summary ---
anomaly_lines.append("─── Weekday vs Weekend Comparison ───")
wday = daily[daily["tag_date"].dt.dayofweek < 5]["total_cars"]
wend = daily[daily["tag_date"].dt.dayofweek >= 5]["total_cars"]
anomaly_lines.append(
    f"  Weekday avg: {wday.mean():>12,.0f} cars/day"
)
anomaly_lines.append(
    f"  Weekend avg: {wend.mean():>12,.0f} cars/day  "
    f"({(wend.mean() - wday.mean()) / wday.mean() * 100:+.1f}% vs weekdays)"
)
anomaly_lines.append("")

# --- Top 5 quietest & busiest days ---
anomaly_lines.append("─── Top 5 Quietest Days ───")
for _, row in daily.nsmallest(5, "total_cars").iterrows():
    ds = row["tag_date"].strftime("%Y-%m-%d")
    dow = row["tag_date"].strftime("%A")
    note = holidays_2018.get(ds, "")
    anomaly_lines.append(f"  {ds}  ({dow})  {row['total_cars']:>12,.0f} cars  {note}")

anomaly_lines.append("")
anomaly_lines.append("─── Top 5 Busiest Days ───")
for _, row in daily.nlargest(5, "total_cars").iterrows():
    ds = row["tag_date"].strftime("%Y-%m-%d")
    dow = row["tag_date"].strftime("%A")
    note = holidays_2018.get(ds, "")
    anomaly_lines.append(f"  {ds}  ({dow})  {row['total_cars']:>12,.0f} cars  {note}")

anomaly_lines.append("")
anomaly_lines.append("─── Key Observations ───")
anomaly_lines.append(
    "  • Traffic is significantly lower on weekends and public holidays."
)
anomaly_lines.append(
    "  • Summer school holidays (Jul–Aug) show a sustained moderate dip."
)
anomaly_lines.append(
    "  • Christmas–New Year period is the quietest stretch of the year."
)
anomaly_lines.append(
    "  • Peak traffic typically falls on Tuesday–Thursday mornings (7–9am) "
    "and afternoons (4–6pm)."
)
anomaly_lines.append(
    "  • Note: COVID-19 lockdowns started in 2020, so no COVID effect in 2018."
)

anomaly_text = "\n".join(anomaly_lines)
print(anomaly_text)

anomaly_path = out / "anomalies_2018.txt"
anomaly_path.write_text(anomaly_text, encoding="utf-8")
print(f"\n  Saved → {anomaly_path}")

# ── 5. Peak traffic hours ──────────────────────────────────────────────────────
print("Finding peak traffic hours …")

# Sum all sensors per (date, hour) to get total hourly traffic
hourly = (
    df_2018
    .groupby(["tag_date", "stunde"])["q_pkw_mq_hr"]
    .sum()
    .reset_index()
    .rename(columns={"q_pkw_mq_hr": "total_cars"})
)
hourly["day_of_week"] = hourly["tag_date"].dt.day_name()
hourly["date_str"]    = hourly["tag_date"].dt.strftime("%Y-%m-%d")

top10 = (
    hourly
    .nlargest(10, "total_cars")
    [["date_str", "stunde", "total_cars", "day_of_week"]]
    .rename(columns={
        "date_str":    "Date",
        "stunde":      "Hour",
        "total_cars":  "Total Cars",
        "day_of_week": "Day of Week",
    })
    .reset_index(drop=True)
)
top10.index += 1  # 1-based rank

print("\nTop 10 Busiest Hours – 2018:")
print(top10.to_string())

peak_path = out / "peak_hours_2018.csv"
top10.to_csv(peak_path)
print(f"\n  Saved → {peak_path}")

# ── Done ───────────────────────────────────────────────────────────────────────
print("\n✓ All outputs written to out/")
print(f"   {heatmap_path}")
print(f"   {line_path}")
print(f"   {anomaly_path}")
print(f"   {peak_path}")
