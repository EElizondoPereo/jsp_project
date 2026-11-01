import glob
import random
import sys
import time

sys.path.insert(0, ".")

from jsp.bounds import h1, h2, h3, job_bound, machine_ops, one_machine_bound
from jsp.instance import read_instance


def simple_bound(instance, job_next, job_ready, machine_free):
    """Machine bound written with machine_ops: min head + total work + min tail.
    It is the same quantity as bounds.one_machine_bound, which this test confirms."""
    best = 0
    for ops in machine_ops(instance, job_next, job_ready, machine_free).values():
        best = max(best, min(r for r, _, _ in ops) + sum(p for _, p, _ in ops) + min(q for _, _, q in ops))
    return best


def random_walk_check(instance, walks, rng):
    for _ in range(walks):
        job_next = [0] * instance.n_jobs
        job_ready = [0] * instance.n_jobs
        machine_free = [0] * instance.n_machines
        g = 0
        last1 = h1(instance, job_next, job_ready, machine_free, g)
        last2 = h2(instance, job_next, job_ready, machine_free, g)
        last3 = h3(instance, job_next, job_ready, machine_free, g)
        for _ in range(instance.total_ops()):
            j = rng.choice([j for j in range(instance.n_jobs) if job_next[j] < instance.n_machines])
            m, d = instance.jobs[j][job_next[j]]
            start = max(job_ready[j], machine_free[m])
            end = start + d
            step = max(g, end) - g
            job_next[j] += 1
            job_ready[j] = end
            machine_free[m] = end
            g = max(g, end)
            v1 = h1(instance, job_next, job_ready, machine_free, g)
            v2 = h2(instance, job_next, job_ready, machine_free, g)
            v3 = h3(instance, job_next, job_ready, machine_free, g)
            if last1 > step + v1 or last2 > step + v2 or last3 > step + v3 or v1 > v2 or v2 > v3:
                return False
            if simple_bound(instance, job_next, job_ready, machine_free) != one_machine_bound(instance, job_next, job_ready, machine_free):
                return False
            last1, last2, last3 = v1, v2, v3
        if last1 != 0 or last2 != 0 or last3 != 0:
            return False
    return True


def timing(instance, fn, repeat=2000):
    job_next = [0] * instance.n_jobs
    job_ready = [0] * instance.n_jobs
    machine_free = [0] * instance.n_machines
    t0 = time.perf_counter()
    for _ in range(repeat):
        fn(instance, job_next, job_ready, machine_free, 0)
    return (time.perf_counter() - t0) / repeat * 1e6


def main():
    rng = random.Random(0)
    print(f"{'instance':>10} {'size':>6} {'opt':>5} {'H1(root)':>9} {'H2(root)':>9} {'H3(root)':>9} {'consistent':>10} {'H1 us':>7} {'H2 us':>7} {'H3 us':>7}")
    for folder in ["instances/tiny", "instances/generated", "instances/benchmarks"]:
        for path in sorted(glob.glob(f"{folder}/*.txt")):
            inst = read_instance(path)
            zero_j = [0] * inst.n_jobs
            zero_m = [0] * inst.n_machines
            r1 = h1(inst, zero_j, zero_j, zero_m, 0)
            r2 = h2(inst, zero_j, zero_j, zero_m, 0)
            r3 = h3(inst, zero_j, zero_j, zero_m, 0)
            if inst.best_known is not None and (r1 > inst.best_known or r2 > inst.best_known or r3 > inst.best_known):
                print(f"NOT ADMISSIBLE at root on {inst.name}")
            ok = random_walk_check(inst, 50, rng)
            print(f"{inst.name:>10} {inst.n_jobs}x{inst.n_machines:<3} {inst.best_known:>5} {r1:>9} {r2:>9} {r3:>9} "
                  f"{str(ok):>10} {timing(inst, h1):>7.1f} {timing(inst, h2):>7.1f} {timing(inst, h3):>7.1f}")


if __name__ == "__main__":
    main()
