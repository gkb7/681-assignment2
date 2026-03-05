import pandas as pd
import numpy as np
import os
from simulator import Simulator

os.makedirs("results", exist_ok=True)

users = [10,20,40,80,120,160,200]

runs = 20

rows = []

for u in users:

    rts=[]
    thr=[]
    util=[]

    for i in range(runs):

        sim = Simulator(users=u)

        m = sim.run()

        if m:
            rts.append(m["response_time"])
            thr.append(m["throughput"])
            util.append(m["utilization"])

    mean = np.mean(rts)
    std = np.std(rts)
    ci = 1.96*std/np.sqrt(runs)

    rows.append({
        "users":u,
        "response_time":mean,
        "ci":ci,
        "throughput":np.mean(thr),
        "utilization":np.mean(util)
    })

df=pd.DataFrame(rows)

df.to_csv("results/results.csv",index=False)

print(df)