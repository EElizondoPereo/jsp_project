import heapq
import math


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


def machine_ops(instance, job_next, job_ready, machine_free):
    """For each machine, its unscheduled ops as (head r, duration p, tail q).

    r: earliest possible start (job ready time plus the work before it in the job,
       but not before the machine is free)
    q: work that must still follow the op inside its own job
    """
    ops = {}
    for j, job in enumerate(instance.jobs):
        t = job_ready[j]
        rest = sum(d for _, d in job[job_next[j]:])
        for m, d in job[job_next[j]:]:
            rest -= d
            ops.setdefault(m, []).append((max(t, machine_free[m]), d, rest))
            t += d
    return ops


def jackson_preemptive(ops):
    """Optimal makespan (completion + tail) of the preemptive one-machine relaxation.
    At every moment the released op with the largest tail runs (Jackson's rule)."""
    ops = sorted(ops)
    i, t, best = 0, 0, 0
    avail = []  # max-heap on tail through negation: (-q, remaining p)
    while i < len(ops) or avail:
        if not avail:
            t = max(t, ops[i][0])
        while i < len(ops) and ops[i][0] <= t:
            heapq.heappush(avail, (-ops[i][2], ops[i][1]))
            i += 1
        neg_q, p = heapq.heappop(avail)
        next_release = ops[i][0] if i < len(ops) else math.inf
        run = min(p, next_release - t)
        t += run
        if run < p:
            heapq.heappush(avail, (neg_q, p - run))   # preempted by a new arrival
        else:
            best = max(best, t - neg_q)               # completion time + tail
    return best


def jackson_bound(instance, job_next, job_ready, machine_free):
    best = 0
    for ops in machine_ops(instance, job_next, job_ready, machine_free).values():
        best = max(best, jackson_preemptive(ops))
    return best


def h3(instance, job_next, job_ready, machine_free, g):
    lb = max(job_bound(instance, job_next, job_ready),
             jackson_bound(instance, job_next, job_ready, machine_free))
    return max(0, lb - g)
