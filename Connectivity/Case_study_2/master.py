from flask import Flask, request, jsonify
import pickle
import time
import requests  # To communicate with slave nodes

# Load the master River model
with open('F:\Projects\Cap_github\Capstone\Connectivity\Case_study_2\master_model.pkl', 'rb') as file:
    model = pickle.load(file)

# Slave node URLs
slave_nodes = [
    "http://localhost:5001/predict"
]


selected_features = [
    "flow_duration", "Header_Length", "Duration", "Rate", "ack_count", "syn_count",
    "fin_count", "urg_count", "HTTP", "ARP", "Min", "Max", "Tot size", "IAT", "Variance"
]


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
            
            # Predict using master model (expects a single dictionary as input)
            master_prediction = model.predict_one(data)
            
            # Send prediction and data to slaves for further classification
            slave_responses = []
            for slave_url in slave_nodes:
                try:
                    response = requests.post(slave_url, json={"data": data, "master_prediction": master_prediction}, timeout=5)
                    if response.status_code == 200:
                        slave_responses.append(response.json())
                    else:
                        slave_responses.append({"slave_prediction": 0})  # Default if slave fails
                except requests.exceptions.RequestException:
                    slave_responses.append({"slave_prediction": 0})  # Default if slave fails

            # Aggregate slave responses
            valid_slaves = [res for res in slave_responses if res["slave_prediction"] != 0]
            
            # Determine final prediction
            if valid_slaves:
                # Update metrics only if at least one slave provides a valid prediction
                final_prediction = valid_slaves[0]["slave_prediction"]  # Use the first valid slave's prediction
                #model.learn_one(data, final_prediction)  # Update master model
            else:
                # If no valid slave predictions, fallback to master prediction
                final_prediction = master_prediction

            # Record the time after prediction
            end_time = time.time()
            prediction_time = end_time - start_time

            # Prepare the result
            final_results.append({
                "data": data,
                "master_prediction": master_prediction,
                "final_prediction": final_prediction,
                "slave_responses": slave_responses,
                "prediction_time": prediction_time
            })

        return jsonify({"results": final_results})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)
