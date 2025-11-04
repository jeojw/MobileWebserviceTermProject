import socket
import requests
import io
import json

HOST = "0.0.0.0"
PORT = 9000
DJANGO_API_URL = "http://127.0.0.1:8000/"
UPLOAD_API_URL = "http://127.0.0.1:8000/post/new/"

def handle_client(conn):
    try:
        dis = conn.makefile("rb")
        dos = conn.makefile("wb")

        cmd = conn.recv(1024).decode().strip()

        if cmd == "GET_IMAGES":
            res = requests.get(DJANGO_API_URL)
            posts = res.json()

            json_list = []
            for post in posts:
                img_path = post.get("image", "")
                print(img_path)
                if img_path:
                    img_res = requests.get(f"http://127.0.0.1:8000/{img_path}")
                    img_bytes = img_res.content
                    json_list.append({"size": len(img_bytes)})
                    conn.sendall(json.dumps(json_list[-1]).encode() + b"\n")
                    conn.sendall(img_bytes)

            conn.sendall(json.dumps(json_list).encode())

        elif cmd.startswith("UPLOAD_IMAGE"):
            filename = cmd.split(" ")[1]
            img_size_data = conn.recv(4)
            img_size = int.from_bytes(img_size_data, "big")
            img_data = conn.recv(img_size)

            files = {"image": (filename, io.BytesIO(img_data), "image/jpeg")}
            data = {"title": "Socket Upload"}
            res = requests.post(UPLOAD_API_URL, files=files, data=data)

            conn.sendall(b"Upload OK" if res.status_code in [200, 201] else b"Upload Failed")

        else:
            conn.sendall(b"Unknown Command")

    except Exception as e:
        conn.sendall(f"Error: {e}".encode())
    finally:
        conn.close()

def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(5)
        print(f"Socket server running on {HOST}:{PORT}")
        while True:
            conn, addr = s.accept()
            print(f"Connected by {addr}")
            handle_client(conn)

if __name__ == "__main__":
    start_server()
