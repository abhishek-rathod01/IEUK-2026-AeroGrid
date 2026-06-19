# ---------------------------------------------------------------------------
# Dockerfile  -  AeroGrid Turbine Anomaly Detection
# IEUK 2026 Engineering Sector Skills Project - Artefact 2
#
# A Dockerfile is a recipe that packages our script + Python + its dependencies
# into one portable "container". Anyone can then run the analysis with a single
# command, on any machine, with zero setup. That solves "it works on my machine".
# ---------------------------------------------------------------------------

# 1. Start from a small, official Python image.
#    "slim" keeps the image lightweight, so it builds and ships faster.
FROM python:3.12-slim

# 2. Set the working folder inside the container where our app will live.
WORKDIR /app

# 3. Copy ONLY the requirements file first, then install the dependencies.
#    Doing this before copying our code lets Docker cache this layer, so future
#    rebuilds are much faster when only the script (not the dependencies) changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the analysis script and the telemetry data into the image.
COPY anomaly_detection.py .
COPY telemetry_data.csv .

# 5. The command that runs automatically when the container starts.
CMD ["python", "anomaly_detection.py"]

# ---------------------------------------------------------------------------
# HOW TO BUILD AND RUN
#   docker build -t aerogrid-anomaly .
#   docker run --rm aerogrid-anomaly
#
# Note: for this task we copy the CSV into the image so the container is fully
# self-contained. In a real streaming system the data would arrive live from
# the pipeline (Kafka/Kinesis) instead of being baked into the image.
# ---------------------------------------------------------------------------
