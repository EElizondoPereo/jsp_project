def job_bound(instance, job_next, job_ready):
    best = 0
    for j, job in enumerate(instance.jobs):
        remaining = sum(d for _, d in job[job_next[j]:])
        best = max(best, job_ready[j] + remaining)
    return best


def one_machine_bound(instance, job_next, job_ready, machine_free):
    heads = {}
    tails = {}
    loads = {}
    for j, job in enumerate(instance.jobs):
        t = job_ready[j]
        rest = sum(d for _, d in job[job_next[j]:])
        for m, d in job[job_next[j]:]:
            rest -= d
            heads[m] = min(heads.get(m, t), t)
            tails[m] = min(tails.get(m, rest), rest)
            loads[m] = loads.get(m, 0) + d
            t += d
    best = 0
    for m, load in loads.items():
        best = max(best, max(machine_free[m], heads[m]) + load + tails[m])
    return best


def h1(instance, job_next, job_ready, machine_free, g):
    return max(0, job_bound(instance, job_next, job_ready) - g)


def h2(instance, job_next, job_ready, machine_free, g):
    lb = max(job_bound(instance, job_next, job_ready),
             one_machine_bound(instance, job_next, job_ready, machine_free))
    return max(0, lb - g)
