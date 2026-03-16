import pandas as pd
import numpy as np
import os
from simulator import Simulator
import random
import sys

dist = sys.argv[1]

os.makedirs("results", exist_ok=True)

# fixed users
users = 300

# quantum values in milliseconds
quantums = [i for i in range(10, 201, 10)]

runs = 10

rows = []
run_rows = []

for q in quantums:

    rts = []
    thr = []
    good = []
    bad = []
    drop = []
    util = []
    tt = []
    tau = []

    for i in range(runs):

        np.random.seed(i)
        random.seed(i)

        sim = Simulator(
            users=users,
            cores=4,
            service_dist=dist,
            quantum=q/1000.0  # convert ms → seconds
        )

        m = sim.run()

        if m:

            rts.append(m["response_time"])
            thr.append(m["throughput"])
            good.append(m["goodput"])
            bad.append(m["badput"])
            drop.append(m["drop_rate"])
            util.append(m["utilization"])

            # derived metrics
            think_exp = (users / m["throughput"]) - m["response_time"]
            tau_exp = (m["utilization"] * 4) / m["throughput"]

            tt.append(think_exp)
            tau.append(tau_exp)

            # store per-run data
            run_rows.append({
                "users": users,
                "quantum_ms": q,
                "run": i,
                "response_time": m["response_time"],
                "throughput": m["throughput"],
                "goodput": m["goodput"],
                "badput": m["badput"],
                "drop_rate": m["drop_rate"],
                "utilization": m["utilization"],
                "think_time_experimental": think_exp,
                "tau_experimental": tau_exp
            })

    mean = np.mean(rts)
    std = np.std(rts, ddof=1)
    ci = 1.96 * std / np.sqrt(runs)

    rows.append({
        "users": users,
        "quantum_ms": q,
        "response_time": mean,
        "ci": ci,
        "throughput": np.mean(thr),
        "goodput": np.mean(good),
        "badput": np.mean(bad),
        "drop_rate": np.mean(drop),
        "utilization": np.mean(util),
        "think_time_experimental": np.mean(tt),
        "tau_experimental": np.mean(tau)
    })


# summary results
df_summary = pd.DataFrame(rows)
df_summary.to_csv("results/results_quantum_summary.csv", index=False)

# per-run results
df_runs = pd.DataFrame(run_rows)
df_runs.to_csv("results/results_quantum_runs.csv", index=False)

print(df_summary)
