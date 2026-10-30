import random

from jsp.instance import Instance


def generate_instance(name, n_jobs, n_machines, low, high, seed):
    rng = random.Random(seed)
    jobs = []
    for _ in range(n_jobs):
        machines = list(range(n_machines))
        rng.shuffle(machines)
        jobs.append([(m, rng.randint(low, high)) for m in machines])
    return Instance(name, n_jobs, n_machines, jobs)
