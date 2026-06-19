"""
AeroGrid Turbine Anomaly Detection
==================================
IEUK 2026 Engineering Sector Skills Project - Artefact 1
Author: Abhishek Rathod

WHAT THIS SCRIPT DOES
---------------------
1. Reads turbine telemetry readings from a CSV file.
2. Groups the readings by turbine, then for each turbine calculates:
      - the AVERAGE temperature  (the rule talks about "Average Temperature")
      - the MAXIMUM vibration    (the rule says vibration "spikes" above a limit,
                                  and a spike is a peak, so we check the max reading)
3. Flags any turbine that breaks EITHER anomaly rule:
      - Average temperature  > 85.0 C    OR
      - Maximum vibration    > 15.0 mm/s
4. Prints a clear list of the failing Turbine IDs, with the reason for each.

HOW TO RUN
----------
1. Make sure Python 3 and pandas are installed:
       pip install pandas
2. Put this file in the SAME folder as telemetry_data.csv
3. Open a terminal in that folder and run:
       python anomaly_detection.py
"""

import pandas as pd   # pandas: the industry-standard library for handling CSV / table data


# ----------------------------------------------------------------------
# CONFIG  -  change these if your CSV uses different names
# ----------------------------------------------------------------------
CSV_FILE = "telemetry_data.csv"   # the data file provided by AeroGrid

# The exact column headings inside the CSV.
# If the script can't find one of these, it prints the columns it DID find,
# so you can correct the names below in one place.
COL_TURBINE_ID  = "turbine_id"
COL_TEMPERATURE = "temperature_c"
COL_VIBRATION   = "vibration_mm_s"

# The anomaly thresholds, taken straight from the brief.
MAX_SAFE_TEMP      = 85.0   # degrees C  - flag if the AVERAGE temp is above this
MAX_SAFE_VIBRATION = 15.0   # mm/s       - flag if a vibration SPIKE goes above this


def main():
    # ------------------------------------------------------------------
    # STEP 1: Read the CSV into a pandas DataFrame (a table held in memory)
    # ------------------------------------------------------------------
    # If the file is missing, show a clear message instead of crashing.
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print(f"ERROR: could not find '{CSV_FILE}'.")
        print("Make sure the CSV is in the same folder as this script, and that")
        print("its name matches CSV_FILE in the CONFIG section above.")
        return

    # Tidy the column names: strip any accidental spaces around them.
    df.columns = df.columns.str.strip()

    # ------------------------------------------------------------------
    # STEP 2: Safety check - make sure the columns we need actually exist
    # ------------------------------------------------------------------
    required = [COL_TURBINE_ID, COL_TEMPERATURE, COL_VIBRATION]
    missing = [col for col in required if col not in df.columns]
    if missing:
        print("ERROR: these expected columns were not found:", missing)
        print("The CSV actually contains these columns:", list(df.columns))
        print("Open the script and fix the COL_* names in the CONFIG section.")
        return   # stop here - no point continuing with the wrong columns

    # ------------------------------------------------------------------
    # STEP 3: Group all readings by turbine, then calculate the two metrics
    # ------------------------------------------------------------------
    # groupby() gathers every row belonging to the same turbine together.
    grouped = df.groupby(COL_TURBINE_ID)

    avg_temp      = grouped[COL_TEMPERATURE].mean()  # average temperature per turbine
    max_vibration = grouped[COL_VIBRATION].max()     # worst (peak) vibration per turbine

    # ------------------------------------------------------------------
    # STEP 4: Apply the anomaly rules
    # ------------------------------------------------------------------
    # A turbine fails if EITHER condition is true.  In pandas, | means OR.
    temp_anomaly      = avg_temp > MAX_SAFE_TEMP
    vibration_anomaly = max_vibration > MAX_SAFE_VIBRATION
    failing           = temp_anomaly | vibration_anomaly

    # .index gives us the Turbine IDs; keep only the ones marked True.
    failing_ids = failing[failing].index.tolist()

    # ------------------------------------------------------------------
    # STEP 5: Report the results
    # ------------------------------------------------------------------
    print("=" * 52)
    print("AeroGrid Turbine Health Report")
    print("=" * 52)
    print(f"Total turbines analysed:                {grouped.ngroups}")
    print(f"Turbines requiring urgent maintenance:  {len(failing_ids)}")
    print("-" * 52)

    if failing_ids:
        for turbine_id in failing_ids:
            # Show WHY each turbine was flagged - this feeds straight into the report.
            reasons = []
            if temp_anomaly[turbine_id]:
                reasons.append(f"avg temp {avg_temp[turbine_id]:.1f} C")
            if vibration_anomaly[turbine_id]:
                reasons.append(f"peak vibration {max_vibration[turbine_id]:.1f} mm/s")
            print(f"  {turbine_id}  ->  " + ", ".join(reasons))
    else:
        print("All turbines are operating within safe limits.")

    print("=" * 52)


# Only run main() when this file is executed directly (good Python practice).
if __name__ == "__main__":
    main()
