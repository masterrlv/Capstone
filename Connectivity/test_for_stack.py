import pandas as pd
import time
import requests
import os

# Configuration for local testing
CSV_FILE = r"master_model_depl_test.csv"  # Path to your dataset
API_URL = "http://127.0.0.1:5000/predict"  # Local Flask server URL
CHUNK_SIZE = 100  # Number of rows to process at a time
SLEEP_INTERVAL = 10  # Time (in seconds) to wait before checking for new data
OUTPUT_FILE = "predictions_output_stack.csv"  # File to save predictions

# Features to include in the JSON request
SELECTED_FEATURES = ['IAT', 'Tot sum', 'Tot size', 'Max', 'Header_Length', 'AVG', 'Magnitue', 
                    'Min', 'rst_count', 'Protocol Type', 'flow_duration', 'Std', 'Radius', 
                    'Variance', 'urg_count', 'Covariance', 'syn_count', 'Number', 'Weight']
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
        print(f"CSV file {CSV_FILE} not found. Retrying...")
        time.sleep(SLEEP_INTERVAL)
        continue

    # Check if there are new rows to process
    if processed_rows >= len(data):
        print("No new data to process. Retrying...")
        time.sleep(SLEEP_INTERVAL)
        continue

    # Get new rows
    new_data = data.iloc[processed_rows:processed_rows + CHUNK_SIZE]
    
    # Select only the required features
    missing_features = [feature for feature in SELECTED_FEATURES if feature not in new_data.columns]
    if missing_features:
        print(f"Error: Missing required features in the dataset: {missing_features}")
        break

    filtered_data = new_data[SELECTED_FEATURES]

    # Convert filtered rows to a JSON payload
    json_payload = filtered_data.to_dict(orient="records")

    predictions = []  # List to store predictions
    try:
        # Send data to the API row by row
        for sample in json_payload:
            payload = [sample]  # Wrap each sample in a list
            print(f"Sending payload: {payload}")  # Debug: Log the payload
            response = requests.post(API_URL, json=payload)
            response.raise_for_status()  # Raise an error for non-200 status codes
            prediction = response.json().get("predictions", None)
            if prediction is not None:
                predictions.append(prediction)
            else:
                print(f"Warning: Missing prediction for sample: {sample}")
    except Exception as e:
        print(f"Error sending data to the API: {e}")
        time.sleep(SLEEP_INTERVAL)
        continue

    # Save predictions
    predictions_df = filtered_data.copy()
    predictions_df["predictions"] = predictions
    predictions_df["predictions"] = predictions_df["predictions"].astype(int)

    if os.path.exists(OUTPUT_FILE):
        predictions_df.to_csv(OUTPUT_FILE, mode="a", index=False, header=False)
    else:
        predictions_df.to_csv(OUTPUT_FILE, index=False)

    print(f"Processed {len(predictions)} rows.")

    # Update the processed row count
    processed_rows += len(new_data)

    # Wait before checking again
    time.sleep(SLEEP_INTERVAL)
