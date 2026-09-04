import pandas as pd
from functions import *
import re

def build_speed_lookup(data):

    lookup = {}

    for die, records in data.items():

        lookup[die] = {}

        for record in records:

            machine = str(record[0]).upper()
            speed = record[-1]

            lookup[die][machine] = speed

    return lookup

def calculate_total_lost_hours(work_orders, speed_lookup):
    total_lost_hours = 0
    best_speed = None

    for job in work_orders:

        die = job["die"]
        wo = job["wo"]
        machine = job["machine"]
        qty = job["qty"]
        actual_hours = job["hours"]



        if die not in speed_lookup:
            continue

        if machine not in speed_lookup[die]:
            continue

        best_speed = max(speed_lookup[die].values())

        # Skip jobs already run on the fastest machine
        actual_machine_speed = speed_lookup[die][machine]

        print(die, wo, machine, qty, actual_hours, best_speed, actual_machine_speed)

        if actual_machine_speed == best_speed:
            continue

        if best_speed is None or best_speed <= 0:
            continue

        optimal_hours = qty / best_speed

        lost_hours = actual_hours - optimal_hours

        print(
            "actual =", actual_hours,
            "optimal =", optimal_hours,
            "lost =", lost_hours
        )


        if lost_hours > 0:
            total_lost_hours += lost_hours
            print(total_lost_hours)

    return round(total_lost_hours, 2)

def get_work_orders(df):

    jobs = []

    for row in range(len(df)):

        die = clean_value(df.iloc[row, 0])
        machine = clean_value(df.iloc[row, 1])
        wo = clean_value(df.iloc[row, 2])

        qty = clean_value(df.iloc[row, 3])
        hours = clean_value(df.iloc[row, 6])

        # Only summary rows have total quantity
        if qty is None:
            continue

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

    # Find date conditions
    match = re.search(
        r'U_Shiftdate\s*>=\s*"([^"]+)"\s*.*?U_Shiftdate\s*<=\s*"([^"]+)"',
        text
    )

    if match:
        return match.group(1), match.group(2)

    return "Unknown", "Unknown"