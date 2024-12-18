# Use the official Python image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY continuous_testing.py .
COPY master_model_depl_test.csv /app/master_model_depl_test.csv

# Expose port (if API is running in another container)
EXPOSE 5000

# Run the script when the container starts
CMD ["python", "continuous_testing.py"]