import glob
import sys

from ortools.sat.python import cp_model

from jsp.instance import read_instance, write_instance


def solve_reference(instance, time_limit=60.0):
    model = cp_model.CpModel()
    horizon = sum(d for job in instance.jobs for _, d in job)
    starts, ends = {}, {}
    machine_intervals = {m: [] for m in range(instance.n_machines)}
    for j, job in enumerate(instance.jobs):
        for k, (m, d) in enumerate(job):
            s = model.NewIntVar(0, horizon, f"s{j}_{k}")
            e = model.NewIntVar(0, horizon, f"e{j}_{k}")
            machine_intervals[m].append(model.NewIntervalVar(s, d, e, f"i{j}_{k}"))
            starts[j, k], ends[j, k] = s, e
            if k > 0:
                model.Add(s >= ends[j, k - 1])
    for intervals in machine_intervals.values():
        model.AddNoOverlap(intervals)
    cmax = model.NewIntVar(0, horizon, "cmax")
    model.AddMaxEquality(cmax, [ends[j, instance.n_machines - 1] for j in range(instance.n_jobs)])
    model.Minimize(cmax)
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.random_seed = 0
    solver.parameters.num_workers = 1
    result = solver.Solve(model)
    return int(solver.Value(cmax)), result == cp_model.OPTIMAL


def main():
    folders = sys.argv[1:] or ["instances/tiny", "instances/generated"]
    for folder in folders:
        for path in sorted(glob.glob(f"{folder}/*.txt")):
            instance = read_instance(path)
            value, proven = solve_reference(instance)
            instance.best_known = value
            write_instance(instance, path)
            print(f"{instance.name}: {value} ({'optimal' if proven else 'best found'})")


if __name__ == "__main__":
    main()
