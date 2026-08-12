import pandas as pd
from functions import *

df = pd.read_csv("data.csv", skiprows=6)

def analyse_file(df):
    # Dictionary to store all data grouped by die
    dies = {}

    # First die in the file
    current_die = clean_value(df.iloc[0, 0])

    # Create an empty list for that die
    dies[current_die] = []

    # Loop through every row in the dataframe
    for row in range(len(df)):
        # Save the first die
        die = clean_value(df.iloc[row, 0])

        # If we are still talking about the same die
        if die == current_die:

            # List to store all the average data
            avrg_data = []
            
            for j in range(9):
                # Store the value we are in the row 
                value = clean_value(df.iloc[row, j])
                # If that value is the die number and the following value is None
                if (value == current_die) & (clean_value(df.iloc[row, 1]) == None):

                    # Then we iterate in that line to save those values
                    for i in range(9):
                        # I get the first value & clean it
                        value = df.iloc[row, i+1]
                        value = clean_value(value)
                        # If the value is not None then I save it
                        if value != None:
                            avrg_data.append(value)

            dies[current_die].append(avrg_data)
        

        else:
            print("I am here")
            current_die = die

            dies[current_die] = []

            avrg_data = []

            for j in range(9):
                # Store the value we are in the row 
                value = clean_value(df.iloc[row, j])
                # If that value is the die number and the following value is None
                
                if (value == current_die) & (clean_value(df.iloc[row, 1]) == None):
                    # Then we iterate in that line to save those values
                    
                    for i in range(9):
                        # I get the first value & clean it
                        value = df.iloc[row, i+1]
                        value = clean_value(value)
                        # If the value is not None then I save it
                        
                        if value != None:
                            avrg_data.append(value)

            dies[current_die].append(avrg_data)


    return dies


# Run

output = analyse_file(df)

print(output)

output.to_csv(
    "best_machine_by_die.csv",
    index=False
)