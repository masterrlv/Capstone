from flask import Flask, request, jsonify
import pickle
from river import metrics, drift
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import time

# Load the slave's pre-trained model
with open('F:\\Projects\\Cap_github\\Capstone\\Connectivity\\Case_study_2\\DOR_Node.pkl', 'rb') as file:
    slave_model = pickle.load(file)

# Initialize real-time metrics
metric = metrics.Accuracy()
yt = []  # True labels
yp = []  # Predicted labels
i = 0  # Counter for the number of samples processed
t = []  # Tracking samples processed
m = []  # Tracking real-time accuracy

# Initialize drift detector
eddm = drift.binary.EDDM()

# Features expected by the slave model
expected_features = [
    "flow_duration", "Header_Length", "Duration", "Rate", "ack_count", "syn_count",
    "fin_count", "urg_count", "HTTP", "ARP", "Min", "Max", "Tot size", "IAT", "Variance"
]

# Flask app initialization
app = Flask(__name__)

@app.route('/')
def home():
    return "Slave Node API is running!"

@app.route('/predict', methods=['POST'])
def predict():
    global i, yt, yp, t, m
    
    try:
        # Parse incoming JSON data
        input_data = request.get_json()
        if not input_data or "data" not in input_data:
            return jsonify({"error": "Invalid input data"}), 400
        
        data = input_data["data"]
        y_true = input_data.get("label")  # True label (optional, provided for accuracy tracking)
        
        # Validate and preprocess the data
        x = {key: data[key] for key in expected_features if key in data}

        # Make a prediction
        start_time = time.time()
        y_pred = slave_model.predict_one(x)
        slave_model.learn_one(x, y_true)  # Learn from the sample
        end_time = time.time()
        prediction_time = end_time - start_time

        # Update metrics if true label is available
        if y_true is not None:
            metric.update(y_true, y_pred)
            yt.append(y_true)
            yp.append(y_pred)
            t.append(i)
            m.append(metric.get() * 100)
            i += 1

        # Drift detection
        if y_true is not None and y_pred != y_true:
            eddm.update(y_true)
            if eddm.drift_detected:
                print(f"Change detected at sample {i}, input value: {y_true}")
            if eddm.warning_detected:
                print(f"Warning detected at sample {i}")

        # Respond with metrics and prediction
        response = {
            "slave_prediction": y_pred,
            "real_time_accuracy": metric.get() * 100 if y_true is not None else "N/A",
            "f1_score": round(f1_score(yt, yp), 4) * 100 if yt else "N/A",
            "accuracy": round(accuracy_score(yt, yp), 4) * 100 if yt else "N/A",
            "prediction_time": prediction_time
        }
        return jsonify(response)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5001)
