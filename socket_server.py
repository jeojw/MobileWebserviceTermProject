import socket
from datetime import datetime
import os
import re

HOST = "0.0.0.0"
PORT = 9000
REQUEST_DIR = "./request"
os.makedirs(REQUEST_DIR, exist_ok=True)

def save_request(data):
    timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"{REQUEST_DIR}/{timestamp}.bin"
    with open(filename, "wb") as f:
        f.write(data)
    print(f"[+] Saved request to {filename}")
    return filename

def validate_protocol(request_text):
    lines = request_text.splitlines()
    if not lines:
        return "400 Bad Request (empty request)"

    request_line = lines[0].strip()
    pattern = r"^(GET|POST|PUT|DELETE|HEAD|OPTIONS) [^\s]+ HTTP/1\.[01]$"
    if not re.match(pattern, request_line):
        return f"400 Bad Request (invalid request line: {request_line})"

    headers = "\n".join(lines[1:])
    required_headers = ["Host", "User-Agent", "Accept-Encoding"]
    for header in required_headers:
        if not re.search(rf"^{header}:", headers, re.MULTILINE | re.IGNORECASE):
            return f"400 Missing required header: {header}"

    return "200 OK (Protocol Valid)"

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen(5)
        print(f"[*] Socket Server running on {HOST}:{PORT}")

        while True:
            conn, addr = server.accept()
            print(f"[+] Connection from {addr}")

            data = b""
            conn.settimeout(2.0)
            try:
                while True:
                    chunk = conn.recv(4096)
                    if not chunk:
                        break
                    data += chunk
            except socket.timeout:
                pass

            if not data:
                conn.close()
                continue

            save_request(data)

            request_text = data.decode(errors="ignore")
            result = validate_protocol(request_text)
            print(f"[Protocol Check] {result}")

            status_code = result.split(" ")[0]
            reason = "OK" if status_code == "200" else "Bad Request"
            response = f"HTTP/1.1 {status_code} {reason}\r\nContent-Length: 0\r\n\r\n"
            conn.sendall(response.encode())
            conn.close()

if __name__ == "__main__":
    start_server()
