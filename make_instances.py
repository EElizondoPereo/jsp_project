import os

from jsp.generator import generate_instance
from jsp.instance import Instance, write_instance

TINY = [
    ("tiny_01", 3, 3, 1, 9, 11),
    ("tiny_02", 3, 4, 1, 9, 12),
    ("tiny_03", 4, 3, 1, 9, 13),
    ("tiny_04", 4, 4, 1, 9, 14),
    ("tiny_05", 5, 4, 1, 9, 15),
]

GENERATED = (
    [(f"easy_{i:02d}", *size, 1, 10, 100 + i) for i, size in enumerate([(4, 4), (5, 4), (5, 5)] * 4, start=1)][:10]
    + [(f"medium_{i:02d}", *size, 1, 20, 200 + i) for i, size in enumerate([(6, 6), (8, 6), (8, 8)] * 3, start=1)][:8]
    + [("hard_01", 10, 10, 1, 99, 301), ("hard_02", 15, 10, 1, 99, 302)]
)

BENCHMARKS = ["ft06", "ft10", "la01", "la02", "la03", "la04", "la05",
              "la16", "la17", "la18", "la19", "la20", "ta01", "ta02", "ta03", "ta04", "ta05"]


def hand_made_toy():
    jobs = [
        [(0, 3), (1, 2), (2, 2)],
        [(0, 2), (2, 1), (1, 4)],
        [(1, 4), (2, 3), (0, 1)],
    ]
    return Instance("toy_3x3", 3, 3, jobs)


def main():
    os.makedirs("instances/tiny", exist_ok=True)
    os.makedirs("instances/generated", exist_ok=True)
    os.makedirs("instances/benchmarks", exist_ok=True)

    write_instance(hand_made_toy(), "instances/tiny/toy_3x3.txt")
    for name, n_jobs, n_machines, low, high, seed in TINY:
        write_instance(generate_instance(name, n_jobs, n_machines, low, high, seed), f"instances/tiny/{name}.txt")
    for name, n_jobs, n_machines, low, high, seed in GENERATED:
        write_instance(generate_instance(name, n_jobs, n_machines, low, high, seed), f"instances/generated/{name}.txt")

    try:
        from job_shop_lib.benchmarking import load_benchmark_instance
    except ImportError:
        print("job_shop_lib not installed, skipping benchmarks (pip install job-shop-lib)")
        return
    for name in BENCHMARKS:
        b = load_benchmark_instance(name)
        jobs = [[(op.machine_id, op.duration) for op in job] for job in b.jobs]
        best = b.metadata.get("optimum") or b.metadata.get("upper_bound")
        write_instance(Instance(name, b.num_jobs, b.num_machines, jobs, best), f"instances/benchmarks/{name}.txt")


if __name__ == "__main__":
    main()
