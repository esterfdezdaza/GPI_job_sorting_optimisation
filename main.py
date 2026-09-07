import pandas as pd
from functions import *
from money_time import *
from testing import *
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import ctypes
import sys
import matplotlib.pyplot as plt

# Avoid having more than one file open at the same time
mutex = ctypes.windll.kernel32.CreateMutexW(
    None,
    False,
    "MachineRankingToolMutex"
)

print("LastError:", ctypes.GetLastError())

if ctypes.GetLastError() == 183:
    messagebox.showinfo(
        "Already Running",
        "Machine Ranking Tool is already open."
    )
    sys.exit()

root = tk.Tk()
root.withdraw()  # Hide the main window

# Keep dialogs on top
root.attributes("-topmost", True)

accepted = messagebox.askokcancel(
    "AVANTE File Requirements", 
    """
========================================================
        MACHINE RANKING ANALYSIS TOOL
========================================================

Before running the program, ensure the AVANTE export:

1. Is saved as a CSV file.
2. Has the first 5 report rows intact
   (the program automatically skips them).
3. Contains the following columns in this order:

   Column A : Die Number
   Column B : Machine
   Column C : Works Order / Job Number
   Column D : Total Quantity
   Column E : Total Hours
   Column F : Average Speed (Cartons per Hour)

Example:

--------------------------------------------------------
| Die    | Machine | Job No | Qty | Hours | Speed      |
--------------------------------------------------------
| 76537  | DIANA   | 12345  | ... | ...   | 16923      |
|         DIANA Average Values                         |
--------------------------------------------------------

Press OK to choose the data file.

""")
# User clicked Cancel or X
if not accepted:
    raise SystemExit()

# -------------------------------------------
# Imports CSV File
# -------------------------------------------
try:
    # Ask the user to select a CSV file
    file_path = select_csv_file()
        
    try:
        # First checks that we can access the file 
        start_date, end_date = get_report_period(file_path)
        df = pd.read_csv(
            file_path,
            skiprows=5,   # Skip the first 5 rows because they contain report information, not actual production data
            encoding="cp1252"
        )

        # Then checks that the AVANTE imported file contains the correct format
        errors = validate_avante_file(df)
    
        # Validate that the file matches the expected structure
        if errors:
    
            print("\nAVANTE FILE VALIDATION FAILED\n")
    
            # Display all validation errors found
            for error in errors:
                print(f"- {error}")
    
            # Stop the program if validation fails
            messagebox.showinfo("Select AVANTE Data File", """Wrong File Format""")
            raise SystemExit()

        # Tests the programm is working correctly
        run_all_tests()
        print("AVANTE file validation passed.")

    # Handle file encoding issues
    except UnicodeDecodeError:
        messagebox.showinfo("File Read Error", f"{type(e).__name__}\n\n{e}")
        raise SystemExit()

    # Extract production data from the raw AVANTE export
    # and organise it by die and machine
    data = get_data_from_csv(df)
    ranking = analyse_data(data)

    # Calculate amount of money lost
    jobs = get_work_orders(df)   

    speed_lookup = build_speed_lookup(data)

    hours_lost, meaningful_hours_lost = (calculate_total_lost_hours(jobs,speed_lookup))
    preferred_usage = calculate_machine_demand(jobs, speed_lookup)
    actual_usage = calculate_actual_machine_usage(jobs)


    print()
    print("========== BUSINESS IMPACT ==========")
    print(f"Period Analysed: "f"{start_date} to {end_date}")
    print(f"Jobs analysed: {len(jobs)}")
    print(f"Theoretical recoverable capacity: " f"{hours_lost:.2f} hours")
    print(f"Theoretical recoverable capacity: "f"{hours_lost / 24:.2f} days")
    print(f"Meaningful recoverable capacity "f"(>30 minutes/job): "f"{meaningful_hours_lost:.2f} hours")
    print(f"Meaningful recoverable capacity "f"(>30 minutes/job): "f"{meaningful_hours_lost / 24:.2f} days")
    # Data of the money per hour (Machine Gluing Costs- includes lost time /break downs machine - 193) in finishing taken from SOP 407 - Supplier Claim
    print(f"Money recoverable theoretical capacity: £{hours_lost*193:.2f}")
    print(f"Money recoverable meaningful capacity: £{meaningful_hours_lost*193:.2f}")
    print(f"12h - Shifts recoverable: "f"{hours_lost / 12:.2f}")

    print()
    print("========== MACHINE DEMAND ==========")
    print("\nPreferred Allocation")
    for machine, count in preferred_usage.items():
        print(f"{machine}: {count} jobs")
    print("\nActual Allocation")
    for machine, count in actual_usage.items():
        print(f"{machine}: {count} jobs")

    print()
    print("========== BOTTLENECK ANALYSIS ==========")
    all_jobs = len(jobs)
    for machine, count in preferred_usage.items():
        percentage = round(count / all_jobs * 100, 1)
        print(f"{machine}: " f"{count} jobs " f"({percentage}%)")  

    create_kpi_dashboard(start_date, end_date, len(jobs), hours_lost, meaningful_hours_lost, meaningful_hours_lost*193)
    plot_machine_allocation(preferred_usage, actual_usage)


    # Print ranking results to the console for debugging
    print(ranking)

    # -------------------------------------------
    # Create CSV output
    # -------------------------------------------

    # Store one row per die
    rows = []

    # Loop through each die and its ranked machines
    for die, machines in ranking.items():

        # First column contains the die number
        row = {"Die": die}


        for i, machine in enumerate(machines, start=1):
            row[f"Machine {i}"] = machine

        rows.append(row)

    # Convert the list into a DataFrame
    df = pd.DataFrame(rows)

    # -------------------------------------------
    # Exports CSV File
    # -------------------------------------------

    # Menu allowing to download, search or exit the program
    show_menu(ranking, df)
    

except Exception as e:
    messagebox.showinfo("File Read Error", f"{type(e).__name__}\n\n{e}")
    raise SystemExit()