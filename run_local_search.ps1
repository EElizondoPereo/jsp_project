python run_experiments.py `
    --instances instances/tiny instances/generated instances/benchmarks `
    --algorithm hill_climbing `
    --variants swap insertion `
    --seeds 0 1 2 `
    --budget 60 `
    --out results/local_search_final.csv
