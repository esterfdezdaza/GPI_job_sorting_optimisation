import pandas as pd
from functions import *

df = pd.read_csv("data_various_machines.csv", skiprows=5)

# Run
data = get_data_from_csv(df)

ranking = analyse_data(data)

print(ranking)


rows = []

for die, machines in ranking.items():

    row = {"Die": die}

    for i, machine in enumerate(machines, start=1):
        row[f"Machine {i}"] = machine

    rows.append(row)

df = pd.DataFrame(rows)

df.to_csv("machine_ranking.csv", index=False)


