import pandas as pd
from functions import *
import re

def build_speed_lookup(data):
    """ Creates a lookup table containing the average speed achieve by each machine for every die.
    The lookup enables fast access to machine speeds when calculating historical production losses.

    Args:
        data (dict): Dictionary produced by get_data_from_csv().

    Returns:
        dict: 
            Structure in the form:

            {
                die_number: {
                    machine_name: average_speed
                    }
            }
    """
    lookup = {}

    # Loop through every die and its machine records
    for die, records in data.items():

        lookup[die] = {}

        # Store each machine speed under the corresponding die
        for record in records:

            machine = str(record[0]).upper()
            speed = record[-1]

            lookup[die][machine] = speed

    return lookup

def calculate_total_lost_hours(work_orders, speed_lookup):
    """ Calculates the total production time lost due to jobs being run on machines that are not the preferred machine for a die.

    For each Works Order:
    - The actual running hours are taken from the AVANTE summary row.
    - The fastest machine speed available for that die is identified.
    - The theoretical running time on the fastest machine is calculated.
    - The difference between actual and theoretical time is treated as lost production time.
    
    Args:
        work_orders (list[dict]): List of Works Orders extracted from the AVANTE file
        speed_lookup (dict): Dictionary containing average machine speeds by die

    Returns:
        float: Total estimated hours lost
    """
    total_lost_hours = 0
    best_speed = None

    # Analyse each Works Order individually
    for job in work_orders:

        die = job["die"]
        wo = job["wo"]
        machine = job["machine"]
        qty = job["qty"]
        actual_hours = job["hours"]


        # Skips jobs where no ranking information exists
        if die not in speed_lookup:
            continue

        # Skips jobs where no machine is unavailable in the lookup
        if machine not in speed_lookup[die]:
            continue
        
        # Identify the fastest average speed available for this die
        best_speed = max(speed_lookup[die].values())

        # Skip jobs already run on the fastest machine
        actual_machine_speed = speed_lookup[die][machine]

        # Debug output
        print(die, wo, machine, qty, actual_hours, best_speed, actual_machine_speed)

        # Ignore jobs that already ran on the fastest machine
        if actual_machine_speed == best_speed:
            continue
        
        # Prevents division-by-zero errors
        if best_speed is None or best_speed <= 0:
            continue

        # Calculate how long the job would have taken on the fastest machine
        optimal_hours = qty / best_speed

        # Calculate the additional time consumed
        lost_hours = actual_hours - optimal_hours

        # Debug output
        print(
            "actual =", actual_hours,
            "optimal =", optimal_hours,
            "lost =", lost_hours
        )

        # Only count genuine losses
        if lost_hours > 0:
            total_lost_hours += lost_hours
            print(total_lost_hours)

    return round(total_lost_hours, 2)

def get_work_orders(df):
    """Extracts completed Works Orders from AVANTE report.
        Only summary rows are collected. 
        These rows contain:
        - Total quantity produced
        - Total hours running

        Each Work Order is stored as a dictionary to simplify later analysis.

    Args:
        df (pandas.DataFrame): AVANTE report dataframe

    Returns:
        list[dict]: List containing Works Order Information
    """

    jobs = []

    # Scan every row in the dataframe
    for row in range(len(df)):

        die = clean_value(df.iloc[row, 0])
        machine = clean_value(df.iloc[row, 1])
        wo = clean_value(df.iloc[row, 2])

        qty = clean_value(df.iloc[row, 3])
        hours = clean_value(df.iloc[row, 6])

        # Summary rows contain the total quantity
        if qty is None:
            continue

        # Ignore incomplete records
        if (
            die is None or
            machine is None or
            wo is None or
            hours is None
        ):
            continue

        jobs.append({
            "die": die,
            "machine": str(machine).upper(),
            "wo": wo,
            "qty": qty,
            "hours": hours
        })

    return jobs

def get_report_period(file_path):
    """
    Extracts the date range used in the AVANTE report. 
    
    The function searches the report header for:
        U_Shiftdate >= "dd/mm/yy"
        U_Shiftdate <= "dd/mm/yy"

    Args:
        file_path (str): Path to the AVANTE CSV export.

    Returns:
        tuple(str, str):
            (start_date, end_date)
    """

    header = pd.read_csv(
        file_path,
        nrows=5,
        header=None,
        encoding="cp1252"
    )

    # Combine all header rows into a single string
    text = " ".join(
        str(value)
        for row in header.values
        for value in row
        if pd.notna(value)
    )

    # Extract the report date range
    match = re.search(
        r'U_Shiftdate\s*>=\s*"([^"]+)"\s*.*?U_Shiftdate\s*<=\s*"([^"]+)"',
        text
    )

    if match:
        return match.group(1), match.group(2)

    return "Unknown", "Unknown"