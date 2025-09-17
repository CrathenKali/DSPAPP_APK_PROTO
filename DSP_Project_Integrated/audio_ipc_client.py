#!/usr/bin/env python3
import socket, json, sys
def send_cmd(obj, host="127.0.0.1", port=52000):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    payload = json.dumps(obj).encode('utf-8')
    s.sendto(payload, (host, port))
    # try to read ack
    s.settimeout(2.0)
    try:
        data, addr = s.recvfrom(1024)
        print("Ack:", data.decode())
    except Exception as e:
        print("No ack:", e)
    s.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: audio_ipc_client.py cmd_json_string")
        print('Example: python audio_ipc_client.py \'{"cmd":"eq","band":5,"value":2.5}\'')
        sys.exit(1)
    raw = sys.argv[1]
    try:
        obj = json.loads(raw)
    except:
        print("Invalid JSON")
        sys.exit(1)
    send_cmd(obj)
