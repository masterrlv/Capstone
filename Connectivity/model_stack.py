from flask import Flask, request, jsonify
import pickle
import pandas as pd
import os

# Ensure the model file exists locally
# Load the pre-trained model from local file
PATH = r'master_multi_class.pkl'
with open(PATH, 'rb') as file:
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
        if not input_data:
            return jsonify({"error": "No input data provided"}), 400
        
        # Ensure the input is in the correct format
        if isinstance(input_data, dict):
            input_data = [input_data]
        
        # Convert input data to a pandas DataFrame
        df = pd.DataFrame(input_data)
        if df.empty:
            return jsonify({"error": "Input data is empty"}), 400
        
        # Predict using the loaded model
        predictions = model.predict(df)
        return jsonify({"predictions": int(predictions[0])})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Run Flask locally
    app.run(host='127.0.0.1', port=5000)  # Use 127.0.0.1 to run locally