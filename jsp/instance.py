from dataclasses import dataclass


@dataclass
class Instance:
    name: str
    n_jobs: int
    n_machines: int
    jobs: list
    best_known: int = None

    def total_ops(self):
        return self.n_jobs * self.n_machines

    def job_lengths(self):
        return [sum(d for _, d in job) for job in self.jobs]

    def machine_loads(self):
        loads = [0] * self.n_machines
        for job in self.jobs:
            for m, d in job:
                loads[m] += d
        return loads

    def trivial_lower_bound(self):
        return max(max(self.job_lengths()), max(self.machine_loads()))

    def duration_range(self):
        durations = [d for job in self.jobs for _, d in job]
        return min(durations), max(durations)


def read_instance(path, name=None):
    best_known = None
    numbers = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                parts = line[1:].split("=")
                if len(parts) == 2 and parts[0].strip() == "best_known":
                    best_known = int(parts[1])
                continue
            numbers.extend(int(x) for x in line.split())
    n_jobs, n_machines = numbers[0], numbers[1]
    values = numbers[2:]
    jobs = []
    for j in range(n_jobs):
        row = values[j * 2 * n_machines:(j + 1) * 2 * n_machines]
        jobs.append([(row[2 * k], row[2 * k + 1]) for k in range(n_machines)])
    if name is None:
        name = path.replace("\\", "/").split("/")[-1].rsplit(".", 1)[0]
    return Instance(name, n_jobs, n_machines, jobs, best_known)


def write_instance(instance, path):
    with open(path, "w") as f:
        f.write(f"# {instance.name}\n")
        if instance.best_known is not None:
            f.write(f"# best_known = {instance.best_known}\n")
        f.write(f"{instance.n_jobs} {instance.n_machines}\n")
        for job in instance.jobs:
            f.write(" ".join(f"{m} {d}" for m, d in job) + "\n")
