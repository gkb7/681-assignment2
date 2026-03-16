import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results/results_quantum_summary.csv")

# 1 Response Time vs Quantum (with CI)
plt.errorbar(df["quantum_ms"],
             df["response_time"],
             yerr=df["ci"],
             marker='o')

plt.xlabel("Quantum (ms)")
plt.ylabel("Avg Response Time (s)")
plt.title("Response Time vs Quantum")
plt.grid(True)
plt.savefig("results/quantum_response_time.png")
plt.show()


# 2 Throughput vs Quantum
plt.plot(df["quantum_ms"], df["throughput"], marker='o')
plt.xlabel("Quantum (ms)")
plt.ylabel("Throughput (req/s)")
plt.title("Throughput vs Quantum")
plt.grid(True)
plt.savefig("results/quantum_throughput.png")
plt.show()


# 3 Goodput vs Quantum
plt.plot(df["quantum_ms"], df["goodput"], marker='o')
plt.xlabel("Quantum (ms)")
plt.ylabel("Goodput (req/s)")
plt.title("Goodput vs Quantum")
plt.grid(True)
plt.savefig("results/quantum_goodput.png")
plt.show()


# 4 Badput vs Quantum
plt.plot(df["quantum_ms"], df["badput"], marker='o')
plt.xlabel("Quantum (ms)")
plt.ylabel("Badput (req/s)")
plt.title("Badput vs Quantum")
plt.grid(True)
plt.savefig("results/quantum_badput.png")
plt.show()


# 5 Drop Rate vs Quantum
plt.plot(df["quantum_ms"], df["drop_rate"], marker='o')
plt.xlabel("Quantum (ms)")
plt.ylabel("Drop Rate (fraction)")
plt.title("Drop Rate vs Quantum")
plt.grid(True)
plt.savefig("results/quantum_drop_rate.png")
plt.show()


# 6 Utilization vs Quantum
plt.plot(df["quantum_ms"], df["utilization"], marker='o')
plt.xlabel("Quantum (ms)")
plt.ylabel("Core Utilization")
plt.title("Core Utilization vs Quantum")
plt.grid(True)
plt.savefig("results/quantum_utilization.png")
plt.show()