
import os
import re
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.ticker import FuncFormatter

input_file = "results/local_search_final.csv"
output = "results/local_search_results"
figures = os.path.join(output, "figures")

os.makedirs(figures, exist_ok=True)

GROUP_ORDER = [
    "3X3 to 5X4 (Tiny)",
    "4X4 to 5X5 (Easy)",
    "6X6 to 8X8 (Medium, FT06)",
    "10X5 (LA01-05)",
    "10X10, 15X10 (Hard, FT10, LA16-20)",
    "15X15 (TA01-05)"
]

COLORS = {
    "swap": "#0A5B89",
    "insertion": "#77B4C7"
}

plt.rcParams.update({
    "font.family": "Arial",
    "font.size": 12,
    "axes.labelsize": 13,
    "axes.titlesize": 15,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.dpi": 300,
    "savefig.dpi": 300
})

df = pd.read_csv(input_file)

numeric_columns = [
    "n_jobs", "n_machines", "seed",
    "time_budget_s", "runtime_s", "time_to_best_s",
    "makespan", "lower_bound", "best_known", "gap_pct",
    "iterations", "restarts", "candidate_evaluations",
    "success"
]

for column in numeric_columns:
    if column in df.columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

# Keep only local search results
df_ls = df[(df["algorithm"] == "hill_climbing") & (df["variant"].isin(["swap", "insertion"]))].copy()

def assign_group(row):
    instance = str(row["instance_id"]).lower()
    family = str(row.get("family", "")).lower()

    # Generated instances
    if instance.startswith("tiny") or family == "tiny":
        return GROUP_ORDER[0]
    if instance.startswith("easy") or family == "easy":
        return GROUP_ORDER[1]
    if instance.startswith("medium") or family == "medium":
        return GROUP_ORDER[2]
    if instance.startswith("hard") or family == "hard":
        return GROUP_ORDER[4]

    # Benchmark instances
    if re.match(r"^ft06(?:_|$)", instance):
        return GROUP_ORDER[2]
    if re.match(r"^la0[1-5](?:_|$)", instance):
        return GROUP_ORDER[3]
    if re.match(r"^ft10(?:_|$)", instance):
        return GROUP_ORDER[4]
    if re.match(r"^la1[6-9](?:_|$)|^la20(?:_|$)", instance):
        return GROUP_ORDER[4]
    if re.match(r"^ta0[1-5](?:_|$)", instance):
        return GROUP_ORDER[5]
    return None


df_ls["instance_group"] = df_ls.apply(assign_group, axis=1)

df_ls["instance_group"] = pd.Categorical(df_ls["instance_group"],categories=GROUP_ORDER,ordered=True)

instance_summary = (df_ls.groupby(["instance_group", "instance_id", "variant"],observed=True).agg(
        n_runs=("seed", "count"),
        makespan_mean=("makespan", "mean"),
        makespan_best=("makespan", "min"),
        success_rate_pct=("success", lambda x: x.mean() * 100),
        gap_mean_pct=("gap_pct", "mean"),
        time_to_best_median_s=("time_to_best_s", "median"),
        iterations_mean=("iterations", "mean"),
        restarts_mean=("restarts", "mean"),
        evaluations_mean=("candidate_evaluations", "mean"),
        runtime_mean_s=("runtime_s", "mean")).reset_index())

instance_summary.to_csv(os.path.join(output, "instance_summary.csv"), index=False)

local_search_behavior = (
    instance_summary.groupby(
        ["instance_group", "variant"],observed=True).agg(
        n_instances=("instance_id", "nunique"),
        restarts_mean=("restarts_mean", "mean"),
        iterations_mean=("iterations_mean", "mean"),
        evaluations_mean=("evaluations_mean", "mean"),
        runtime_mean_s = ("runtime_mean_s", "mean"),
        time_to_best_median_s = ("time_to_best_median_s", "median"),
        best_known_reached_pct = ("success_rate_pct", "mean"),
        gap_mean_pct = ("gap_mean_pct","mean"),
        n_runs=("n_runs", "sum"))
    .reset_index()
)

local_search_behavior = local_search_behavior.round(2)
local_search_behavior.to_csv(
    os.path.join(output, "local_search_behavior.csv"), index=False)


# Figure
VARIANTS = ["swap", "insertion"]
plot_df = instance_summary[instance_summary["variant"].isin(VARIANTS)].copy()

# Order instances by group, then by instance ID
plot_df["instance_group"] = pd.Categorical(plot_df["instance_group"],categories=GROUP_ORDER,ordered=True)

