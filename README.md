# IEUK 2026 — AeroGrid Turbine Anomaly Detection

**Author:** Abhisheksinh Vanrajsinh Rathod  
**Course:** BSc Computer Science with AI & Placement Year — London South Bank University (Year 1 → 2)  
**Event:** IEUK 2026 Engineering Sector Skills Project (Bright Network)  
**Submitted:** 18 June 2026  

---

## What this project is

This is my submission for the IEUK 2026 Engineering track, built for a fictional client called **AeroGrid** — a wind farm operator whose legacy monitoring system couldn't keep up with the volume of telemetry data coming from 10 turbines, and whose engineering team kept missing early warning signs of failure.

The brief gave me 5,000 rows of real-time telemetry (temperature, vibration, RPM, timestamps) and asked me to:

1. Detect which turbines were operating outside safe limits
2. Containerise the solution so it runs anywhere
3. Design a cloud architecture that scales to handle this data in real time
4. Write a report explaining the findings and recommendations to the CTO

---

## What I found

Running the anomaly detection script on the full dataset:

| Turbine | Issue | Value | Limit |
|---------|-------|-------|-------|
| **T-04** | Overheating | Avg temp **90.6°C** | 85°C |
| **T-07** | Excessive vibration | Peak **25.0 mm/s** | 15 mm/s |

The other 8 turbines are healthy (~65°C average, vibration peaks ~12 mm/s).

**T-04** likely has a bearing friction or cooling system failure — sustained high heat degrades seals and will cause structural failure.  
**T-07** shows sustained high vibration (not a one-off spike), pointing to blade imbalance or rotor misalignment — a metal fatigue risk.

---

## Files in this repo

| File | What it is |
|------|------------|
| `anomaly_detection.py` | Artefact 1 — Python data processing script |
| `requirements.txt` | Python dependency (pandas, pinned version) |
| `Dockerfile` | Artefact 2 — containerises the script for portable deployment |
| `architecture_diagram.svg` | Artefact 3 — cloud streaming architecture diagram |
| `architecture_diagram.drawio` | Artefact 3 — editable source (open in draw.io) |
| `AeroGrid_CTO_Report.docx` | Artefact 4 — engineering report to the CTO |
| `telemetry_data.csv` | The raw telemetry dataset provided in the brief |
| `IEUK_SUBMISSION_HANDOFF.md` | Session notes and study plan |

---

## How to run the script

```bash
pip install -r requirements.txt
python anomaly_detection.py
```

Make sure `telemetry_data.csv` is in the same folder. Expected output:

```
====================================================
AeroGrid Turbine Health Report
====================================================
Total turbines analysed:                10
Turbines requiring urgent maintenance:  2
----------------------------------------------------
  T-04  ->  avg temp 90.6 C  (limit 85.0°C)
  T-07  ->  peak vibration 25.0 mm/s  (limit 15.0 mm/s)
====================================================
```

---

## How to run via Docker

```bash
docker build -t aerogrid-anomaly .
docker run --rm aerogrid-anomaly
```

---

## Key design decision

The brief uses two different phrasings deliberately:
- *"Average temperature exceeds 85°C"* → I use `.mean()` — a sustained problem
- *"Vibration spikes above 15 mm/s"* → I use `.max()` — a peak/spike is a worst-case, not an average

Using the same calculation for both would have been wrong. This distinction matters in a real engineering system — you want to catch both chronic problems (sustained heat) and acute ones (single dangerous vibration event).

---

## Cloud architecture summary

The proposed real-time pipeline (see `architecture_diagram.svg`):

```
IoT Sensors → Kafka/Kinesis (ingestion) → AWS Lambda (anomaly detection)
                                                    ↓              ↓              ↓
                                               SNS Alerts    Timestream DB    S3 Data Lake
                                             (engineers)    (hot/live data)  (cold archive)
```

This solves AeroGrid's two problems:
1. **Server overload** → Kafka buffers the high-volume stream, decoupling ingestion from processing
2. **Missed warnings** → Lambda flags anomalies in real time and fires instant alerts

---

## Tech stack

Python · pandas · Docker · AWS Lambda · Apache Kafka / AWS Kinesis · Amazon Timestream · Amazon S3 · Amazon SNS · draw.io

---

## About me

I'm a first-year CS student at LSBU specialising in AI and Data Engineering. This project was built under deadline pressure (overnight, between night shifts) which I think is pretty representative of real engineering work. I understand every line of the code and can explain all the design decisions — that was a condition I set myself before submitting.

Connect with me: [LinkedIn](https://linkedin.com/in/abhisheksinh-rathod) | [GitHub](https://github.com/abhishek-rathod01)
