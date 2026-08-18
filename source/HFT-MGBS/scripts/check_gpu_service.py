from __future__ import annotations

import argparse
import json
import socket


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="10.0.5.103")
    parser.add_argument("--port", type=int, default=50051)
    parser.add_argument("--timeout", type=float, default=2.0)
    args = parser.parse_args()
    request = json.dumps({"op": "health"}).encode("utf-8") + b"\n"
    with socket.create_connection(
        (args.host, args.port), timeout=args.timeout
    ) as connection:
        connection.settimeout(args.timeout)
        connection.sendall(request)
        response = b""
        while not response.endswith(b"\n"):
            chunk = connection.recv(65536)
            if not chunk:
                break
            response += chunk
    payload = json.loads(response.decode("utf-8"))
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if payload.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

