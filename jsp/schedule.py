def check_schedule(instance, schedule):
    if len(schedule) != instance.total_ops():
        return False, "wrong number of operations"
    seen = set()
    by_job = {}
    by_machine = {}
    for j, k, m, start, end in schedule:
        if (j, k) in seen:
            return False, f"op ({j},{k}) scheduled twice"
        seen.add((j, k))
        expected_m, d = instance.jobs[j][k]
        if m != expected_m:
            return False, f"op ({j},{k}) on wrong machine"
        if end - start != d or start < 0:
            return False, f"op ({j},{k}) has wrong duration"
        by_job.setdefault(j, []).append((k, start, end))
        by_machine.setdefault(m, []).append((start, end))
    for j, ops in by_job.items():
        ops.sort()
        for (k1, s1, e1), (k2, s2, e2) in zip(ops, ops[1:]):
            if s2 < e1:
                return False, f"precedence broken in job {j}"
    for m, slots in by_machine.items():
        slots.sort()
        for (s1, e1), (s2, e2) in zip(slots, slots[1:]):
            if s2 < e1:
                return False, f"overlap on machine {m}"
    return True, "ok"


def makespan(schedule):
    return max(end for _, _, _, _, end in schedule)
