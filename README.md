# TC6001 – Job-Shop Scheduling project

Search, heuristics, local search for the classic job-shop problem (minimize makespan).

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

```
python run_experiments.py --instances instances/tiny --variants bound no_bound --budget 60
python run_experiments.py --instances instances/benchmarks/ft06.txt --variants bound --budget 60
python tests/check_heuristics.py
```

Each run appends one row to `results/runs.csv` (fields: see the Session 1 logging schema).
Every schedule is checked by `jsp/schedule.py` (precedence, no overlap, durations) before it is logged.

## Code map

| File | What it does |
| --- | --- |
| jsp/instance.py | Instance class, read and write files, trivial lower bound |
| jsp/generator.py | Seeded instance generator |
| jsp/schedule.py | Feasibility checker and makespan |
| jsp/dfs_bb.py | Baseline: DFS + branch-and-bound on formulation A |
| jsp/bounds.py | H1 (job bound) and H2 (job + one-machine bound) |
| run_experiments.py | Runs algorithms on instance sets and writes the CSV log |
| tests/check_heuristics.py | Checks H1/H2 admissibility at the root, consistency on random paths, and cost per call |

## Still to do

- A* and Weighted A* with H1/H2 (Session 2 ablation grid)
- Multi-start hill climbing with N1/N2 (Session 3 design sheet)
- Plots in results/figures
