import heapq

def job_bound(instance, job_next, job_ready):
  n_machines = instance.n_machines
  jobs = instance.jobs
  best = 0
  for j, k in enumerate(job_next):
    if k >= n_machines:
      continue
    #remaining_operations = [d for m, d in jobs[j][k:]]
    remaining = compute_remaining(jobs[j], k)
    best = max(best, remaining + job_ready[j])
  return best

def compute_remaining(job, index):
  return sum([d for m, d in job[index:]])


def one_machine_bound(instance, job_next, job_ready, machine_free):
  heads = {}
  tails = {}
  loads = {}

  jobs = instance.jobs
  for j, k in enumerate(job_next):

   # if k >= instance.n_machines:
   #   continue

    t = job_ready[j]
    remaining = compute_remaining(jobs[j], k)
    for m, d in jobs[j][k:]:
      remaining -= d
      heads[m] = min(heads.get(m, t), t)
      tails[m] = min(tails.get(m, remaining), remaining)
      loads[m] = loads.get(m, 0) + d
      t += d

  best = 0
  for m, load in loads.items():
    earliest_start = max(heads[m], machine_free[m])
    machine_bound = earliest_start + load + tails[m]
    best = max(best, machine_bound)
  return best


def machine_ops(instance, job_next, job_ready, machine_free):
  jobs = instance.jobs

  ops = {}
  for j, job in enumerate(jobs):
    k = job_next[j]
    tail = compute_remaining(job, k)
    head = job_ready[j]
    for m, d in job[k:]:
      tail -= d
      head = max(head, machine_free[m])
      current_op = (head, d, tail)
      ops.setdefault(m, []).append(current_op)
      head += d
  return ops

def jackson_preemptive(om_ops):
  om_ops = sorted(om_ops)
  best = 0
  time = 0
  i = 0
  avail_ops = []
  while avail_ops or i < len(om_ops):
    if not avail_ops:
      time = max(time, om_ops[i][0])
    while i < len(om_ops) and om_ops[i][0] <= time:
      heapq.heappush(avail_ops, (-om_ops[i][2], om_ops[i][1]))
      i += 1

    tail, d = heapq.heappop(avail_ops)
    time_next = om_ops[i][0] if i < len(om_ops) else float('inf')
    run = min(time_next - time, d)
    time += run

    if run < d:
      heapq.heappush(avail_ops, (tail, d - run))
    else:
      tail = -tail
      best = max(best, time + tail)
  return best

def jackson_bound(instance, job_next, job_ready, machine_free):
  ops = machine_ops(instance, job_next, job_ready, machine_free)
  best = 0
  for om_ops in ops.values():
    best = max(best, jackson_preemptive(om_ops))
  return best

  
def h1(instance, job_next, job_ready, machine_free, g):
  bound = job_bound(instance, job_next, job_ready)
  lb = bound - g
  return max(0, lb)

def h2(instance, job_next, job_ready, machine_free, g):
  j_bound = job_bound(instance, job_next, job_ready)
  om_bound = one_machine_bound(instance, job_next, job_ready, machine_free)
  lb = max(j_bound, om_bound)
  return max(0, lb - g)

def h3(instance, job_next, job_ready, machine_free, g):
  j_bound = job_bound(instance, job_next, job_ready)
  jack_bound = jackson_bound(instance, job_next, job_ready, machine_free)
  lb = max(j_bound, jack_bound)
  return max(0, lb - g)

HEURISTICS = {"h1": h1, "h2": h2, "h3": h3}