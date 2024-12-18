# Use the official Python image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy the application code and model
COPY master_depl.py master_depl.py
COPY master_multi_class.pkl master_multi_class.pkl

# Expose the port Flask will run on
EXPOSE 5000

# Run the Flask application
CMD ["python", "master_depl.py"]