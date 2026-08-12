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

    try:
        number = float(value)

        if number.is_integer():
            return int(number)

        return number

    except ValueError:
        return value



