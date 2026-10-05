import os
import socket
import subprocess
import sys
from pathlib import Path

host = os.environ.get("HOST", "127.0.0.1")
preferred_port = int(os.environ.get("PORT", "8001"))

for port in range(preferred_port, preferred_port + 50):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((host, port))
            chosen_port = port
            break
        except OSError:
            continue
else:
    raise RuntimeError(f"No free port available between {preferred_port} and {preferred_port + 49}.")

print(f"Starting app on http://{host}:{chosen_port}")
subprocess.run(
    [sys.executable, "-m", "uvicorn", "main:app", "--host", host, "--port", str(chosen_port), "--reload"],
    cwd=str(Path(__file__).resolve().parent),
    check=False,
)
