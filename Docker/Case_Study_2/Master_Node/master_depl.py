from flask import Flask, request, jsonify
import pickle
import pandas as pd
import time

with open('master_model.pkl', 'rb') as file:
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
        start_time = time.time()

        # Predict using the loaded model
        predictions = model.predict(df)

        # Record the time after prediction
        end_time = time.time()
        
        # Calculate time taken for prediction
        prediction_time = end_time - start_time
        print(prediction_time)

        # Return predictions and the time it took to predict
        result = [{"prediction": int(predictions[i]), "prediction_time": prediction_time} for i in range(len(predictions))]

        return jsonify({"predictions": result})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
