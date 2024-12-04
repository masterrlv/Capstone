import pandas as pd
import time
import requests
import os

# Configuration
CSV_FILE = "/app/master_model_depl_test.csv"  # Path to your dataset
API_URL = "http://localhost:5000/predict"  # URL of your deployed model's API
CHUNK_SIZE = 100  # Number of rows to process at a time
SLEEP_INTERVAL = 10  # Time (in seconds) to wait before checking for new data
OUTPUT_FILE = "predictions_output.csv"  # File to save predictions

# Track the last processed row
if os.path.exists(OUTPUT_FILE):
    processed_rows = pd.read_csv(OUTPUT_FILE).shape[0]
else:
    processed_rows = 0

# Continuous testing loop
while True:
    # Load the dataset
    try:
        data = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print("CSV file not found. Retrying...")
        time.sleep(SLEEP_INTERVAL)
        continue

    # Check if there are new rows to process
    if processed_rows >= len(data):
        print("No new data to process. Retrying...")
        time.sleep(SLEEP_INTERVAL)
        continue

    # Get new rows
    new_data = data.iloc[processed_rows:processed_rows + CHUNK_SIZE]

    # Convert new rows to a JSON payload
    json_payload = new_data.to_dict(orient="records")

    # Send data to the API
    try:
        response = requests.post(API_URL, json=json_payload)
        response.raise_for_status()
        predictions = response.json().get("predictions", [])
    except Exception as e:
        print(f"Error sending data to the API: {e}")
        time.sleep(SLEEP_INTERVAL)
        continue

    # Save predictions
    predictions_df = pd.DataFrame({
        **new_data.reset_index(drop=True),
        "prediction": predictions
    })

    if os.path.exists(OUTPUT_FILE):
        predictions_df.to_csv(OUTPUT_FILE, mode="a", index=False, header=False)
    else:
        predictions_df.to_csv(OUTPUT_FILE, index=False)

    print(f"Processed {len(predictions)} rows.")

    # Update the processed row count
    processed_rows += len(new_data)

    # Wait before checking again
    time.sleep(SLEEP_INTERVAL)
