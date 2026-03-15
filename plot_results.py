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



# import pandas as pd
# import matplotlib.pyplot as plt

# df = pd.read_csv("results/results.csv")


# # 1 Response Time vs Users (with CI)
# plt.errorbar(df["users"],
#              df["response_time"],
#              yerr=df["ci"],
#              marker='o')

# plt.xlabel("Number of Users")
# plt.ylabel("Average Response Time")
# plt.title("Response Time vs Number of Users")
# plt.savefig("results/response_time.png")
# plt.clf()


# # 2 Throughput vs Users
# plt.plot(df["users"], df["throughput"], marker='o')
# plt.xlabel("Number of Users")
# plt.ylabel("Throughput")
# plt.title("Throughput vs Number of Users")
# plt.savefig("results/throughput.png")
# plt.clf()


# 3 Goodput vs Users
plt.plot(df["users"], df["goodput"], marker='o')
plt.xlabel("Number of Users")
plt.ylabel("Goodput")
plt.title("Goodput vs Number of Users")
plt.savefig("results/goodput.png")
plt.show()


# 4 Badput vs Users
plt.plot(df["users"], df["badput"], marker='o')
plt.xlabel("Number of Users")
plt.ylabel("Badput")
plt.title("Badput vs Number of Users")
plt.savefig("results/badput.png")
plt.show()


# 5 Drop Rate vs Users
plt.plot(df["users"], df["drop_rate"], marker='o')
plt.xlabel("Number of Users")
plt.ylabel("Drop Rate")
plt.title("Request Drop Rate vs Users")
plt.savefig("results/drop_rate.png")
plt.show()


# 6 Core Utilization vs Users
plt.plot(df["users"], df["utilization"], marker='o')
plt.xlabel("Number of Users")
plt.ylabel("Core Utilization")
plt.title("Average Core Utilization vs Users")
plt.savefig("results/utilization.png")
plt.show()