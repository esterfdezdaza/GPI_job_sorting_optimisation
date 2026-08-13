import pandas as pd

mr_machines = [("HS2", 47), ("HS3", 46), ("Pick&Place", 58), ("115D", 50), 
              ("Diana", 57), ("110WP", 23), ("INT", 19), ("75", 23), ("110", 50), 
              ("DGM", 35), ("FLAT", 0)]
finaltime = float
real_speed = int

def minutes_to_hours(minutes):
    """it changes from minutes into fractions of an hour

    Args:
        minutes (int): time

    Returns:
        float: amount of hours
    """
    return round(minutes / 60.0, 2)

def finaltime(total_hours_running, machine):
    """It calculates the total time excluding the MR time

    Args:
        total_hours_running (float): raw hours it took to run the job
        machine (string): machine that run the job

    Returns:
        float: the real time it took the machine to run the job
    """
    for mr_machine in mr_machines:

        if mr_machine[0] == machine:
            mr = minutes_to_hours(mr_machine[1])
            total_hours_running = total_hours_running - mr 

    return total_hours_running

def real_speed(finaltime, qty):
    """It calculates the speed of a machine

    Args:
        finaltime (float): how long it took to run them
        qty (int): amount of sheets

    Returns:
        int: the speed it took the machine runnig that amount of sheets
    """
    return round(qty / finaltime)

import pandas as pd

def clean_value(value):
    # Handle NaN/empty values
    if pd.isna(value):
        return None

    # Already a number
    if isinstance(value, (int, float)):
        if float(value).is_integer():
            return int(value)
        return float(value)

    # Handle strings
    value = str(value).strip()

    if value == "":
        return None

    # Remove thousand separators
    value = value.replace(",", "")

    try:
        number = float(value)

        if number.is_integer():
            return int(number)

        return number

    except ValueError:
        return value

def get_data_from_csv(df):
    # Dictionary to store all data grouped by die
    dies = {}

    # First die in the file
    current_die = clean_value(df.iloc[0, 0])

    current_machine = df.iloc[0, 1]

    # Create an empty list for that die
    dies[current_die] = []

    # Loop through every row in the dataframe
    for row in range(len(df)):
        # Save the first die
        die = clean_value(df.iloc[row, 0])
        current_machine = df.iloc[row-1, 1]

        # If we are still talking about the same die
        if die == current_die:

            # List to store all the average data
            avrg_data = []
            
            for j in range(9):
                # Store the value we are in the row 
                value = clean_value(df.iloc[row, j])
                
                # If that value is the die number and the following value is None
                if (value == current_die) & (clean_value(df.iloc[row, 2]) == None):
                    # We save the machine those values are for
                    avrg_data.append(current_machine)

                    # Then we iterate in that line to save those values
                    for i in range(9):
                        # I get the first value & clean it
                        value = df.iloc[row, i+2]
                        value = clean_value(value)
                        # If the value is not None then I save it
                        if value != None:
                            avrg_data.append(value)
            # Just creating the list if there is a value to avoid empty lists
            if avrg_data:
                dies[current_die].append(avrg_data)
        

        else:
            current_die = die

            dies[current_die] = []

            avrg_data = []

            for j in range(9):
                # Store the value we are in the row 
                value = clean_value(df.iloc[row, j])

                # If that value is the die number and the following value is None
                if (value == current_die) & (clean_value(df.iloc[row, 2]) == None):
                    # We save the machine those values are for
                    avrg_data.append(current_machine)
                    # Then we iterate in that line to save those values
                    for i in range(9):
                        # I get the first value & clean it
                        value = df.iloc[row, i+2]
                        value = clean_value(value)
                        # If the value is not None then I save it
                        
                        if value != None:
                            avrg_data.append(value)

            # Just creating the list if there is a value to avoid empty lists
            if avrg_data:
                dies[current_die].append(avrg_data)


    return dies


