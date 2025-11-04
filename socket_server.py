import socket
import requests
import io
import json
import struct

HOST = "0.0.0.0"
PORT = 9000
DJANGO_API_URL = "http://127.0.0.1:8000/api_root/post"
UPLOAD_API_URL = "http://127.0.0.1:8000/post/new/"

def handle_client(conn):
    try:
        dis = conn.makefile("rb")
        dos = conn.makefile("wb")

        cmd = conn.recv(1024).decode().strip()

        if cmd == "GET_IMAGES":
            print("성공")
            res = requests.get(DJANGO_API_URL)
            print(res)
            posts = res.json()

            json_list = []
            image_data_list = []
            for post in posts:
                img_path = post.get("image", "")
                if img_path:
                    if not img_path.startswith("http"):
                        img_path = f"http://127.0.0.1:8000/{img_path.lstrip('/')}"
                    img_res = requests.get(img_path)
                    img_bytes = img_res.content
                    json_list.append({"size": len(img_bytes)})
                    image_data_list.append(img_bytes)

            json_str = json.dumps(json_list)
            json_bytes = json_str.encode("utf-8")
            conn.send(struct.pack(">H", len(json_bytes)))
            conn.send(json_bytes)

            for img_bytes in image_data_list:
                conn.sendall(img_bytes)

            print("[+] Sent all images successfully")

            print("[+] Sent all images successfully")

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
        print(f"[!] Server internal error: {e}")
        try:
            conn.sendall(f"Error: {e}".encode())
        except OSError:
            pass
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
