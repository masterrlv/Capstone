from flask import Flask, request, jsonify
import random

app = Flask(__name__)

# Predefined attack types for demonstration
ATTACK_TYPES = ["DDoS", "Phishing", "Ransomware", "SQL Injection"]

@app.route('/classify', methods=['POST'])
def classify_attack():
    data = request.get_json()
    
    # Example: Use some logic to classify the attack (here we randomize for demo)
    features = data.get("features", [])
    if not features:
        return jsonify({"status": "error", "message": "No features provided"}), 400

    # Random attack type as placeholder
    attack_type = random.choice(ATTACK_TYPES)
    return jsonify({"attack_type": attack_type, "confidence": random.uniform(0.8, 1.0)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
