# Dockerfile
FROM python:3.12.7-alpine

# Set the working directory
WORKDIR /app

# Copy the Python script into the container
COPY server_run.py /app/
COPY client.py /app/

# Install dependencies
RUN pip install requests

# Set the default command for servers
CMD ["python3", "server_run.py"]