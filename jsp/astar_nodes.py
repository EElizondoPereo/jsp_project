from dataclasses import dataclass


@dataclass(frozen=True)
class ReachedNode:
    job_next: tuple
    job_ready: tuple
    machine_free: tuple

class FrontierNode:
  def __init__(self, f, h, tie, job_next, job_ready, machine_free, g = 0, depth = 0, path = None):
    self.f = f
    self.h = h
    self.tie = tie
    self.job_next = job_next
    self.job_ready = job_ready
    self.machine_free = machine_free
    self.g = g
    self.depth = depth
    self.path = path

  def __init__(self, f, h, tie, reached:ReachedNode, g = 0, depth = 0, path = None):
    self.f = f
    self.h = h
    self.tie = tie
    self.job_next = list(reached.job_next)
    self.job_ready = list(reached.job_ready)
    self.machine_free = list(reached.machine_free)
    self.g = g
    self.depth = depth
    self.path = path

  def __lt__(self, other):
    if self.f != other.f:
      return self.f < other.f
    elif self.h != other.h:
      return self.h < other.h
    else:
      return self.tie < other.tie

  def copyReached(self, reached: ReachedNode):
    self.job_next = reached.job_next[:]
    self.job_ready = reached.job_ready[:]
    self.machine_free = reached.machine_free[:]


