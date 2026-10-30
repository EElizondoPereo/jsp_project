import glob
import sys

sys.path.insert(0, ".")

from jsp.astar import astar
from jsp.instance import read_instance
from jsp.schedule import check_schedule, makespan

# tiny + easy instances: small enough that every variant finishes quickly
PATHS = sorted(glob.glob("instances/tiny/*.txt")) + sorted(glob.glob("instances/generated/easy_*.txt"))
VARIANTS = [(h, b) for b in ("all", "gt") for h in ("h1", "h2", "h3")]


def main():
    failures = 0
    header = f"{'instance':>10} {'best':>5} " + " ".join(f"{b + '/' + h:>9}" for h, b in VARIANTS)
    print("expanded nodes per variant (branching/heuristic)")
    print(header)
    for path in PATHS:
        inst = read_instance(path)
        cells = []
        for h, b in VARIANTS:
            r = astar(inst, time_limit=60.0, heuristic=h, branching=b)
            ok, msg = (False, r["status"]) if r["schedule"] is None else check_schedule(inst, r["schedule"])
            good = (r["status"] == "optimal" and ok and makespan(r["schedule"]) == r["makespan"]
                    and r["makespan"] == inst.best_known)
            if not good:
                failures += 1
                print(f"FAILED {inst.name} {b}/{h}: status={r['status']} makespan={r['makespan']} "
                      f"best_known={inst.best_known} check={msg}")
            cells.append(r["expanded"])
        print(f"{inst.name:>10} {inst.best_known:>5} " + " ".join(f"{c:>9}" for c in cells))
    print("all checks passed" if failures == 0 else f"{failures} check(s) failed")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
