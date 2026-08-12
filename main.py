import pandas as pd
from functions import *

df = pd.read_csv("data.csv", skiprows=6)

def analyse_file(df):

    machine_data = {}
    dies = {}

    current_die = clean_value(df.iloc[0, 0])
    dies[current_die] = []
    print(current_die)


    for row in df:
        if current_die == row:
            for i in range (9):
                value = df.iloc[row, i]
                current_die.append(clean_value(value))
            print(row, df.iloc[row, i].tolist())

        else:
            current_die = row
            dies[current_die] = []
                
    return dies


# Run

output = analyse_file(df)

print(output)

output.to_csv(
    "best_machine_by_die.csv",
    index=False
)