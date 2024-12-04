# Use the official Python image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install required Python libraries
RUN pip install --no-cache-dir -r requirements.txt


# Copy the Python script
COPY continuous_testing.py .


# Copy the CSV file into the container
COPY master_model_depl_test.csv /app/master_model_depl_test.csv

# Expose port (if API is running in another container)
EXPOSE 5000

# Run the script when the container starts
CMD ["python", "continuous_testing.py"]
