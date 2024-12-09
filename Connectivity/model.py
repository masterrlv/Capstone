from flask import Flask, request, jsonify
import pickle
import pandas as pd
import os
import river

# Ensure the model file exists locally
# Load the pre-trained model from local file
PATH = r'master_model.pkl'
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
        
        # Ensure the input data is valid
        if not input_data:
            return jsonify({"error": "No input data provided"}), 400
        
        # Convert input data to a pandas DataFrame
        df = pd.DataFrame(input_data)
        
        # Ensure the DataFrame is not empty
        if df.empty:
            return jsonify({"error": "Input data is empty"}), 400
        
        # Check if the input has only one row (River expects single samples)
        if len(df) != 1:
            return jsonify({"error": "Only one sample is expected"}), 400
        
        # Convert the single row to a dictionary
        sample = df.iloc[0].to_dict()
        
        # Predict using the loaded model
        prediction = model.predict_one(sample)
        
        # Return predictions as JSON
        return jsonify({"prediction": prediction})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Run Flask locally
    app.run(host='127.0.0.1', port=5000)  # Use 127.0.0.1 to run locally