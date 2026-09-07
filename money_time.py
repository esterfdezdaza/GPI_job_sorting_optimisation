import pandas as pd
from functions import *
import re
import matplotlib.pyplot as plt

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
    """
    Calculates the total theoretical and meaningful hours lost
    due to jobs being run on non-preferred machines.

    Meaningful losses are defined as jobs where moving to the
    preferred machine would save at least 30 minutes.

    Args:
        work_orders (list):
            List of works order dictionaries.

        speed_lookup (dict):
            Dictionary containing machine speeds by die.

    Returns:
        tuple:
            (
                total_lost_hours,
                meaningful_lost_hours
            )
    """

    total_lost_hours = 0
    meaningful_lost_hours = 0

    # 30 minutes
    MIN_TIME_SAVED = 0.5

    for job in work_orders:

        die = job["die"]
        wo = job["wo"]
        machine = job["machine"]
        qty = job["qty"]
        actual_hours = job["hours"]

        # Skip jobs for dies not present in rankings
        if die not in speed_lookup:
            continue

        # Skip machines not present in rankings
        if machine not in speed_lookup[die]:
            continue

        # Fastest machine speed for this 
        best_speed = max(speed_lookup[die].values())

        # Speed of the machine that actually ran the job
        actual_machine_speed = speed_lookup[die][machine]

        # Ignore jobs already run on the preferred machine
        if actual_machine_speed == best_speed:
            continue

        # Prevent divide-by-zero errors
        if best_speed <= 0:
            continue

        # Time that the preferred machine would have needed
        optimal_hours = qty / best_speed

        # Additional time incurred
        lost_hours = actual_hours - optimal_hours

        # Only count real losses
        if lost_hours > 0:

            total_lost_hours += lost_hours

            # Only count significant opportunities
            if lost_hours >= MIN_TIME_SAVED:
                meaningful_lost_hours += lost_hours
            """
            # Debug output
            print(
                f"WO={wo}",
                f"Die={die}",
                f"Machine={machine}",
                f"Qty={qty}",
                f"Actual={actual_hours:.2f}",
                f"Optimal={optimal_hours:.2f}",
                f"Lost={lost_hours:.2f}"
            )"""

    return (
        round(total_lost_hours, 2),
        round(meaningful_lost_hours, 2)
    )

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

def calculate_machine_demand(work_orders, speed_lookup):
    """
    Calculates how many jobs would ideally be assigned
    to each machine.

    Returns:
        dict:
            {
                machine: number_of_jobs
            }
    """

    preferred_machine_count = {}

    for job in work_orders:

        die = job["die"]

        if die not in speed_lookup:
            continue

        # Find the best machine for this die
        best_machine = max(
            speed_lookup[die],
            key=speed_lookup[die].get
        )

        if best_machine not in preferred_machine_count:
            preferred_machine_count[best_machine] = 0

        preferred_machine_count[best_machine] += 1

    return dict(
        sorted(
            preferred_machine_count.items(),
            key=lambda x: x[1],
            reverse=True
        )
    )

def calculate_actual_machine_usage(work_orders):
    """
    Counts how many jobs actually ran on each machine.
    """

    actual_usage = {}

    for job in work_orders:

        machine = job["machine"]

        if machine not in actual_usage:
            actual_usage[machine] = 0

        actual_usage[machine] += 1

    return dict(
        sorted(
            actual_usage.items(),
            key=lambda x: x[1],
            reverse=True
        )
    )

def plot_machine_allocation(preferred_usage, actual_usage):
    """
    Creates a comparison chart showing:

    - How many jobs ideally should have run on each machine.
    - How many jobs actually ran on each machine.
    """

    # Get all machines appearing in either dictionary
    machines = sorted(set(preferred_usage.keys()) | set(actual_usage.keys()))

    # Build dataframe
    df_plot = pd.DataFrame({
        "Machine": machines,
        "Preferred": [
            preferred_usage.get(machine, 0)
            for machine in machines],
        "Actual": [
            actual_usage.get(machine, 0)
            for machine in machines]
    })

    # Sort by preferred demand
    df_plot = df_plot.sort_values(by="Preferred", ascending=False)

    # Plot
    ax = df_plot.plot(x="Machine", y=["Preferred", "Actual"], kind="bar", figsize=(12, 6))

    ax.set_title("Preferred vs Actual Machine Allocation")

    ax.set_ylabel("Number of Works Orders")

    ax.set_xlabel("Machine")

    plt.xticks(rotation=45)

    plt.tight_layout()

    plt.show()


def create_kpi_dashboard(start_date, end_date, jobs, hours_lost, meaningful_hours_lost, money_lost):
    fig = plt.figure(figsize=(12, 7), facecolor="#E8F5E9")

    fig.suptitle("Potential Capacity Improvement Analysis", fontsize=20, fontweight="bold", y=0.95)

    plt.figtext(0.5, 0.87, f"{start_date} → {end_date}", ha="center", fontsize=12)
    cards = [
        ("Works Orders", f"{jobs:,}"),
        ("Recoverable Hours", f"{meaningful_hours_lost:.1f} h"),
        ("Shift Days", f"{meaningful_hours_lost/12:.1f}"),
        ("Financial Impact", f"£{money_lost:,.0f}")
    ]

    positions = [
        [0.05, 0.60, 0.40, 0.25],
        [0.55, 0.60, 0.40, 0.25],
        [0.05, 0.25, 0.40, 0.25],
        [0.55, 0.25, 0.40, 0.25]
    ]

    for (title, value), pos in zip(cards, positions):

        ax = fig.add_axes(pos)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_facecolor("#7BC67B") # Medium green

        for spine in ax.spines.values():
            spine.set_visible(False)

        ax.text(0.5, 0.65, value, ha="center", va="center", fontsize=24, fontweight="bold")
        ax.text(0.5, 0.25, title, ha="center", va="center", fontsize=12)

    plt.savefig("business_impact_dashboard.png", dpi=300, bbox_inches="tight")
    plt.close()