import pandas as pd
from functions import *
import tkinter as tk
from tkinter import messagebox, filedialog, simpledialog

"""
Automated tests for the Machine Ranking Analysis Tool

Run:
python test_program.py

"""

# -----------------------------------------
# Test 1: clean_value
# -----------------------------------------
def test_clean_value():

    assert clean_value(None) is None
    assert clean_value("12,345") == 12345
    assert clean_value("DIANA") == "DIANA"

    print("✅ test_clean_value passed")

# -----------------------------------------
# Test 2: hours_to_hm
# -----------------------------------------
def test_hours_to_hm():

    assert hours_to_hm(1.5) == "1h 30m"
    assert hours_to_hm(2.75) == "2h 45m"
    assert hours_to_hm(0.25) == "0h 15m"

    print("✅ test_hours_to_hm passed")

# -----------------------------------------
# Test 3: ranking order
# Fastest machine should appear first
# -----------------------------------------
def test_ranking_order():

    test_data = {
        1000: [
            ["DIANA", 100000, 5, 20000],
            ["ALPINA", 100000, 5, 25000],
            ["110WP", 100000, 5, 15000]
        ]
    }

    ranking = analyse_data(test_data)

    first_machine = ranking[1000][0]

    assert "ALPINA" in first_machine

    print("✅ test_ranking_order passed")

# -----------------------------------------
# Test 4: machine with speed 0
# Program should not crash
# -----------------------------------------
def test_zero_speed():

    test_data = {
        1000: [
            ["DIANA", 1000, 0, 0],
            ["110WP", 1000, 0, 0]
        ]
    }

    ranking = analyse_data(test_data)

    assert ranking is not None

    print("✅ test_zero_speed passed")

# -----------------------------------------
# Test 5: extra time calculation
# -----------------------------------------
def test_extra_time():

    test_data = {
        1000: [
            ["FAST", 100000, 5, 20000],
            ["SLOW", 100000, 5, 10000]
        ]
    }

    ranking = analyse_data(test_data)

    # FAST should be first
    assert "FAST" in ranking[1000][0]

    # SLOW should be second
    assert "SLOW" in ranking[1000][1]

    print("✅ test_extra_time passed")

# -----------------------------------------
# Test 6: single machine die
# -----------------------------------------
def test_single_machine():

    test_data = {
        1000: [
            ["DIANA", 50000, 2, 25000]
        ]
    }

    ranking = analyse_data(test_data)

    assert len(ranking[1000]) == 1
    assert "fastest" in ranking[1000][0]

    print("✅ test_single_machine passed")

# -----------------------------------------
# Test 7: all speeds must be sorted
# -----------------------------------------
def test_sorting():

    test_data = {
        1000: [
            ["M1", 100000, 5, 15000],
            ["M2", 100000, 5, 30000],
            ["M3", 100000, 5, 20000]
        ]
    }

    ranking = analyse_data(test_data)

    assert "M2" in ranking[1000][0]
    assert "M3" in ranking[1000][1]
    assert "M1" in ranking[1000][2]

    print("✅ test_sorting passed")

# -----------------------------------------
# Test 8: Check whether the output file can be written to.
#   If the file is open in Excel or another program,
#   the test will fail.
# -----------------------------------------
def check_output_file(output_file):

    try:
        with open(output_file, "a"):
            print("✅ check_output_file passed")
            pass

        return True

    except PermissionError:
        messagebox.showerror("ERROR",
            """\nERROR: The file "machine_ranking.csv" is currently open. Please close the file and run the analysis again."""
        )

        return False

# -----------------------------------------
# Test runner
# -----------------------------------------
def run_all_tests():

    print("\nRunning automated tests...\n")

    test_clean_value()
    test_hours_to_hm()
    test_ranking_order()
    test_zero_speed()
    test_extra_time()
    test_single_machine()
    test_sorting()


    print("\n✅ ALL 7 TESTS PASSED\n")


