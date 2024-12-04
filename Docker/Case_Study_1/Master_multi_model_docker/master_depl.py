from flask import Flask, request, jsonify
import pickle
import numpy as np
import pandas as pd

with open('master_multi_class.pkl', 'rb') as file:
    model = pickle.load(file)

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def home():
    return "Stacking Model API is running!"

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Parse input JSON
        input_data = request.get_json()
        # Convert input data to a pandas DataFrame
        df = pd.DataFrame(input_data)
        # Predict using the loaded model
        predictions = model.predict(df)
        # Return predictions as JSON
        return jsonify({"predictions": predictions.tolist()})
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
