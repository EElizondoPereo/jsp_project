import heapq
import time
from jsp.heuristics import HEURISTICS
from jsp.branching import BRANCHING
from jsp.astar_nodes import FrontierNode, ReachedNode
from jsp.instance import Instance
from jsp.dfs_bb import rebuild_schedule

from dataclasses import asdict, dataclass

def astar(instance: Instance, time_limit=60.0, heuristic="h1", branching = "all", max_states=3_000_000):
  t0 = time.perf_counter()
  h = HEURISTICS[heuristic]
  branch = BRANCHING[branching]

  jobs = instance.jobs
  n_machines = instance.n_machines
  n_jobs = instance.n_jobs
  max_depth = instance.total_ops()

  job_next = [0]*n_jobs
  job_ready = [0]*n_jobs
  machine_free = [0]*n_machines

  frontier = []
  reached = {}

  h_root = h(instance, job_next, job_ready, machine_free, 0)
  root = ReachedNode(tuple(job_next), tuple(job_ready), tuple(machine_free))
  
  heapq.heappush(frontier, FrontierNode(h_root, h_root, 0, root))
  reached[root] = h_root
  
  data = DataStore()
  tie = 1
  while frontier:
    node = heapq.heappop(frontier)

    if time.perf_counter() - t0 > time_limit:
      data.status = "timeout"
      break

    if len(reached) > max_states:
      data.status = "memory_limit"
      break

    if node.depth == max_depth:
      data.makespan, data.schedule, data.status = node.g, rebuild_schedule(instance, node.path), "optimal"

      break

    candidates = branch(instance, node.job_next, node.job_ready, node.machine_free)
    data.expanded += 1
    for j in candidates:
      k = node.job_next[j]
      if k >= n_machines:
        continue
      
      data.generated += 1
      m, d = jobs[j][k]

      start = max(node.job_ready[j], node.machine_free[m])
      end = start + d

      new_job_next = node.job_next[:]
      new_job_ready = node.job_ready[:]
      new_machine_free = node.machine_free[:]

      new_job_next[j] += 1
      new_job_ready[j] = end
      new_machine_free[m] = end

      new_reached = ReachedNode(tuple(new_job_next), tuple(new_job_ready), tuple(new_machine_free))

      if new_reached in reached:
        data.duplicates += 1
        continue

      new_g = max(node.g, end)
      reached[new_reached] = new_g


      h_new = h(instance, new_reached.job_next, new_reached.job_ready, new_reached.machine_free, new_g)
      new_node = FrontierNode(new_g + h_new, h_new, tie, new_reached, new_g, node.depth + 1, (j, start, node.path))
      heapq.heappush(frontier, new_node)

      if len(frontier) > data.max_frontier:
        data.max_frontier = len(frontier)

      tie += 1
  
  runtime = time.perf_counter() - t0
  data.runtime_s = runtime
  data.time_to_best_s = runtime if data.makespan is not None else None
  data.states_stored = len(reached)
  return asdict(data)


@dataclass
class DataStore:
  makespan: int = None
  schedule: tuple = None
  status: str = "no_solution"
  runtime_s: float = 0.0
  time_to_best_s: float = None
  states_stored: int = 0
  expanded: int = 0
  generated: int = 1
  pruned: int = 0
  duplicates: int = 0
  max_frontier: int = 1



