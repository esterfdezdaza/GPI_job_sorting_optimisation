import pandas as pd
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog
import sys, os

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
    """
    Cleans and standardizes a value extracted from the source CSV file.

    The function converts numeric strings to integers or floats, removes
    thousand separators, handles empty or missing values, and preserves
    non-numeric text values.

    Args:
        value (Any):
            Value read from the dataframe cell. Can be a number, string,
            empty value, or NaN.

    Returns:
        int | float | str | None:
            - int for whole numbers.
            - float for decimal numbers.
            - str for non-numeric text values.
            - None for empty or missing values.
    """
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

    current_machine = df.iloc[0, 1]

    # Create an empty list for that die
    dies[current_die] = []

    # Loop through every row in the dataframe
    for row in range(len(df)):
        # Save the first die
        die = clean_value(df.iloc[row, 0])

        if die is None or die == "":
            continue
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
                    # First we should check if that machine is already saved
                    for idx, record in enumerate(dies[current_die]):
                        if record[0] == current_machine:
                            #If it is saved we delete the value and store the new/last one
                            dies[current_die].pop(idx)    
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


def hours_to_hm(decimal_hours):
    """
    Converts a decimal hour value into a human-readable hours and minutes
    format.

    Example:
        1.75 -> "1h 45m"

    Args:
        decimal_hours (float):
            Time expressed in decimal hours.

    Returns:
        str:
            Formatted string showing hours and minutes.
    """
    hours = int(decimal_hours)
    minutes = round((decimal_hours - hours) * 60)

    return f"{hours}h {minutes}m"


def analyse_data(data):
    """
    Analyses machine performance data and generates a ranking for each die.

    Machines are ranked according to their production speed. The fastest
    machine is used as the benchmark, and all other machines show the
    additional time required to produce 10,000 cartons compared with the
    fastest machine.

    Args:
        data (dict):
            Dictionary containing die numbers and their associated machine
            performance records.

    Returns:
        dict[int, list[str]]:
            Dictionary where:
            - The key is a die number.
            - The value is a list of ranking strings sorted from fastest
              to slowest machine.
    """
    # Standard quantity used to compare all machines
    REF_QTY = 10000

    ranking = {}

    for die, records in data.items():
        # Ignore records with no valid speed
        valid_records = [
            record for record in records
            if record[-1] > 0
        ]

        if not valid_records:
            ranking[die] = ["No valid speed data"]
            continue

        # Sort from fastest to slowest
        sorted_records = sorted(
            valid_records,
            key=lambda record: record[-1],
            reverse=True
        )

        result = []

        # Fastest machine and its speed
        fastest_machine = sorted_records[0][0]
        fastest_speed = sorted_records[0][-1]

        # Time needed by fastest machine to produce 10,000 cartons
        fastest_time = REF_QTY / fastest_speed

        for record in sorted_records:

            machine = record[0]
            speed = record[-1]

            # First machine is the benchmark
            if machine == fastest_machine:
                result.append(
                    f"{machine} ({speed}) - fastest"
                )
                continue

            # Time needed by this machine to produce 10,000 cartons
            machine_time = REF_QTY / speed

            # Extra time compared to the fastest machine
            extra_time = machine_time - fastest_time

            result.append(
                f"{machine} ({speed}) - +{hours_to_hm(extra_time)}"
            )

        ranking[die] = result

    return ranking

def validate_avante_file(df):
    """
    Validates that an imported dataframe matches the expected AVANTE
    export format.

    The validation checks:
    - Whether the file is empty.
    - Whether the required columns exist.
    - Whether the expected number of columns is present.
    - Whether die numbers are found in the first column.

    Args:
        df (pandas.DataFrame):
            Dataframe loaded from the selected CSV file.

    Returns:
        list[str]:
            List of validation error messages. An empty list indicates
            that the file passed all validation checks.
    """
    errors = []

    # Check the file has data
    if df.empty:
        errors.append("File is empty.")

    # Check first column exists
    if df.shape[1] < 1:
        errors.append("No die column found.")

    
    # Check that the AVANTE export contains enough columns
    if df.shape[1] < 11:
        errors.append("Not the correct format.")
        print("\nERROR: Tried to import a file with less columns than are expected")

    # Check first 20 rows for at least one die number
    die_found = False

    for row in range(min(20, len(df))):

        value = clean_value(df.iloc[row, 0])

        if isinstance(value, (int, float)):
            die_found = True
            break

    if not die_found:
        errors.append(
            "No die numbers found in the first column. Check skiprows value."
        )

    return errors

