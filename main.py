import pandas as pd
from functions import *

try:
    # Read the AVANTE export file
    # Skip the first 5 rows because they contain report information,
    # not actual production data
    try:
        df = pd.read_csv(
            "data_various_machines.csv",
            skiprows=5,
            encoding="cp1252"
        )

    # Handle file encoding issues
    except UnicodeDecodeError:
        print(
            "ERROR: The file encoding is not supported. "
            "Please export the file again from AVANTE."
        )
        raise SystemExit()

    # Validating formatting errors
    errors = validate_avante_file(df)

    # Validate that the file structure matches the expected
    21
    # AVANTE report format before performing any analysis
    if errors:

        print("\nAVANTE FILE VALIDATION FAILED\n")

        # Display all validation errors found
        for error in errors:
            print(f"- {error}")

        # Stop the program if validation fails
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

    #Export results to CSV
    # Note:
    # Extra time values are calculated against the
    # fastest machine for a standard run of 10,000 sheets

    with open("machine_ranking.csv", "w", newline="", encoding="utf-8") as f:

        # Add explanatory note at the top of the file
        f.write('"Note: Extra time is compared against the fastest machine for 10,000 sheets."\n')

        # Write the actual results
        df.to_csv(f, index=False)

except Exception as e:
    print(f"Unexpected error: {e}")