import socket
import os

HOST = ''            
PORT = 8080          

def handle_client_connection(client_connection):
    # Receive the client request data
    request_data = client_connection.recv(1024).decode('utf-8')
    print("Received request:")
    print(request_data)
    
    # Split request into lines and extract the request line ("GET /index.html HTTP/1.1")
    request_lines = request_data.splitlines()
    if not request_lines:
        client_connection.close()
        return

    request_line = request_lines[0]
    parts = request_line.split()
    if len(parts) < 2:
        client_connection.close()
        return

    method, path = parts[0], parts[1]

    # GET requests 
    if method != "GET":
        response_line = "HTTP/1.1 405 Method Not Allowed\r\n"
        response_headers = "Connection: close\r\n\r\n"
        response_body = "<html><body><h1>405 Method Not Allowed</h1></body></html>"
        response = response_line + response_headers + response_body
        client_connection.sendall(response.encode('utf-8'))
        client_connection.close()
        return

    # Default to index.html if root is requested.
    if path == "/":
        path = "/index.html"

    # Remove the leading '/' to obtain the local file path
    file_path = path.lstrip("/")

    try:
        # Try to open the requested file in binary mode
        with open(file_path, 'rb') as f:
            response_body = f.read()

        # HTTP response header for 200 OK
        response_line = "HTTP/1.1 200 OK\r\n"
        response_headers = (
            "Content-Type: text/html\r\n" +
            f"Content-Length: {len(response_body)}\r\n" +
            "Connection: close\r\n\r\n"
        )
        # Response
        response = response_line.encode('utf-8') + response_headers.encode('utf-8') + response_body

    except IOError:
        # File not found
        response_line = "HTTP/1.1 404 Not Found\r\n"
        response_body = b"<html><body><h1>404 Not Found</h1></body></html>"
        response_headers = (
            "Content-Type: text/html\r\n" +
            f"Content-Length: {len(response_body)}\r\n" +
            "Connection: close\r\n\r\n"
        )
        response = response_line.encode('utf-8') + response_headers.encode('utf-8') + response_body

    # Send the complete HTTP response back to the client
    client_connection.sendall(response)
    client_connection.close()

def run_server():
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(1)
    print(f"Serving HTTP on port {PORT}...")

    while True:
        # Accept client connections one at a time
        client_connection, client_address = server_socket.accept()
        handle_client_connection(client_connection)

if __name__ == "__main__":
    run_server()
