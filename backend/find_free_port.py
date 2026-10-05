import os
import socket

host = os.environ.get("HOST", "127.0.0.1")
preferred = int(os.environ.get("PORT", "8001"))

for port in range(preferred, preferred + 50):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            print(port)
            break
        except OSError:
            continue
else:
    print(preferred)
