from flask import Flask, request, jsonify
import pickle
import time

# Load the slave model (River model)
with open('F:\Projects\Cap_github\Capstone\Connectivity\Case_study_2\DOR_Node.pkl', 'rb') as file:
    model = pickle.load(file)

# Selected features for the slave model
selected_features = ["IAT","Variance","Duration","syn_count","fin_count","rst_count",
    "Tot_sum","Protocol_Type","Rate","Min","flow_duration","Header_Length","HTTP",
    "Number","urg_count","ack_count","Covariance","Tot_size","Magnitue"
]

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Slave Node API is running!"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Parse input JSON
        input_data = request.get_json()
        if not input_data:
            return jsonify({"error": "No input data provided"}), 400

        data = input_data.get("data")
        master_prediction = input_data.get("master_prediction")

        if not data:
            return jsonify({"error": "No data provided"}), 400

        # Filter input data to only include selected features
        filtered_data = {key: data[key] for key in selected_features if key in data}

        # Start timing
        start_time = time.time()

        # Predict using the slave model
        slave_prediction = model.predict_one(filtered_data)

        # If the model cannot classify, return 0
        if slave_prediction == 0:
            return jsonify({"slave_prediction": 0})

        # If classification is valid, update the slave model
        #model.learn_one(filtered_data, slave_prediction)

        # Stop timing
        end_time = time.time()
        prediction_time = end_time - start_time

        # Return the slave's prediction and time taken
        return jsonify({
            "slave_prediction": slave_prediction,
            "prediction_time": prediction_time
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001)
