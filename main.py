import pandas as pd
from functions import *

df = pd.read_csv("data_various_machines.csv", skiprows=5)

# Run
data = get_data_from_csv(df)

print(data)

data.to_csv(
    "best_machine_by_die.csv",
    index=False
)