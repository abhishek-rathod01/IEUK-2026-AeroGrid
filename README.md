# AeroGrid Engineering Solutions Package — IEUK 2026
**Author:** Abhishek Rathod

Submission package for the Engineering Sector Skills Project (AeroGrid).

## Files
| File | Artefact | What it is |
|------|----------|------------|
| `anomaly_detection.py` | 1 — Data processing | Reads `telemetry_data.csv`, flags failing turbines |
| `requirements.txt` | (supports 1 & 2) | Python dependency: pandas |
| `Dockerfile` | 2 — Containerisation | Packages the script into a portable container |
| `architecture_diagram.svg` | 3 — System design | Cloud streaming architecture (submit this image) |
| `architecture_diagram.drawio` | 3 — System design | Editable source — open in draw.io to customise |
| `AeroGrid_CTO_Report.md` | 4 — Report | 300-word report to the CTO (personalise before submitting) |

## Run the script directly
```
pip install -r requirements.txt
python anomaly_detection.py
```
(Make sure `telemetry_data.csv` is in the same folder, named exactly that.)

## Run via Docker
```
docker build -t aerogrid-anomaly .
docker run --rm aerogrid-anomaly
```

## Expected result
Flags **2 turbines**:
- **T-04** — overheating (average temperature 90.6 °C)
- **T-07** — excessive vibration (peak 25.0 mm/s)
