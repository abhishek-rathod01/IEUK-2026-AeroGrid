"""
AeroGrid Turbine Anomaly Detection
===================================
IEUK 2026 Engineering Sector Skills Project — Artefact 1
Author: Abhisheksinh Vanrajsinh Rathod
GitHub: github.com/abhishek-rathod01

MY SUMMARY (in my own words)
-----------------------------
This script is a data pipeline that detects broken wind turbines.

It reads a CSV file of sensor readings — each row is one measurement
from one turbine at one moment in time. There are 5,000 rows and 10
turbines in our dataset.

The script works in five steps:
  1. READ    — load the CSV into memory as a table (called a DataFrame)
  2. VALIDATE — check that the columns we expect actually exist
  3. GROUP   — gather all readings belonging to the same turbine together
  4. CALCULATE — for each turbine:
                   * average temperature (are they running hot on average?)
                   * peak vibration     (did they ever spike dangerously?)
  5. FLAG    — apply the safety rules from the brief:
                   * avg temp > 85°C   → overheating problem
                   * peak vib > 15mm/s → structural vibration problem
               If EITHER rule breaks, the turbine is flagged.

DESIGN DECISION (important for interviews)
-------------------------------------------
The brief says "average temperature exceeds 85°C" → so I use .mean()
The brief says vibration "spikes above 15 mm/s" → so I use .max()
These are deliberately different calculations. A "spike" is a peak,
not an average. Using .max() for vibration and .mean() for temperature
shows careful reading of the brief, not just copy-paste logic.

RESULT
------
Out of 10 turbines:
  T-04 → overheating   (avg temp 90.6°C, limit 85°C)
  T-07 → over-vibrating (peak 25.0 mm/s, limit 15 mm/s)

HOW TO RUN
----------
1. Install Python 3 and pandas:
       pip install pandas
2. Put this file in the SAME folder as telemetry_data.csv
3. Open a terminal in that folder and run:
       python anomaly_detection.py
"""

# pandas is the industry-standard Python library for working with
# table-structured data (like spreadsheets / CSV files).
# We give it the alias "pd" so we can write pd.read_csv() instead of
# pandas.read_csv() — saves typing and is the universal convention.
import pandas as pd


# ======================================================================
# CONFIG — single place to change filenames and thresholds
# ======================================================================
# Keeping all "magic numbers" and filenames in one block at the top
# is a best practice called "configuration separation". If the CSV
# changes names or the safety limits change, you only edit here.

CSV_FILE = "telemetry_data.csv"   # the telemetry data file from AeroGrid

# Column names — must exactly match the headers in the CSV.
# If they don't match, the script prints the real names rather than crashing.
COL_TURBINE_ID  = "turbine_id"       # which turbine the reading belongs to
COL_TEMPERATURE = "temperature_c"    # temperature in degrees Celsius
COL_VIBRATION   = "vibration_mm_s"   # vibration in millimetres per second

# Safety thresholds — taken directly from the IEUK project brief.
MAX_SAFE_TEMP      = 85.0   # °C   — flag if AVERAGE temperature exceeds this
MAX_SAFE_VIBRATION = 15.0   # mm/s — flag if vibration SPIKE exceeds this


