import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results/results.csv")

plt.errorbar(df["users"],
             df["response_time"],
             yerr=df["ci"],
             marker='o')

plt.xlabel("Users")
plt.ylabel("Avg Response Time")
plt.title("Response Time vs Users")

plt.savefig("results/response_time.png")
plt.show()

plt.plot(df["users"], df["throughput"], marker='o')
plt.xlabel("Users")
plt.ylabel("Throughput")
plt.title("Throughput vs Users")
plt.savefig("results/throughput.png")
plt.show()