import pandas as pd
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import sys, os
from functions import *


# This is yet to be implemented. At the moment it takes the last for the machine but only issue is takes 
# the last per machine now averaging and also when there is average on the last machine it does not
# save it when is different die (?)

def get_data_from_csv(df):
    """
    Extracts machine performance data from an AVANTE export dataframe and
    organizes it by die number.

    The function processes the raw CSV structure, identifies die records,
    groups machine performance data under each die, and stores the latest
    available values for each machine.

    Args:
        df (pandas.DataFrame):
            Raw dataframe imported from the AVANTE CSV file.

    Returns:
        dict[int, list[list]]:
            Dictionary where:
            - The key is a die number.
            - The value is a list of machine records.
            - Each machine record contains the machine name followed by
              its associated performance metrics.
    """
    # Dictionary to store all data grouped by die
    dies = {}

    # First die in the file
    current_die = clean_value(df.iloc[0, 0])

    current_machine = clean_value(df.iloc[0, 1])

    # Create an empty list for that die
    if current_die != None:
        dies[current_die] = []

    # List to store all the average data
    avrg_data = []
    total_data = []

    # Loop through every row in the dataframe
    for row in range(len(df)):
        # List to store all the average data
        avrg_data = []
        total_data = []

        # Save the first die
        die = clean_value(df.iloc[row, 0])
        machine = clean_value(df.iloc[row, 1])
        wo = clean_value(df.iloc[row, 2])

        if die is None or die == "":
            continue
        if (
            die == current_die
            and machine is not None
            and current_machine is not None
            and machine != current_machine
        ):
            current_machine = clean_value(df.iloc[row-1, 1])

        # If we are still talking about the same die
        if die == current_die:
            
            # If that value is the die number and the following value is None
            if (die == current_die and wo is None):

                # First we should check if that machine is already saved
                for idx, record in enumerate(dies[current_die]):
                    if record[0] == current_machine:
                        #If it is saved we delete the value and store the new/last one
                        dies[current_die].pop(idx)   
                total_data.append(current_machine)

                # We save the machine those values are for
                for i in range(9):
                    # I get the first value & clean it
                    value = clean_value(df.iloc[row, i+2])
                    # If the value is not None then I save it
                    if value != None:
                        print("Saving:", total_data)
                        total_data.append(value)

                # But then if the following row is empty the machine and wo then we want to save actually that value
                if (
                    row < len(df) - 1
                    and die == current_die
                    and clean_value(df.iloc[row+1, 2]) is None
                    and clean_value(df.iloc[row+1, 3]) is None
                ):   
            
                    # Then we iterate in that line to save those values
                    avrg_data.append(current_machine)
                    for i in range(9):
                        # I get the first value & clean it
                        value = clean_value(df.iloc[row+1, i+2])
                        # If the value is not None then I save it
                        if value != None:
                            print("Saving:", avrg_data)
                            avrg_data.append(value)

            # Just creating the list if there is a value to avoid empty lists
            if current_die is None: 
                continue
            if avrg_data:
                if total_data and total_data[0] is not None:
                    dies[current_die].append(avrg_data.copy())
            elif total_data:
                if total_data and total_data[0] is not None:
                    dies[current_die].append(total_data.copy())

        else:
            current_die = die

            dies[current_die] = []

            # If that value is the die number and the following value is None
            if (die == current_die and wo is None):

                # First we should check if that machine is already saved
                for idx, record in enumerate(dies[current_die]):
                    if record[0] == current_machine:
                        #If it is saved we delete the value and store the new/last one
                        dies[current_die].pop(idx)   
                total_data.append(current_machine)

                # We save the machine those values are for
                for i in range(9):
                    # I get the first value & clean it
                    value = clean_value(df.iloc[row, i+2])
                    # If the value is not None then I save it
                    if value != None:
                        total_data.append(value)

                # But then if the following row is empty the machine and wo then we want to save actually that value
                if (
                    row < len(df) - 1
                    and die == current_die
                    and clean_value(df.iloc[row+1, 2]) is None
                    and clean_value(df.iloc[row+1, 3]) is None
                ):                           
                    # Then we iterate in that line to save those values
                    avrg_data.append(current_machine)
                    for i in range(9):
                        # I get the first value & clean it
                        value = clean_value(df.iloc[row+1, i+2])
                        # If the value is not None then I save it
                        if value != None:
                            avrg_data.append(value)

            # Just creating the list if there is a value to avoid empty lists
            if current_die is None: 
                continue
            if avrg_data:
                if total_data and total_data[0] is not None:
                    dies[current_die].append(avrg_data.copy())
            elif total_data:
                if total_data and total_data[0] is not None:
                    dies[current_die].append(total_data.copy())


    return dies
