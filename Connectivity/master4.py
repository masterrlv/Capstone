from flask import Flask, request, jsonify
import requests
import time
import csv

# Master model prediction imports (use the actual master model)
import pickle

# Load master model
with open('F:\\Projects\\Cap_github\\Capstone\\Connectivity\\Case_study_2\\master_model.pkl', 'rb') as file:
    master_model = pickle.load(file)

# Features expected by the master model
expected_features = [
    "flow_duration", "Header_Length", "Duration", "Rate", "ack_count", "syn_count",
    "fin_count", "urg_count", "HTTP", "ARP", "Min", "Max", "Tot size", "IAT", "Variance"
]

# Slave nodes configuration
SLAVE_NODES = {
    "DoS": "http://127.0.0.1:5001/predict",
    "Recon": "http://127.0.0.1:5002/predict",
}

# Flask app initialization
app = Flask(__name__)

# Logging setup
LOG_FILE = "master_slave_logs.csv"
with open(LOG_FILE, mode='w', newline='') as log_file:
    writer = csv.writer(log_file)
    writer.writerow(["Timestamp", "Incoming Data", "Master Prediction", "Slave", "Slave Prediction", 
                     "Slave Accuracy", "Final Prediction", "Processing Time"])

@app.route('/')
def home():
    return "Master Node API is running!"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Parse incoming JSON data
        input_data = request.get_json()
        if not input_data:
            return jsonify({"error": "No input data provided"}), 400

        start_time = time.time()

        # Validate and preprocess the data
        x_master = [{key: input_data[key] for key in expected_features if key in input_data}]

        # Master prediction
        master_pred = master_model.predict_one(x_master)
        if master_pred == 0:
            # If master predicts 0, no need to send to slaves
            end_time = time.time()
            log_entry = [time.ctime(), input_data, master_pred, "N/A", "N/A", "N/A", "No Action", end_time - start_time]
            with open(LOG_FILE, mode='a', newline='') as log_file:
                csv.writer(log_file).writerow(log_entry)
            return jsonify({"master_prediction": master_pred, "final_prediction": "No Action"}), 200

        # If master predicts 1, send data to slaves
        final_prediction = {}
        for attack_type, slave_url in SLAVE_NODES.items():
            try:
                response = requests.post(slave_url, json=input_data)
                if response.status_code == 200:
                    slave_response = response.json()
                    slave_pred = slave_response.get("slave_prediction")
                    slave_accuracy = slave_response.get("real_time_accuracy", "N/A")

                    # Map slave prediction to string constant
                    if slave_pred is not None:
                        mapped_prediction = attack_type if slave_pred == 1 else "No Match"
                        final_prediction[attack_type] = mapped_prediction

                    # Log each slave's response
                    log_entry = [
                        time.ctime(), input_data, master_pred, attack_type, slave_pred, 
                        slave_accuracy, mapped_prediction, time.time() - start_time
                    ]
                    with open(LOG_FILE, mode='a', newline='') as log_file:
                        csv.writer(log_file).writerow(log_entry)
                else:
                    raise Exception("Slave response error")
            except Exception as e:
                # Handle unreachable slave or failure
                log_entry = [
                    time.ctime(), input_data, master_pred, attack_type, "-1", "N/A", "Error", time.time() - start_time
                ]
                with open(LOG_FILE, mode='a', newline='') as log_file:
                    csv.writer(log_file).writerow(log_entry)
                final_prediction[attack_type] = "Error"

        end_time = time.time()
        return jsonify({
            "master_prediction": master_pred,
            "slave_predictions": final_prediction,
            "processing_time": end_time - start_time
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)