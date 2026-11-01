# TC6001 – Job-Shop Scheduling project

Uninformed search, Informed search-heuristics and local search for the classic job-shop problem (minimize makespan).
Status: (baseline DFS + branch-and-bound, H1/H2/H3 bounds, A* (formulation A and Giffler-Thompson), Multi-start hill climbing, instances, logging, plotting).

## Setup

Python 3.10+.

```
pip install -r requirements.txt
```

`ortools` is only used to compute reference optima for our own instances (`reference_optima.py`).
`job-shop-lib` is only used once, to export the OR-Library benchmarks to text files.
Neither is one of our four methods.

## Instances
```
python make_instances.py
python reference_optima.py
```
| Folder | Content | Size | Processing times |
| --- | --- | --- | --- |
| instances/tiny | toy_3x3 (hand-made) + tiny_01–05 | 3×3 to 5×4 | 1–9 |
| instances/generated | easy_01–10, medium_01–08, hard_01–02 | 4×4–5×5, 6×6–8×8, 10×10 and 15×10 | 1–10, 1–20, 1–99 |
| instances/benchmarks | ft06, ft10, la01–05, la16–20, ta01–05 | 6×6 to 15×15 | 1–99 |

Generated instances use `jsp/generator.py`: each job visits every machine once in a random order,
durations are uniform integers. The seed of each instance is fixed in `make_instances.py`.

File format (OR-Library style): lines starting with `#` are comments (`# best_known = 55`),
then `n_jobs n_machines`, then one line per job with `machine duration` pairs in job order.
Machines are numbered from 0.

## Running experiments

The experiment runner supports both individual instance files and directories containing multiple .txt instances. When a directory is provided, all .txt files direclty insided it are included. Experiments can then be executed on individual instances for texting or on complete instances sets for evaluation.

**DFS + Branch-and-Bound**

```
python run_experiments.py --instances instances/tiny --variants bound no_bound --budget 60
python run_experiments.py --instances instances/benchmarks/ft06.txt --variants bound --budget 60
```

**A\***

```
python run_experiments.py --instances instances/benchmarks/ft06.txt --algorithm astar --variants h1 h2 h3 --budget 120
python run_experiments.py --instances instances/benchmarks/ft06.txt --algorithm astar_gt --variants h1 h2 h3 --budget 120
```

**A\* tests**

```
python tests/check_heuristics.py
python tests/check_astar.py
```

**Multi-start Hill Climbing**
```
python run_experiments.py --instances instances/tiny --algorithm hill_climbing --variants swap insertion --seeds 0 1 2 --budget 60
```

The runner accepts the following arguments:

| Argument | Description |
|---|---|
| `--instances` | One or more instance files or directories |
| `--algorithm` | Algorithm to execute (`dfs_bb`, `astar`, `astar_gt`, or `hill_climbing`) |
| `--variants` | Algorithm variants or neighborhood operators |
| `--seeds` | Random seeds for repeated runs |
| `--budget` | Time limit per run, in seconds |
| `--out` | Output CSV file path (default: `results/runs.csv`) |

Every schedule is checked by `jsp/schedule.py` (precedence, no overlap, durations) before it is logged.

## Code map

| File | What it does |
| --- | --- |
| jsp/instance.py | Instance class, read and write files, trivial lower bound |
| jsp/generator.py | Seeded instance generator |
| jsp/schedule.py | Feasibility checker and makespan |
| jsp/dfs_bb.py | Baseline: DFS + branch-and-bound on formulation A |
| jsp/bounds.py | H1 (job bound), H2 (job + one-machine bound), H3 (job bound + Jackson preemptive one-machine bound, built on `machine_ops`) |
| jsp/branching.py | Successor rules: `all` (formulation A) and `gt` (Giffler-Thompson conflict set, active schedules) |
| jsp/astar.py | A* with H1/H2/H3 and `all` or `gt` branching, duplicate detection, memory cap (`memory_limit` status) |
| jsp/local_search.py | Multi-start hill climbing with swap and insertion neighborhoods, sequence representation, and schedule decoding |
| run_experiments.py | Runs algorithms on instance sets and writes the CSV log |
| tests/check_heuristics.py | Checks H1/H2/H3 admissibility at the root, consistency and H1<=H2<=H3 on random paths, and cost per call |
| tests/check_astar.py | Checks the six A* variants (all/gt x H1/H2/H3) return valid optimal schedules matching best_known on tiny and easy instances |
| analize_local_search.py | Analyzes local search experiment results and generate summary CSVs per group size and per instance (mean of seeds), also generates comparison plots |

