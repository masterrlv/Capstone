from river import metrics, linear_model, preprocessing
import pickle
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

WORKER_NODES = [
    "http://worker:5001/classify",
    "http://worker:5002/classify",
    "http://worker:5003/classify"
]


with open("master_model.pkl", "rb") as model_file:
    attack_detector = pickle.load(model_file)


accuracy_metric = metrics.Accuracy()

@app.route('/api', methods=['POST'])
def analyze_traffic():
    data = request.get_json()
    features = dict(data.get("features", {}))

    # Step 1: Predict attack presence (1 or 0)
    features_scaled = scaler.learn_one(features).transform_one(features)
    attack_prediction = attack_detector.predict_one(features_scaled)

    if attack_prediction == 0:
        return jsonify({"status": "normal", "message": "No attack detected"})

    # Step 2: Send to worker nodes for classification
    results = []
    for worker_url in WORKER_NODES:
        try:
            response = requests.post(worker_url, json=data, timeout=5)
            result = response.json()
            results.append(result)
        except requests.exceptions.RequestException:
            continue

    # Step 3: Evaluate worker results
    for result in results:
        if result.get("status") == "classified" and result.get("valid"):
            # Update master metrics with correct prediction
            attack_detector.learn_one(features_scaled, 1)  # Assume true label for now
            accuracy_metric.update(1, 1)  # Predicted correctly
            return jsonify({"status": "attack", "details": result})

    # If no valid classification found
    attack_detector.learn_one(features_scaled, 0)  # Feedback for learning
    accuracy_metric.update(1, 0)  # Incorrect prediction
    return jsonify({"status": "unknown", "message": "No valid classification"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