instance_order = (plot_df[["instance_id", "instance_group"]].drop_duplicates().sort_values(["instance_group", "instance_id"])["instance_id"].tolist())

# Pivot the data: one row per instance, one column per neighborhood
gap_data = plot_df.pivot(index="instance_id",columns="variant",values="gap_mean_pct").reindex(instance_order)
success_data = plot_df.pivot(index="instance_id",columns="variant",values="success_rate_pct").reindex(instance_order)
evaluation_data = plot_df.pivot(index="instance_id",columns="variant",values="evaluations_mean").reindex(instance_order)

fig, axes = plt.subplots(1, 3,figsize=(16, 6.5),gridspec_kw={"width_ratios": [1.1, 0.75, 1.1]})
ax1, ax2, ax3 = axes
x = np.arange(len(instance_order))

# Identify boundaries between instance groups
group_info = (plot_df[["instance_id", "instance_group"]].drop_duplicates().set_index("instance_id").reindex(instance_order))

group_positions = {}
for i, group in enumerate(GROUP_ORDER):
    positions = [
        j for j, instance in enumerate(instance_order)
        if group_info.loc[instance, "instance_group"] == group
    ]
    if positions:
        group_positions[group] = positions


#a) mean gap per instance (mean of seeds)
for i, instance in enumerate(instance_order):
    if (pd.notna(gap_data.loc[instance, "swap"]) and pd.notna(gap_data.loc[instance, "insertion"])):
        ax1.plot([0, 1],
            [gap_data.loc[instance, "swap"],gap_data.loc[instance, "insertion"]],
            color="#A8A8A8", alpha=0.45, linewidth=0.1, zorder=1)
        
for variant in VARIANTS:
    ax1.scatter(x,gap_data[variant],color=COLORS[variant],label=variant.capitalize(),s=35,zorder=2)

ax1.set_xticks(x)
ax1.set_xticklabels(instance_order, rotation=90)
ax1.set_ylabel("Mean gap (%)")
ax1.set_xlabel("Individual instances")
ax1.set_title("(a) Mean gap to best-known per instance", fontweight="bold")
ax1.legend(frameon=False, loc="upper left")

# Group boundaries
for positions in group_positions.values():
    if positions != list(range(len(instance_order))):
        ax1.axvline(positions[-1] + 0.5,color="black", linewidth=0.5,alpha=0.35)
ax1.grid(axis="y", alpha=0.2)

# b) Success per instance (mean of 3 seeds)
heatmap_data = success_data[VARIANTS].to_numpy(dtype=float)
success_cmap = LinearSegmentedColormap.from_list("success_blue",["#E8F1F4", "#77B4C7", "#0A5B89", "#004368"])
im = ax2.imshow(heatmap_data,aspect="auto",cmap=success_cmap, vmin=0,vmax=100)

ax2.set_xticks([0, 1])
ax2.set_xticklabels(["A (Swap)", "B (Insertion)"])
ax2.set_yticks(x)
ax2.set_yticklabels(instance_order)
ax2.set_title("(b) Success rate per instance", fontweight="bold")
ax2.set_xlabel("Neighborhood")

cbar = fig.colorbar(im,ax=ax2,fraction=0.08,pad=0.04)
cbar.set_label("Success rate (%)", fontsize=13)
cbar.ax.tick_params(labelsize=10)

# Separate instance groups
for positions in group_positions.values():
    ax2.axhline(positions[-1] + 0.5,color="black",linewidth=0.7)

#c) candidate evaluations vs gap to optimal
for variant in VARIANTS:
    ax3.scatter(evaluation_data[variant], gap_data[variant], color=COLORS[variant], label=variant.capitalize(), alpha=0.8, s=45, edgecolors="white", linewidths=0.5)

ax3.set_xlabel("Mean candidate evaluations per run")
ax3.set_ylabel("Mean gap (%)")
ax3.set_title("(c) Mean candidate evaluations vs mean gap", fontweight="bold")
ax3.legend(frameon=False)
ax3.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value / 1e6:.1f}"))
ax3.set_xlabel("Mean candidate evaluations (millions)")
ax3.grid(alpha=0.2)

#export
fig.tight_layout(w_pad=1.5)
figures = os.path.join(output, "figures")
os.makedirs(figures, exist_ok=True)
fig.savefig(os.path.join(figures, "local_search_instance_comparison.png"),bbox_inches="tight")

