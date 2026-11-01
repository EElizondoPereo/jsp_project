from jsp.instance import Instance

def branch_all_jobs(instance: Instance, job_next, job_ready = None, machine_free = None):
  n_machines = instance.n_machines
  candidates = []
  for i, next in enumerate(job_next):
    if next < n_machines:
      candidates.append(i)
  return candidates

def giffler_thompson_branch(instance: Instance, job_next, job_ready, machine_free):
  jobs = instance.jobs
  c_star, m_star = float('inf'), None
  for j, k in enumerate(job_next):
   
    if k >= instance.n_machines:
      continue
    
    m, d  = jobs[j][k]
    c = max(job_ready[j], machine_free[m]) + d

    if c < c_star:
      c_star, m_star = c, m
  
  candidates = []
  for j, k in  enumerate(job_next):
    if k >= instance.n_machines:
      continue
    m, _ = jobs[j][k]
    head = max(job_ready[j], machine_free[m])
    if m == m_star and head < c_star:
      candidates.append(j)
  
  return candidates

BRANCHING = {"all": branch_all_jobs, "gt": giffler_thompson_branch}