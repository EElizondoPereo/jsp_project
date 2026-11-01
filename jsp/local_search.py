import random
import time
from jsp.schedule import makespan

#To generate a random sequence that contains one job ID for every operation in the instance
def generate_initial_sequence (instance, rng):
    sequence= []

    for job_id, job in enumerate(instance.jobs):
        sequence.extend([job_id]*len(job))

    rng.shuffle(sequence)
    return sequence

def decode_sequence(instance, sequence):
    job_next = [0] * instance.n_jobs
    job_ready = [0] * instance.n_jobs
    machine_free = [0]* instance.n_machines

    schedule = []

    for job_id in sequence:
        operation_index = job_next[job_id]
        job = instance.jobs[job_id]

        if operation_index>= len(job):
            raise ValueError(
                f"Too many occurences of job {job_id}"
            )
        machine, duration = job[operation_index]

        start = max (job_ready[job_id],machine_free[machine])
        end = start + duration

        schedule.append((job_id, operation_index,machine,start,end))

        job_ready[job_id] = end
        machine_free[machine] = end
        job_next[job_id] += 1

    for job_id, job in enumerate(instance.jobs):
        if job_next[job_id]!= len(job):
            raise ValueError(f"Missing operations for job {job_id}")
    
    return schedule

# Neighborhood A: Swap
def generate_swap_neighbor(sequence,rng):

    if len(set(sequence)) <2:
        return sequence.copy()
    i, j = rng.sample(range(len(sequence)),2)

    while sequence[i] == sequence[j]:
        i, j, = rng.sample(range(len(sequence)),2)
    
    neighbor = sequence.copy()
    neighbor[i], neighbor[j] = neighbor[j], neighbor[i]

    return neighbor

#Neighborhood B: Insertion
def generate_insertion_neighbor(sequence, rng):
    if len(sequence)< 2:
        return sequence.copy()

    i, j = rng.sample(range(len(sequence)), 2)
    neighbor = sequence.copy()
    job_id = neighbor.pop(i)
    neighbor.insert(j,job_id)

    return neighbor

def generate_neighbor(sequence, rng, neighborhood="swap"):
    if neighborhood == "swap":
        return generate_swap_neighbor(sequence,rng)
    elif neighborhood == "insertion":
        return generate_insertion_neighbor(sequence, rng)
    else:
        raise ValueError(f"Unknown neighborhood: {neighborhood}")

# Multi-start Hill Climbing
def hill_climbing(instance,time_limit=60,seed = 0,neighbors_per_iteration = 50, neighborhood="swap"):
    start_time = time.perf_counter()
    rng= random.Random(seed)

    best_sequence = None
    best_schedule = None
    best_makespan = float("inf")
    time_to_best = 0.0

    iterations = 0
    candidate_evaluations = 0
    restarts = 0

    first_start = True

    while time.perf_counter() - start_time < time_limit:
        if not first_start:
            restarts +=1

        first_start = False

        #Generate a new random starting solution
        current_sequence = generate_initial_sequence(instance,rng)
        current_schedule = decode_sequence(instance, current_sequence)
        current_makespan = makespan(current_schedule)
        candidate_evaluations +=1

        if current_makespan<best_makespan:
            best_sequence = current_sequence.copy()
            best_schedule = current_schedule
            best_makespan = current_makespan
            time_to_best = time.perf_counter() - start_time

        while time.perf_counter() - start_time<time_limit:
            neighbors = []

            for _ in range(neighbors_per_iteration):
                if time.perf_counter() - start_time>= time_limit:
                    break

                neighbor_sequence = generate_neighbor(current_sequence,rng, neighborhood)

                # ignore if the movement did not change the sequence
                if neighbor_sequence == current_sequence:
                    continue

                
                neighbor_schedule = decode_sequence(instance, neighbor_sequence)
                neighbor_makespan = makespan(neighbor_schedule)
                candidate_evaluations +=1

                neighbors.append((neighbor_makespan,neighbor_sequence,neighbor_schedule)
                )
                
            # if no valid neighbors were generated
            if not neighbors:
                break

            # to select the best neighbor (lowest makespan)
            candidate_makespan, candidate_sequence, candidate_schedule = min(neighbors, key=lambda candidate: candidate[0])

            # stop this run if no improvement
            if candidate_makespan >= current_makespan:
                break

            # if improved, then update ccurrent with candidate
            current_sequence = candidate_sequence
            current_schedule = candidate_schedule
            current_makespan = candidate_makespan
            iterations+=1

            #update if best solution (global)
            if current_makespan < best_makespan:
                best_sequence = current_sequence.copy()
                best_schedule = current_schedule
                best_makespan = current_makespan
                time_to_best = time.perf_counter() - start_time
            
    runtime = time.perf_counter() - start_time

    return {
        "makespan": best_makespan,
        "schedule": best_schedule,
        "sequence": best_sequence,
        "status": "time_limit",
        "runtime_s": runtime,
        "time_to_best_s": time_to_best,
        "iterations": iterations,
        "candidate_evaluations": candidate_evaluations,
        "restarts" : restarts
    }


# test block
if __name__ == "__main__":
    from jsp.instance import read_instance
    from jsp.schedule import check_schedule, makespan

    instance = read_instance("instances/generated/easy_01.txt")
    for neighborhood in["swap", "insertion"]:
        print(f"\n---Multi-start Hill Climbing: {neighborhood}---")

        result = hill_climbing(
            instance, time_limit = 10, 
            seed = 42, 
            neighbors_per_iteration= 50,
            neighborhood=neighborhood
        )

        print("Best makespan:", result["makespan"])
        print("Status:", result["status"])
        print("Runtime (s):", round(result["runtime_s"], 3))
        print("Time to best (s):", round(result["time_to_best_s"], 3))
        print("Iterations:", result["iterations"])
        print("Restarts:", result["restarts"])
        print("Candidate evaluations:", result["candidate_evaluations"])

        print(
            "Schedule validation:",
            check_schedule(instance, result["schedule"])
        )

   