def select_csv_file():
    """
    Opens a file selection dialog and allows the user to choose an AVANTE
    CSV export file.

    If no file is selected, the user is notified and the application
    exits.

    Returns:
        str:
            Full path of the selected CSV file.

    Raises:
        SystemExit:
            Raised when the user cancels the file selection dialog.
    """
    # Ask the user to select a CSV file
    file_path = filedialog.askopenfilename(
        title="Select AVANTE Data File",
        filetypes=[("CSV files", "*.csv")]
    )
    # User clicked Cancel or X
    if not file_path:
        messagebox.showinfo("Select AVANTE Data File", """No file has been selected""")
        raise SystemExit()

    return file_path

def show_menu(ranking, output_df):
    """Creates and displays the main graphical user interface for the Machine Ranking Tool.
    The menu allows users to:
    - Search for a die number and view its machine rankings.
    - Export the machine ranking report as a CSV file.
    - Exit the application.

    Args:
        ranking (dict[int, list[str]]):
            Dictionary mapping each die number to a list of ranked machine
            recommendations and related information.
        output_df (pandas.DataFrame):
            DataFrame containing the machine ranking results that can be
            exported to a CSV report.
    """

    root = tk.Tk()
    root.title("Machine Ranking Tool")

    root.geometry("400x200")
    root.resizable(False, False)

    def search_die():
        """Prompts the user to enter a die number and displays the corresponding
        machine ranking information.
        
        The function validates user input, searches for the die number in the
        ranking dictionary, and shows the results in a message box. If the die
        number is not found or the input is invalid, an appropriate warning or
        error message is displayed.
        """
        while True:

            die = simpledialog.askstring(
                "Search Die",
                "Enter Die Number:"
            )

            # User pressed Cancel
            if die is None:
                return

            try:
                die = int(die)
            except ValueError:
                messagebox.showerror(
                    "Invalid Input",
                    "Please enter a valid die number."
                )
                continue

            if die in ranking:

                result = "\n".join(ranking[die])

                messagebox.showinfo(
                    f"Die {die}",
                    result
                )

            else:

                messagebox.showwarning(
                    "Not Found",
                    f"Die {die} was not found."
                )

    def save_csv():
        """Prompts the user to enter a die number and displays the corresponding
        machine ranking information.
       
        The function validates user input, searches for the die number in the
        ranking dictionary, and shows the results in a message box. If the die
        number is not found or the input is invalid, an appropriate warning or
        error message is displayed.
        """
        output_file = filedialog.asksaveasfilename(
            title="Save Ranking Report",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="machine_ranking.csv"
        )

        if not output_file:
            return

        try:

            with open(
                output_file,
                "w",
                newline="",
                encoding="utf-8"
            ) as f:

                f.write(
                    '"Note: Extra time is compared against the fastest machine for 10,000 sheets."\n'
                )

                output_df.to_csv(
                    f,
                    index=False
                )

            messagebox.showinfo(
                "Success",
                "File saved successfully."
            )

        except PermissionError:

            messagebox.showerror(
                "File Open",
                "Please close the file and try again."
            )
    def close_program():
        """Closes the application and terminates the Python process.
        Destroys the main Tkinter window and forces the program to exit,
        ensuring that no background Tkinter processes remain running.
        """
        root.destroy()
        os._exit(0)

    tk.Label(
        root,
        text="Machine Ranking Tool",
        font=("Arial", 14, "bold")
    ).pack(pady=15)

    tk.Button(
        root,
        text="Search Die",
        width=25,
        command=search_die
    ).pack(pady=5)

    tk.Button(
        root,
        text="Download Ranking CSV",
        width=25,
        command=save_csv
    ).pack(pady=5)

    tk.Button(
        root,
        text="Exit",
        width=25,
        command=lambda: sys.exit()
    ).pack(pady=5)

    root.protocol("WM_DELETE_WINDOW", close_program)

    root.mainloop()