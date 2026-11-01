import argparse
import csv
import glob
import os
import platform
import random

from jsp.dfs_bb import dfs_bb
from jsp.instance import read_instance
from jsp.schedule import check_schedule, makespan
from jsp.local_search import hill_climbing

FIELDS = [
    "run_id", "instance_id", "family", "n_jobs", "n_machines", "algorithm", "variant", "seed",
    "time_budget_s", "runtime_s", "time_to_best_s", "makespan", "lower_bound", "best_known", "gap_pct",
    "status", "expanded", "generated", "max_frontier", "pruned", "duplicates", "backtracks",
    "iterations", "restarts","candidate_evaluations", "machine", "success",
]

ALGORITHMS = {
    ("dfs_bb", "bound"): lambda inst, budget, seed: dfs_bb(inst, budget, use_bound=True),
    ("dfs_bb", "no_bound"): lambda inst, budget, seed: dfs_bb(inst, budget, use_bound=False),
    ("hill_climbing", "swap"): lambda inst, budget, seed: hill_climbing(inst, time_limit=budget, seed=seed, neighborhood="swap"),
    ("hill_climbing", "insertion"): lambda inst, budget, seed: hill_climbing(inst, time_limit=budget, seed=seed, neighborhood="insertion"),
}


def machine_info():
    return f"{platform.processor() or platform.machine()} | Python {platform.python_version()}"


def run_one(path, algorithm, variant, seed, budget):
    instance = read_instance(path)
    random.seed(seed)
    result = ALGORITHMS[(algorithm, variant)](instance, budget, seed)
    if result["schedule"] is not None:
        ok, message = check_schedule(instance, result["schedule"])
        if not ok or makespan(result["schedule"]) != result["makespan"]:
            raise RuntimeError(f"invalid schedule on {instance.name}: {message}")
    best = instance.best_known
    gap = None
    if best and result["makespan"] is not None:
        gap = round(100 * (result["makespan"] - best) / best, 2)
    family = path.replace("\\", "/").split("/")[-2]
    return {
        "run_id": f"{instance.name}__{algorithm}__{variant}__s{seed}",
        "instance_id": instance.name,
        "family": family,
        "n_jobs": instance.n_jobs,
        "n_machines": instance.n_machines,
        "algorithm": algorithm,
        "variant": variant,
        "seed": seed,
        "time_budget_s": budget,
        "runtime_s": round(result["runtime_s"], 3),
        "time_to_best_s": None if result["time_to_best_s"] is None else round(result["time_to_best_s"], 3),
        "makespan": result["makespan"],
        "lower_bound": instance.trivial_lower_bound(),
        "best_known": best,
        "gap_pct": gap,
        "status": result["status"],
        "expanded": result.get("expanded"),
        "generated": result.get("generated"),
        "max_frontier": result.get("max_frontier"),
        "pruned": result.get("pruned"),
        "duplicates": result.get("duplicates"),
        "backtracks": result.get("backtracks"),
        "iterations": result.get("iterations"),
        "restarts": result.get("restarts"),
        "candidate_evaluations": result.get("candidate_evaluations"),
        "machine": machine_info(),
        "success": (None if best is None or result["makespan"] is None
                    else int(result["makespan"] == best)
                    ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--instances", nargs="+", default=["instances/tiny"])
    parser.add_argument("--algorithm", default="dfs_bb")
    parser.add_argument("--variants", nargs="+", default=["bound"])
    parser.add_argument("--seeds", nargs="+", type=int, default=[0])
    parser.add_argument("--budget", type=float, default=60.0)
    parser.add_argument("--out", default="results/runs.csv")
    args = parser.parse_args()

    paths = []
    for item in args.instances:
        paths.extend(sorted(glob.glob(f"{item}/*.txt")) if os.path.isdir(item) else [item])

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    new_file = not os.path.exists(args.out)
    with open(args.out, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        for path in paths:
            for variant in args.variants:
                for seed in args.seeds:
                    row = run_one(path, args.algorithm, variant, seed, args.budget)
                    writer.writerow(row)
                    f.flush()
                    print(f"{row['instance_id']:>10} {variant:>16} "
                          f"ms={row['makespan']} best={row['best_known']} "
                          f"status={row['status']} t={row['runtime_s']}s "
                          f"exp={row['expanded']} frontier={row['max_frontier']} "
                          f"iterations={row['iterations']} restarts={row['restarts']} "
                          f"evaluations={row['candidate_evaluations']}" )


if __name__ == "__main__":
    main()


