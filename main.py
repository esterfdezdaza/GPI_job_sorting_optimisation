import pandas as pd
from functions import *
from testing import *
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import ctypes
import sys

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
        df = pd.read_csv(
            file_path,
            skiprows=5,   # Skip the first 5 rows because they contain report information, not actual production data
            encoding="cp1252"
        )

        # Then checks that the AVANTE imported file contains the correct format
        errors = validate_avante_file(df)
    
        # Validate that the file structure matches the expected
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

    # Handle file encoding issues
    except UnicodeDecodeError:
        messagebox.showinfo("File Read Error", f"{type(e).__name__}\n\n{e}")
        raise SystemExit()

    print("AVANTE file validation passed.")

    # Extract production data from the raw AVANTE export
    # and organise it by die and machine
    data = get_data_from_csv(df)
    ranking = analyse_data(data)

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