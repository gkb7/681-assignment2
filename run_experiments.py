import pandas as pd
import numpy as np
import os
from simulator import Simulator
import random
import sys
dist = sys.argv[1]

# if dist == "exp":
#     params = (float(sys.argv[2]),)

# elif dist == "const":
#     params = (float(sys.argv[2]),)

# elif dist == "uniform":
#     params = (float(sys.argv[2]), float(sys.argv[3]))


os.makedirs("results", exist_ok=True)

# users = [i for i in range(10,251,20)]
users = [i for i in range(1,351,50)]


runs = 2

rows = []

for u in users:

    rts=[]
    thr=[]
    good=[]
    bad=[]
    drop=[]
    util=[]

    for i in range(runs):

        np.random.seed(i)
        random.seed(i)
        # sim = Simulator(users=u)
        sim = Simulator(
                users=u,
                cores=4,
                service_dist=dist,
                # service_params=params
        )
        # sim.trace=True

        m = sim.run()

        if m:
            rts.append(m["response_time"])
            thr.append(m["throughput"])
            good.append(m["goodput"])
            bad.append(m["badput"])
            drop.append(m["drop_rate"])
            util.append(m["utilization"])

    mean = np.mean(rts)
    std = np.std(rts, ddof=1)
    ci = 1.96*std/np.sqrt(runs)

    rows.append({
        "users":u,
        "response_time":mean,
        "ci":ci,
        "throughput":np.mean(thr),
        "goodput":np.mean(good),
        "badput":np.mean(bad),
        "drop_rate":np.mean(drop),
        "utilization":np.mean(util)
    })

df=pd.DataFrame(rows)

df.to_csv("results/results.csv",index=False)

print(df)