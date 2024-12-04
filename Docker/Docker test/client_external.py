import requests
import json
import sys

def send_message(target_ip, target_port, message):
    url = f"http://{target_ip}:{target_port}/"
    payload = {'msg': message}
    try:
        response = requests.post(url, json=payload)
        print(f"Response from {target_ip}:{target_port}: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to {target_ip}:{target_port}: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python client.py <server_ip> <server_port>")
        sys.exit(1)

    server_ip = 'localhost'
    server_port = 8080
    send_message(server_ip, server_port, "Hello from VS Code!")