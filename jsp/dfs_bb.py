import time


def rebuild_schedule(instance, path):
    actions = []
    while path is not None:
        j, start, path = path
        actions.append((j, start))
    actions.reverse()
    job_next = [0] * instance.n_jobs
    schedule = []
    for j, start in actions:
        k = job_next[j]
        m, d = instance.jobs[j][k]
        schedule.append((j, k, m, start, start + d))
        job_next[j] += 1
    return schedule


def dfs_bb(instance, time_limit=60.0, use_bound=True, use_visited=True, max_visited=2_000_000):
    t0 = time.perf_counter()
    n_jobs = instance.n_jobs
    n_machines = instance.n_machines
    n_ops = instance.total_ops()
    jobs = instance.jobs

    root = (tuple([0] * n_jobs), tuple([0] * n_jobs), tuple([0] * n_machines), 0, 0, None)
    stack = [root]
    visited = set()

    best = float("inf")
    best_path = None
    time_to_best = None
    stats = {"expanded": 0, "generated": 1, "pruned": 0, "duplicates": 0, "max_frontier": 1, "visited_full": False}
    status = None
    counter = 0

    while stack:
        counter += 1
        if counter % 2000 == 0 and time.perf_counter() - t0 > time_limit:
            status = "timeout"
            break

        job_next, job_ready, machine_free, g, depth, path = stack.pop()

        if use_bound and g >= best:
            stats["pruned"] += 1
            continue

        if depth == n_ops:
            if g < best:
                best = g
                best_path = path
                time_to_best = time.perf_counter() - t0
            continue

        if use_visited:
            key = (job_next, job_ready, machine_free)
            if key in visited:
                stats["duplicates"] += 1
                continue
            if len(visited) < max_visited:
                visited.add(key)
            else:
                stats["visited_full"] = True

        stats["expanded"] += 1
        children = []
        for j in range(n_jobs):
            k = job_next[j]
            if k == n_machines:
                continue
            m, d = jobs[j][k]
            start = max(job_ready[j], machine_free[m])
            end = start + d
            new_next = job_next[:j] + (k + 1,) + job_next[j + 1:]
            new_ready = job_ready[:j] + (end,) + job_ready[j + 1:]
            new_free = machine_free[:m] + (end,) + machine_free[m + 1:]
            children.append((new_next, new_ready, new_free, max(g, end), depth + 1, (j, start, path)))
        stats["generated"] += len(children)
        stack.extend(reversed(children))
        if len(stack) > stats["max_frontier"]:
            stats["max_frontier"] = len(stack)

    runtime = time.perf_counter() - t0
    if status is None:
        status = "optimal" if best_path is not None else "no_solution"
    elif best_path is None:
        status = "no_solution"

    schedule = rebuild_schedule(instance, best_path) if best_path is not None else None
    return {
        "makespan": best if best_path is not None else None,
        "schedule": schedule,
        "status": status,
        "runtime_s": runtime,
        "time_to_best_s": time_to_best,
        **stats,
    }