def main():
    """
    Main function — runs all five pipeline steps in sequence.
    Wrapping everything in a function (rather than writing it at module
    level) is good Python practice: it keeps the code organised and
    prevents variables leaking into the global scope.
    """

    # ------------------------------------------------------------------
    # STEP 1: READ THE CSV
    # ------------------------------------------------------------------
    # pd.read_csv() opens the file and loads it into a DataFrame.
    # A DataFrame is pandas' word for a table held in memory — think of
    # it like an Excel spreadsheet you can query with code.
    #
    # We wrap it in try/except so that if the file is missing, we print
    # a helpful message instead of a confusing Python crash.
    # This is called "defensive programming" — assume input can be wrong.

    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print(f"ERROR: could not find '{CSV_FILE}'.")
        print("Make sure the CSV is in the same folder as this script, and that")
        print("its name matches CSV_FILE in the CONFIG section above.")
        return   # 'return' inside a function means "stop here, exit the function"

    # Strip any accidental leading/trailing spaces from column names.
    # Some CSV editors add invisible spaces — this prevents silent failures.
    df.columns = df.columns.str.strip()

    # ------------------------------------------------------------------
    # STEP 2: VALIDATE COLUMNS EXIST
    # ------------------------------------------------------------------
    # Before doing any analysis, we check that the three columns we need
    # are actually present in the file. If not, we print the REAL column
    # names so the user knows what to fix in the CONFIG block.

    required = [COL_TURBINE_ID, COL_TEMPERATURE, COL_VIBRATION]

    # List comprehension: builds a list of any column names that are
    # in 'required' but NOT in df.columns (i.e. missing from the CSV).
    missing = [col for col in required if col not in df.columns]

    if missing:
        print("ERROR: these expected columns were not found:", missing)
        print("The CSV actually contains these columns:", list(df.columns))
        print("Open the script and fix the COL_* names in the CONFIG section.")
        return   # no point continuing with the wrong column names

    # ------------------------------------------------------------------
    # STEP 3: GROUP BY TURBINE
    # ------------------------------------------------------------------
    # The CSV has 5,000 rows — roughly 500 readings per turbine.
    # groupby() collects all rows with the same turbine_id together,
    # so we can calculate one summary value per turbine rather than
    # looking at every individual row.
    #
    # Think of it like sorting 5,000 postcards into 10 piles by address.

    grouped = df.groupby(COL_TURBINE_ID)

    # .mean() adds up all temperatures for each turbine and divides by
    # the count — gives us the average temperature per turbine.
    avg_temp = grouped[COL_TEMPERATURE].mean()

    # .max() finds the single highest vibration reading per turbine.
    # We use max (not mean) because the brief says "spikes" — a spike
    # is a peak value, not an average. One bad reading is enough.
    max_vibration = grouped[COL_VIBRATION].max()

    # ------------------------------------------------------------------
    # STEP 4: APPLY THE ANOMALY RULES
    # ------------------------------------------------------------------
    # These comparisons produce a True/False value for each turbine.
    # Example: avg_temp["T-04"] = 90.6 → 90.6 > 85.0 → True (flagged)
    #          avg_temp["T-01"] = 65.3 → 65.3 > 85.0 → False (safe)

    temp_anomaly      = avg_temp > MAX_SAFE_TEMP          # True where avg temp too high
    vibration_anomaly = max_vibration > MAX_SAFE_VIBRATION  # True where vib spike too high

    # The | operator means OR — a turbine fails if EITHER rule breaks.
    # If both are True for one turbine, it still just appears once.
    failing = temp_anomaly | vibration_anomaly

    # Keep only the turbine IDs where 'failing' is True.
    # .index gives us the turbine ID labels; .tolist() converts to a
    # plain Python list so we can loop through it easily.
    failing_ids = failing[failing].index.tolist()

    # ------------------------------------------------------------------
    # STEP 5: PRINT THE REPORT
    # ------------------------------------------------------------------
    # f-strings (f"...") let us embed variables directly inside strings.
    # The {variable} parts get replaced with their values at runtime.

    print("=" * 52)
    print("AeroGrid Turbine Health Report")
    print("=" * 52)
    print(f"Total turbines analysed:                {grouped.ngroups}")
    print(f"Turbines requiring urgent maintenance:  {len(failing_ids)}")
    print("-" * 52)

    if failing_ids:
        for turbine_id in failing_ids:
            # Build a list of reasons WHY this turbine was flagged.
            # This way the output explains itself — useful for the report.
            reasons = []
            if temp_anomaly[turbine_id]:
                # :.1f formats the float to 1 decimal place (e.g. 90.6)
                reasons.append(f"avg temp {avg_temp[turbine_id]:.1f} C  (limit {MAX_SAFE_TEMP}°C)")
            if vibration_anomaly[turbine_id]:
                reasons.append(f"peak vibration {max_vibration[turbine_id]:.1f} mm/s  (limit {MAX_SAFE_VIBRATION} mm/s)")
            print(f"  {turbine_id}  ->  " + ", ".join(reasons))
    else:
        # If no turbines failed, this branch runs instead.
        print("All turbines are operating within safe limits.")

    print("=" * 52)


# ----------------------------------------------------------------------
# ENTRY POINT GUARD
# ----------------------------------------------------------------------
# This block runs main() ONLY when the file is executed directly
# (e.g. "python anomaly_detection.py" in the terminal).
#
# If another Python file imports this script, main() will NOT run
# automatically — which is what we want. This is standard Python
# practice for any script that might be both run AND imported.

if __name__ == "__main__":
    main()
