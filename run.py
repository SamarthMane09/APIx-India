"""
APIx-India Application Entrypoint Runner
Parses host/port flags and launches the FastAPI server.
"""

import sys
import uvicorn

if __name__ == "__main__":
    port = 3000
    host = "0.0.0.0"

    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
            i += 2
            continue
        elif arg.startswith("--port="):
            port = int(arg.split("=")[1])
        elif arg == "--host" and i + 1 < len(sys.argv):
            host = sys.argv[i + 1]
            i += 2
            continue
        elif arg.startswith("--host="):
            host = arg.split("=")[1]
        i += 1

    print(f"Starting APIx-India FastAPI server on {host}:{port}...")
    uvicorn.run("main:app", host=host, port=port, reload=False)
