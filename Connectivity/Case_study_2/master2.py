import csv
from flask import Flask, request, jsonify
import pickle
import time
import requests  # To communicate with slave nodes

# Load the master River model
with open('F:\\Projects\\Cap_github\\Capstone\\Connectivity\\Case_study_2\\master_model.pkl', 'rb') as file:
    model = pickle.load(file)

# Slave node URLs
slave_nodes = [
    "http://localhost:5001/predict"
]

selected_features = [
    "flow_duration", "Header_Length", "Duration", "Rate", "ack_count", "syn_count",
    "fin_count", "urg_count", "HTTP", "ARP", "Min", "Max", "Tot size", "IAT", "Variance"
]

# Accuracy threshold for slaves
SLAVE_VALID_THRESHOLD = 0.8

# Map predictions to string constants
LABEL_MAPPING = {0: "DoS", 1: "Recon"}

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Master Node API is running!"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Parse input JSON
        input_data = request.get_json()
        if not input_data:
            return jsonify({"error": "No input data provided"}), 400

        # Ensure the input is in the correct format
        if isinstance(input_data, dict):
            input_data = [input_data]

        input_data = [{key: data[key] for key in selected_features if key in data} for data in input_data]
        
        # Initialize variables
        final_results = []

        # Predict using the master model
        for data in input_data:
            start_time = time.time()
            
            # Predict using master model
            master_prediction = model.predict_one(data)
            
            # If Master predicts 0, stop and log
            if master_prediction == 0:
                final_results.append({
                    "data": data,
                    "master_prediction": master_prediction,
                    "final_prediction": LABEL_MAPPING[0],
                    "slave_responses": [],
                    "prediction_time": time.time() - start_time
                })
                continue  # Move to next data point

            # Send prediction and data to slaves for further classification
            slave_responses = []
            for slave_url in slave_nodes:
                for retry in range(2):  # Retry mechanism
                    try:
                        response = requests.post(slave_url, json={"data": data, "master_prediction": master_prediction}, timeout=5)
                        if response.status_code == 200:
                            response_json = response.json()
                            if response_json.get("f1_score", 0) >= SLAVE_VALID_THRESHOLD:
                                slave_responses.append(response_json)
                                break  # Break retry loop if successful
                        else:
                            raise requests.exceptions.RequestException
                    except requests.exceptions.RequestException:
                        if retry == 1:
                            slave_responses.append({"slave_prediction": -1})  # Mark as unreachable

            # Aggregate slave responses
            valid_slaves = [res for res in slave_responses if res["slave_prediction"] != -1]

            # Determine final prediction
            if valid_slaves:
                valid_slave = valid_slaves[0]  # Use the first valid slave response
                final_prediction = valid_slave["slave_prediction"]
                final_prediction_label = LABEL_MAPPING[final_prediction]
            else:
                final_prediction = master_prediction
                final_prediction_label = LABEL_MAPPING[master_prediction]

            # Record the time after prediction
            end_time = time.time()
            prediction_time = end_time - start_time

            # Log data for CSV testing
            log_data(data, master_prediction, slave_responses, final_prediction_label, prediction_time)

            # Prepare the result
            final_results.append({
                "data": data,
                "master_prediction": master_prediction,
                "final_prediction": final_prediction_label,
                "slave_responses": slave_responses,
                "prediction_time": prediction_time
            })

        return jsonify({"results": final_results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def log_data(data, master_prediction, slave_responses, final_prediction, prediction_time):
    log_file = "master_log.csv"
    header = ["Data", "Master Prediction", "Slave Responses", "Final Prediction", "Time Taken"]
    row = [data, master_prediction, slave_responses, final_prediction, prediction_time]
    
    try:
        with open(log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            file.seek(0, 2)  # Check if file is empty
            if file.tell() == 0:
                writer.writerow(header)  # Write header if file is new
            writer.writerow(row)
    except Exception as e:
        print(f"Error logging data: {e}")

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
