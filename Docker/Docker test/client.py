# client.py
import requests
import json

def send_message(target_ip, target_port, message):
    url = f"http://{target_ip}:{target_port}/"
    payload = {'msg': message}
    try:
        response = requests.post(url, json=payload)
        print(f"Response from {target_ip}:{target_port}: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending message to {target_ip}:{target_port}: {e}")

if __name__ == "__main__":
    send_message('server_container', 8080, "Hello from client!")
