# server.py
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        message = json.loads(post_data.decode('utf-8'))

        print(f"Received message: {message['msg']} from {self.client_address[0]}")

        # Send response back to the sender
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {'msg': 'Message received successfully'}
        self.wfile.write(json.dumps(response).encode('utf-8'))

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server = server_class(('', port), handler_class)
    print(f"Starting server on port {port}")
    server.serve_forever()

if __name__ == "__main__":
    run(port=8080)